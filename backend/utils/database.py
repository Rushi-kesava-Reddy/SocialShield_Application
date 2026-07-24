"""Firestore database utilities with persistent JSON fallback for dev/demo mode"""
import os
import json
import logging
import firebase_admin
from firebase_admin import firestore

logger = logging.getLogger(__name__)
_db = None
_mock_db_instance = None
_last_db_error = None


class MockDocument:
    def __init__(self, doc_id, data):
        self.id = doc_id
        self._data = data
        self.exists = True

    def to_dict(self):
        return self._data


class MockCollectionReference:
    def __init__(self, name, parent_doc_path=None):
        self.name = name
        self.parent_doc_path = parent_doc_path
        self._docs = {}

    def document(self, doc_id):
        if doc_id not in self._docs:
            self._docs[doc_id] = MockDocumentReference(doc_id, self)
        return self._docs[doc_id]

    def stream(self):
        return [MockDocument(doc_id, doc_ref._data) for doc_id, doc_ref in self._docs.items() if doc_ref._exists]

    def order_by(self, field, direction="DESCENDING"):
        return self

    def limit(self, count):
        return self

    def offset(self, count):
        return self


class MockDocumentReference:
    def __init__(self, doc_id, collection_ref):
        self.id = doc_id
        self.collection_ref = collection_ref
        self._data = {}
        self._exists = False
        self._subcollections = {}

    @property
    def reference(self):
        return self

    def get(self, transaction=None):
        class Snap:
            def __init__(self, doc_ref):
                self.exists = doc_ref._exists
                self._data = doc_ref._data
            def to_dict(self):
                return self._data
        return Snap(self)

    def set(self, data, merge=False):
        if merge and self._exists:
            self._data.update(data)
        else:
            self._data = data.copy()
        self._exists = True
        self._save_to_disk()

    def update(self, data):
        self._data.update(data)
        self._exists = True
        self._save_to_disk()

    def delete(self):
        self._exists = False
        self._data = {}
        self._save_to_disk()

    def collection(self, name):
        if name not in self._subcollections:
            self._subcollections[name] = MockCollectionReference(name, f"{self.collection_ref.name}/{self.id}")
        return self._subcollections[name]

    def _save_to_disk(self):
        global _mock_db_instance
        if _mock_db_instance:
            _mock_db_instance.save_state()


class MockFirestoreClient:
    def __init__(self, filepath="db_store.json"):
        self.filepath = filepath
        self.collections = {}
        self.load_state()

    def collection(self, name):
        if name not in self.collections:
            self.collections[name] = MockCollectionReference(name)
        return self.collections[name]

    def document(self, path):
        parts = path.strip("/").split("/")
        ref = self
        for i, part in enumerate(parts):
            if i % 2 == 0:
                ref = ref.collection(part)
            else:
                ref = ref.document(part)
        return ref

    def transaction(self):
        class MockTransaction:
            def set(self, ref, data, merge=False):
                ref.set(data, merge)
            def get(self, ref):
                return ref.get()
        return MockTransaction()

    def save_state(self):
        state = {}
        for col_name, col in self.collections.items():
            state[col_name] = {}
            for doc_id, doc in col._docs.items():
                if doc._exists:
                    state[col_name][doc_id] = {
                        "data": doc._data,
                        "subcollections": {}
                    }
                    for sub_name, sub in doc._subcollections.items():
                        state[col_name][doc_id]["subcollections"][sub_name] = {}
                        for sdoc_id, sdoc in sub._docs.items():
                            if sdoc._exists:
                                state[col_name][doc_id]["subcollections"][sub_name][sdoc_id] = sdoc._data
        try:
            with open(self.filepath, "w") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save mock db state: {e}")

    def load_state(self):
        if not os.path.exists(self.filepath):
            return
        try:
            with open(self.filepath, "r") as f:
                state = json.load(f)
            for col_name, col_data in state.items():
                col = self.collection(col_name)
                for doc_id, doc_info in col_data.items():
                    doc = col.document(doc_id)
                    doc._data = doc_info["data"]
                    doc._exists = True
                    for sub_name, sub_data in doc_info.get("subcollections", {}).items():
                        sub = doc.collection(sub_name)
                        for sdoc_id, sdoc_val in sub_data.items():
                            sdoc = sub.document(sdoc_id)
                            sdoc._data = sdoc_val
                            sdoc._exists = True
        except Exception as e:
            logger.error(f"Failed to load mock db state: {e}")


