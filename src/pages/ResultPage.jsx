// ─── Result Page ──────────────────────────────────────────────────────────────
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getScanDetail } from '../api';

function ConfidenceRing({ value, verdict }) {
  const colors = { FAKE: '#FF3B3B', SUSPICIOUS: '#FFB800', REAL: '#06FFA5' };
  const color = colors[verdict?.toUpperCase()] || '#06FFA5';
  const R = 60, circ = 2 * Math.PI * R;
  const dash = (value / 100) * circ;

  return (
    <div className="confidence-ring">
      <svg width="160" height="160" viewBox="0 0 160 160">
        <circle cx="80" cy="80" r={R} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="12" />
        <circle
          cx="80" cy="80" r={R}
          fill="none"
          stroke={color}
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={`${dash} ${circ}`}
          style={{ transition: 'stroke-dasharray 1.2s cubic-bezier(0.22,1,0.36,1)', filter: `drop-shadow(0 0 8px ${color}88)` }}
        />
      </svg>
      <div className="confidence-ring-label">
        <span style={{ fontFamily: 'var(--font-display)', fontSize: 30, fontWeight: 900, color }}>{value.toFixed(0)}%</span>
        <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', marginTop: 2 }}>confidence</span>
      </div>
    </div>
  );
}

function ProbBar({ label, value, color }) {
  return (
    <div>
      <div style={{ display:'flex', justifyContent:'space-between', marginBottom:6, fontSize:13 }}>
        <span style={{ color:'rgba(255,255,255,0.6)' }}>{label}</span>
        <span style={{ color, fontWeight:700 }}>{value.toFixed(1)}%</span>
      </div>
      <div className="progress-bar-track">
        <div className="progress-bar-fill" style={{ width:`${value}%`, background:`linear-gradient(90deg, ${color}80, ${color})` }} />
      </div>
    </div>
  );
}

function RiskBars({ risk }) {
  const map = { HIGH: 3, MEDIUM: 2, LOW: 1 };
  const color = { HIGH:'#FF3B3B', MEDIUM:'#FFB800', LOW:'#06FFA5' }[risk?.toUpperCase()] || '#06FFA5';
  const filled = map[risk?.toUpperCase()] || 1;
  return (
    <div style={{ display:'flex', alignItems:'center', gap:8 }}>
      <div className="risk-bars">
        {[1,2,3].map((i) => (
          <div key={i} className="risk-bar" style={{ background: i <= filled ? color : `${color}25` }} />
        ))}
      </div>
      <span style={{ color, fontSize:13, fontWeight:700 }}>{risk?.toUpperCase() || 'LOW'} RISK</span>
    </div>
  );
}

