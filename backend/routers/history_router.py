"""History Router - Fetch user scan history from Firestore subcollections"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
import logging

from utils.auth import get_current_user
from utils.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


def map_to_snake_case(data: dict) -> dict:
    """Helper to convert camelCase Firestore keys to snake_case for Pydantic/Frontend compatibility"""
    if not data:
        return data
    mapped = {}
    key_mapping = {
        "scanId": "scan_id",
        "userId": "user_id",
        "mediaType": "media_type",
        "verdict": "verdict",
        "confidence": "confidence",
        "fakeProbability": "fake_probability",
        "realProbability": "real_probability",
        "riskLevel": "risk_level",
        "explanations": "explanations",
        "recommendations": "recommendations",
        "heatmapBase64": "heatmap_base64",
        "metadata": "metadata",
        "timestamp": "timestamp"
    }
    for k, v in data.items():
        mapped_key = key_mapping.get(k, k)
        mapped[mapped_key] = v
    return mapped


@router.get("/history")
async def get_history(
    user_id: str = Depends(get_current_user),
    media_type: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get paginated scan history for current user from their subcollection"""
    try:
        db = get_db()
        query = db.collection("users").document(user_id).collection("scans")
        
        # In Firestore, we order by timestamp. If filtering by mediaType, we need an index.
        # Fall back to manual filter if indexing isn't fully set up yet.
        docs = query.order_by("timestamp", direction="DESCENDING").limit(limit + offset).stream()
        
        results = []
        for doc in docs:
            data = doc.to_dict()
            data = map_to_snake_case(data)
            data['id'] = doc.id
            
            # Apply media type filter manually to avoid requiring custom composite indexes
            if media_type and data.get("media_type") != media_type.upper():
                continue
                
            # Remove large fields for list view
            data.pop('heatmap_base64', None)
            results.append(data)
            
        # Apply offset manually
        paginated_results = results[offset:offset + limit]
        
        return {"items": paginated_results, "count": len(results), "offset": offset}
    
    except Exception as e:
        logger.error(f"History fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch history")


@router.get("/history/{scan_id}")
async def get_scan_detail(
    scan_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get full details for a specific scan"""
    try:
        db = get_db()
        doc_ref = db.collection("users").document(user_id).collection("scans").document(scan_id)
        doc = doc_ref.get()
        
        if doc.exists:
            return map_to_snake_case(doc.to_dict())
            
        # Fallback to searching by field if document ID does not match
        docs = db.collection("users").document(user_id).collection("scans").where("scanId", "==", scan_id).limit(1).stream()
        for d in docs:
            return map_to_snake_case(d.to_dict())
            
        raise HTTPException(status_code=404, detail="Scan not found")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scan detail error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch scan")


@router.delete("/history/{scan_id}")
async def delete_scan(
    scan_id: str,
    user_id: str = Depends(get_current_user)
):
    """Delete a scan record"""
    try:
        db = get_db()
        doc_ref = db.collection("users").document(user_id).collection("scans").document(scan_id)
        doc = doc_ref.get()
        
        if doc.exists:
            doc_ref.delete()
            return {"message": "Scan deleted successfully"}
            
        # Fallback to search
        docs = list(db.collection("users").document(user_id).collection("scans").where("scanId", "==", scan_id).limit(1).stream())
        if not docs:
            raise HTTPException(status_code=404, detail="Scan not found")
            
        docs[0].reference.delete()
        return {"message": "Scan deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete scan: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete scan")


@router.delete("")
async def clear_history(user_id: str = Depends(get_current_user)):
    """Delete all scan history records for the current user"""
    try:
        db = get_db()
        docs = list(db.collection("users").document(user_id).collection("scans").stream())
        for doc in docs:
            doc.reference.delete()
        return {"message": "All scan history cleared successfully", "count": len(docs)}
    except Exception as e:
        logger.error(f"Clear history error: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear scan history")


@router.get("/stats")
async def get_user_stats(user_id: str = Depends(get_current_user)):
    """Get aggregated stats for dashboard trust score"""
    try:
        db = get_db()
        docs = list(db.collection("users").document(user_id).collection("scans").stream())
        
        total = len(docs)
        fake_count = sum(1 for d in docs if str(d.to_dict().get('verdict')).upper() == 'FAKE')
        suspicious = sum(1 for d in docs if str(d.to_dict().get('verdict')).upper() == 'SUSPICIOUS')
        safe_count = sum(1 for d in docs if str(d.to_dict().get('verdict')).upper() == 'SAFE')
        
        trust_score = 100
        if total > 0:
            threat_rate = (fake_count + suspicious * 0.5) / total
            trust_score = max(0, int(100 - threat_rate * 100))
        
        # Self-healing: Update the main users stats document with correct calculated values
        try:
            db.collection("users").document(user_id).set({
                "totalScans": total,
                "fakeDetected": fake_count,
                "suspiciousDetected": suspicious,
                "safeDetected": safe_count,
                "trustScore": trust_score
            }, merge=True)
        except Exception as db_err:
            logger.error(f"Self-healing stats update failed: {db_err}")
            
        return {
            "total_scans": total,
            "fake_detected": fake_count,
            "suspicious_detected": suspicious,
            "safe_detected": safe_count,
            "trust_score": trust_score
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return {"total_scans": 0, "fake_detected": 0, "suspicious_detected": 0, "safe_detected": 0, "trust_score": 100}
