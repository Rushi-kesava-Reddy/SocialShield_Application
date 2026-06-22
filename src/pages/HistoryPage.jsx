// ─── History Page ─────────────────────────────────────────────────────────────
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getHistory, deleteScan } from '../api';

const FILTERS = ['ALL', 'IMAGE', 'VIDEO', 'AUDIO', 'TEXT', 'URL', 'PROFILE'];
const ICONS = { IMAGE:'🖼️', VIDEO:'🎬', AUDIO:'🎙️', TEXT:'📝', URL:'🔗', PROFILE:'👤' };

const DEMO_SCANS = Array.from({ length: 8 }, (_, i) => ({
  scanId: `demo_${i}`,
  mediaType: ['IMAGE','VIDEO','AUDIO','TEXT','URL','PROFILE'][i % 6],
  verdict: ['FAKE','REAL','SUSPICIOUS','REAL','FAKE','REAL','SUSPICIOUS','REAL'][i],
  confidence: parseFloat((70 + Math.random() * 28).toFixed(1)),
  timestamp: new Date(Date.now() - i * 86400000 * 1.5).toISOString(),
}));

function VerdictBadge({ verdict }) {
  const map = { FAKE:['verdict-fake','🔴 FAKE'], SUSPICIOUS:['verdict-suspicious','⚠️ SUSP.'], REAL:['verdict-real','✅ REAL'] };
  const [cls, label] = map[verdict?.toUpperCase()] || map.REAL;
  return <span className={`verdict-badge ${cls}`}>{label}</span>;
}

export default function HistoryPage() {
  const navigate = useNavigate();
  const [filter, setFilter] = useState('ALL');
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = (type) => {
    setLoading(true);
    getHistory(type === 'ALL' ? null : type)
      .then((r) => setScans(r.data?.items || []))
      .catch(() => setScans(type === 'ALL' ? DEMO_SCANS : DEMO_SCANS.filter((s) => s.mediaType === type)))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(filter); }, [filter]);

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    try { await deleteScan(id); } catch {}
    setScans((prev) => prev.filter((s) => s.scanId !== id));
  };

  return (
    <div>
      <div className="page-header">
        <h1>Scan History</h1>
        <p>Your complete scan activity log</p>
      </div>

      {/* Filter chips */}
      <div className="section" style={{ paddingBottom: 0 }}>
        <div style={{ display:'flex', gap:8, flexWrap:'wrap', marginBottom:20 }}>
          {FILTERS.map((f) => (
            <button key={f} id={`filter-${f.toLowerCase()}`} className={`chip ${filter===f?'active':''}`} onClick={() => setFilter(f)}>
              {f === 'ALL' ? '🌐 All' : `${ICONS[f]} ${f}`}
            </button>
          ))}
        </div>
      </div>

      <div className="section">
        {loading ? (
          <div style={{ display:'flex', justifyContent:'center', padding:48 }}><div className="spinner" style={{ width:36, height:36 }} /></div>
        ) : scans.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🔍</div>
            <h3 style={{ color:'rgba(255,255,255,0.5)', fontSize:16, marginBottom:6 }}>No scans found</h3>
            <p style={{ fontSize:13 }}>Start scanning to see your results here</p>
            <button className="btn-neon" style={{ marginTop:20 }} onClick={() => navigate('/home')}>Start Scanning</button>
          </div>
        ) : (
          <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
            {scans.map((scan) => (
              <div key={scan.scanId} className="history-item" onClick={() => navigate(`/result/${scan.scanId}`)}>
                <div className="history-icon-box" style={{ background:'rgba(0,212,255,0.08)', color:'var(--neon-blue)' }}>
                  {ICONS[scan.mediaType] || '🛡️'}
                </div>
                <div style={{ flex:1, minWidth:0 }}>
                  <div style={{ fontWeight:600, fontSize:14 }}>{scan.mediaType} Scan</div>
                  <div style={{ fontSize:12, color:'rgba(255,255,255,0.4)', marginTop:2 }}>
                    {new Date(scan.timestamp).toLocaleString()}
                  </div>
                </div>
                <div style={{ display:'flex', alignItems:'center', gap:12, flexShrink:0 }}>
                  <VerdictBadge verdict={scan.verdict} />
                  <span style={{ color:'rgba(255,255,255,0.4)', fontSize:13 }}>{scan.confidence?.toFixed(0)}%</span>
                  <button
                    onClick={(e) => handleDelete(scan.scanId, e)}
                    style={{ background:'none', border:'none', cursor:'pointer', color:'rgba(255,255,255,0.25)', fontSize:18, padding:4 }}
                    title="Delete"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