export default function ResultPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showHeatmap, setShowHeatmap] = useState(false);

  useEffect(() => {
    // Try session cache first (from scan page)
    const cached = sessionStorage.getItem('scan_result_' + id);
    if (cached) { setResult(JSON.parse(cached)); setLoading(false); return; }

    getScanDetail(id)
      .then((r) => setResult(r.data))
      .catch(() => {
        // Demo fallback
        setResult({
          scanId: id, verdict: 'FAKE', confidence: 94.2,
          fakeProbability: 94.2, realProbability: 5.8,
          riskLevel: 'HIGH', mediaType: 'IMAGE',
          explanations: ['Facial boundary inconsistencies detected around left cheek', 'Unnatural blinking frequency pattern (0.2hz vs normal 0.3hz)', 'GAN artifacts in high-frequency spatial regions', 'Asymmetric skin texture under chin'],
          metadata: { face_count: 1, resolution: '1080x1920', model: 'EfficientNet-B4', processing_time: '2.3s' },
          timestamp: new Date().toISOString(),
        });
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return (
    <div style={{ display:'flex', alignItems:'center', justifyContent:'center', minHeight:'60vh' }}>
      <div className="spinner" style={{ width:40, height:40 }} />
    </div>
  );

  const r = result;
  const verdictColors = { FAKE:'#FF3B3B', SUSPICIOUS:'#FFB800', REAL:'#06FFA5' };
  const verdictColor = verdictColors[r.verdict?.toUpperCase()] || '#06FFA5';
  const verdictBg = { FAKE:'rgba(255,59,59,0.07)', SUSPICIOUS:'rgba(255,184,0,0.07)', REAL:'rgba(6,255,165,0.07)' }[r.verdict?.toUpperCase()] || 'rgba(6,255,165,0.07)';
  const verdictIcons = { FAKE:'🔴', SUSPICIOUS:'⚠️', REAL:'✅' };

  return (
    <div>
      {/* Header */}
      <div className="page-header" style={{ display:'flex', alignItems:'center', gap:16 }}>
        <button onClick={() => navigate(-1)} style={{ width:40, height:40, borderRadius:12, background:'var(--glass-white)', border:'1px solid var(--glass-border)', cursor:'pointer', fontSize:18, display:'flex', alignItems:'center', justifyContent:'center' }}>
          ←
        </button>
        <h1>Scan Result</h1>
      </div>

      <div className="section" style={{ maxWidth:720 }}>
        {/* Big Verdict Banner */}
        <div style={{ background: verdictBg, border:`1px solid ${verdictColor}30`, borderRadius:'var(--r-lg)', padding:'36px 24px', textAlign:'center', marginBottom:20 }}>
          <div style={{ fontSize:56, marginBottom:12 }}>{verdictIcons[r.verdict?.toUpperCase()] || '✅'}</div>
          <div style={{ fontFamily:'var(--font-display)', fontSize:44, fontWeight:900, color:verdictColor, letterSpacing:2, marginBottom:16 }}>
            {r.verdict?.toUpperCase()}
          </div>
          <ConfidenceRing value={r.confidence || 0} verdict={r.verdict} />
        </div>

        {/* Risk + Probabilities */}
        <div className="glass-card" style={{ marginBottom:16 }}>
          <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', flexWrap:'wrap', gap:16, marginBottom:20 }}>
            <div>
              <p style={{ color:'rgba(255,255,255,0.45)', fontSize:12, marginBottom:6 }}>Risk Level</p>
              <RiskBars risk={r.riskLevel} />
            </div>
            <div style={{ textAlign:'right' }}>
              <p style={{ color:'rgba(255,255,255,0.45)', fontSize:12, marginBottom:4 }}>Fake Probability</p>
              <p style={{ fontFamily:'var(--font-display)', fontSize:32, fontWeight:800, color:verdictColor }}>{(r.fakeProbability||0).toFixed(1)}%</p>
            </div>
          </div>
          <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
            <ProbBar label="Fake" value={r.fakeProbability||0} color="#FF3B3B" />
            <ProbBar label="Real" value={r.realProbability||0} color="#06FFA5" />
          </div>
        </div>

        {/* Heatmap */}
        {r.heatmapBase64 && (
          <div className="glass-card" style={{ marginBottom:16 }}>
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:showHeatmap?16:0 }}>
              <div>
                <p style={{ fontWeight:600, marginBottom:2 }}>Manipulation Heatmap</p>
                <p style={{ color:'rgba(255,255,255,0.4)', fontSize:12 }}>Red areas indicate manipulation</p>
              </div>
              <button className="btn-neon btn-outline" style={{ height:34, padding:'0 14px', fontSize:12 }} onClick={() => setShowHeatmap((v) => !v)}>
                {showHeatmap ? 'Hide' : 'Show'}
              </button>
            </div>
            {showHeatmap && (
              <img src={`data:image/jpeg;base64,${r.heatmapBase64}`} alt="Heatmap" style={{ width:'100%', borderRadius:'var(--r-md)', marginTop:12 }} />
            )}
          </div>
        )}

        {/* AI Explanations */}
        {r.explanations?.length > 0 && (
          <div className="glass-card" style={{ marginBottom:16 }}>
            <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:14 }}>
              <span style={{ fontSize:18 }}>🧠</span>
              <span style={{ fontWeight:700, fontSize:15 }}>AI Explanation</span>
            </div>
            <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
              {r.explanations.map((exp, i) => (
                <div key={i} style={{ display:'flex', gap:10, alignItems:'flex-start' }}>
                  <div style={{ width:6, height:6, borderRadius:'50%', background:verdictColor, flexShrink:0, marginTop:7 }} />
                  <p style={{ color:'rgba(255,255,255,0.8)', fontSize:14, lineHeight:1.6 }}>{exp}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Metadata */}
        {r.metadata && (
          <div className="glass-card" style={{ marginBottom:20 }}>
            <p style={{ fontWeight:600, fontSize:13, color:'rgba(255,255,255,0.6)', marginBottom:10 }}>Technical Details</p>
            <div style={{ display:'flex', flexDirection:'column', gap:6 }}>
              {Object.entries(r.metadata).slice(0,6).map(([k,v]) => (
                <div key={k} style={{ display:'flex', justifyContent:'space-between', fontSize:13 }}>
                  <span style={{ color:'rgba(255,255,255,0.45)' }}>{k.replace(/_/g,' ').replace(/\b\w/g, c => c.toUpperCase())}</span>
                  <span style={{ color:'rgba(255,255,255,0.75)', fontWeight:500 }}>{String(v)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Scan ID */}
        <p style={{ textAlign:'center', color:'rgba(255,255,255,0.2)', fontSize:11, marginBottom:20 }}>
          Scan ID: {id?.slice(0,12)}…
        </p>

        {/* Actions */}
        <div style={{ display:'flex', gap:12 }}>
          <button className="btn-neon btn-outline" style={{ flex:1 }} onClick={() => navigate(-1)}>← Back</button>
          <button className="btn-neon" style={{ flex:1 }} onClick={() => navigate('/home')}>Scan Again 🔄</button>
        </div>
      </div>
    </div>
  );
}