async def init_db():
    global _db
    try:
        from utils.auth import init_firebase
        init_firebase()
        _db = firestore.client()
        logger.info("Firestore connected")
    except Exception as e:
        logger.warning(f"Firestore not available: {e}. Running with persistent JSON database fallback.")


def get_db():
    global _mock_db_instance
    if _db is not None:
        return _db
    if _mock_db_instance is None:
        _mock_db_instance = MockFirestoreClient()
    return _mock_db_instance


async def save_scan_result_and_update_stats(user_id: str, scan_id: str, result: dict):
    """Save scan result to subcollection and transactionally update user stats"""
    try:
        db = get_db()
        
        # Extract string values from Enums if present
        media_type = result.get("media_type")
        if hasattr(media_type, "value"):
            media_type = media_type.value
        elif hasattr(media_type, "name"):
            media_type = media_type.name
            
        verdict = result.get("verdict")
        if hasattr(verdict, "value"):
            verdict = verdict.value
        elif hasattr(verdict, "name"):
            verdict = verdict.name
            
        # Map snake_case to camelCase for Android and shared database compatibility
        result_camel = {
            "scanId": str(result.get("scan_id") or scan_id),
            "userId": str(result.get("user_id") or user_id),
            "mediaType": str(media_type or "IMAGE"),
            "verdict": str(verdict or "SAFE"),
            "confidence": float(result.get("confidence") or 100.0),
            "fakeProbability": float(result.get("fake_probability") or 0.0),
            "realProbability": float(result.get("real_probability") or 100.0),
            "riskLevel": str(result.get("risk_level") or "LOW"),
            "explanations": [str(e) for e in (result.get("explanations") or [])],
            "recommendations": [str(r) for r in (result.get("recommendations") or [])],
            "heatmapBase64": result.get("heatmap_base64"),
            "metadata": result.get("metadata"),
            "timestamp": str(result.get("timestamp"))
        }
        
        # 1. Save scan to subcollection
        scan_ref = db.collection("users").document(user_id).collection("scans").document(scan_id)
        scan_ref.set(result_camel)
        
        # 2. Update user stats document transactionally
        user_ref = db.collection("users").document(user_id)
        
        @firestore.transactional
        def update_stats_transaction(transaction, user_reference):
            snapshot = user_reference.get(transaction=transaction)
            
            total_scans = 0
            fake_detected = 0
            suspicious_detected = 0
            safe_detected = 0
            
            if snapshot.exists:
                user_data = snapshot.to_dict()
                total_scans = user_data.get("totalScans", 0) or 0
                fake_detected = user_data.get("fakeDetected", 0) or 0
                suspicious_detected = user_data.get("suspiciousDetected", 0) or 0
                safe_detected = user_data.get("safeDetected", 0) or 0
                
            verdict = result_camel.get("verdict", "SAFE").upper()
            total_scans += 1
            if verdict in ("SAFE", "REAL"):
                safe_detected += 1
            elif verdict == "SUSPICIOUS":
                suspicious_detected += 1
            elif verdict == "FAKE":
                fake_detected += 1
                
            trust_score = 100
            if total_scans > 0:
                trust_score = int(((safe_detected + 0.5 * suspicious_detected) / total_scans) * 100)
                
            transaction.set(user_reference, {
                "totalScans": total_scans,
                "fakeDetected": fake_detected,
                "suspiciousDetected": suspicious_detected,
                "safeDetected": safe_detected,
                "trustScore": trust_score
            }, merge=True)
            
        transaction = db.transaction()
        update_stats_transaction(transaction, user_ref)
        logger.info(f"Scan {scan_id} saved and stats updated successfully for user {user_id}")
        
    except Exception as e:
        global _last_db_error
        _last_db_error = str(e)
        logger.error(f"Failed to save scan result or update stats: {e}")
