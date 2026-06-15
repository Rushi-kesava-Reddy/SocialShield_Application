// ─── Home Page ────────────────────────────────────────────────────────────────
import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { getUserStats, getHistory } from '../api';

const SCAN_TYPES = [
  { type: 'image',   icon: '🖼️',  label: 'Scan Image',   sub: 'Detect AI-generated faces',        color: '#00D4FF', bg: 'rgba(0,212,255,0.12)'   },
  { type: 'video',   icon: '🎬',  label: 'Scan Video',   sub: 'Frame-by-frame deepfake analysis', color: '#8B5CF6', bg: 'rgba(139,92,246,0.12)'  },
  { type: 'audio',   icon: '🎙️', label: 'Scan Audio',   sub: 'Voice clone detection',            color: '#06FFA5', bg: 'rgba(6,255,165,0.12)'   },
  { type: 'text',    icon: '📝',  label: 'Scan Text',    sub: 'Scam & phishing message check',   color: '#FF3CAC', bg: 'rgba(255,60,172,0.12)'  },
  { type: 'url',     icon: '🔗',  label: 'Scan URL',     sub: 'Safe Browsing & VirusTotal',       color: '#FFB800', bg: 'rgba(255,184,0,0.12)'   },
  { type: 'profile', icon: '👤',  label: 'Scan Profile', sub: 'Fake account detection',           color: '#00E5FF', bg: 'rgba(0,229,255,0.12)'   },
];

function VerdictBadge({ verdict }) {
  const map = { FAKE: ['verdict-fake','🔴 FAKE'], SUSPICIOUS: ['verdict-suspicious','⚠️ SUSPICIOUS'], REAL: ['verdict-real','✅ REAL'] };
  const [cls, label] = map[verdict?.toUpperCase()] || map.REAL;
  return <span className={`verdict-badge ${cls}`}>{label}</span>;
}

export default function HomePage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({ totalScans: 0, fakeDetected: 0, suspiciousDetected: 0, trustScore: 100 });
  const [recent, setRecent] = useState([]);
  const [statsLoading, setStatsLoading] = useState(true);

  useEffect(() => {
    // Try API, fall back to demo data
    getUserStats()
      .then((r) => setStats(r.data))
      .catch(() => setStats({ totalScans: 42, fakeDetected: 7, suspiciousDetected: 5, trustScore: 83 }))
      .finally(() => setStatsLoading(false));

    getHistory()
      .then((r) => setRecent(r.data?.items?.slice(0, 4) || []))
      .catch(() => setRecent([
        { scanId: '1', mediaType: 'IMAGE', verdict: 'FAKE',       confidence: 94.2, timestamp: new Date().toISOString() },
        { scanId: '2', mediaType: 'URL',   verdict: 'SUSPICIOUS',  confidence: 78.5, timestamp: new Date().toISOString() },
        { scanId: '3', mediaType: 'TEXT',  verdict: 'REAL',        confidence: 89.1, timestamp: new Date().toISOString() },
      ]));
  }, []);

  const scoreColor = stats.trustScore >= 80 ? '#06FFA5' : stats.trustScore >= 50 ? '#FFB800' : '#FF3B3B';
  const greetName = user?.displayName || user?.email?.split('@')[0] || 'Shield User';

  return (
    <div style={{ paddingBottom: 40 }}>
      {/* ── Page Header ── */}
      <div className="page-header" style={{ background: 'linear-gradient(180deg, rgba(0,212,255,0.06) 0%, transparent 100%)', padding: '28px 28px 24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <p style={{ color: 'rgba(255,255,255,0.45)', fontSize: 13, marginBottom: 4 }}>Welcome back</p>
            <h1 style={{ fontFamily: 'var(--font-display)', fontSize: 28, fontWeight: 800 }}>{greetName}</h1>
          </div>

          {/* Trust Score */}
          <div className="trust-score-card" style={{ minWidth: 220 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <p style={{ color: 'rgba(255,255,255,0.45)', fontSize: 11, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 4 }}>AI Trust Score</p>
                <div className="trust-score-value" style={{ color: scoreColor }}>
                  {statsLoading ? '—' : stats.trustScore}
                  <span style={{ fontSize: 18, color: 'rgba(255,255,255,0.4)', fontWeight: 400 }}>/100</span>
                </div>
                <p style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', marginTop: 4 }}>
                  {stats.trustScore >= 80 ? 'Excellent protection' : stats.trustScore >= 50 ? 'Moderate risk' : 'High threat exposure'}
                </p>
              </div>
              <div style={{ fontSize: 40, opacity: 0.3 }}>🛡️</div>
            </div>
          </div>
        </div>

        {/* Quick stats */}
        <div className="grid-3" style={{ marginTop: 20, gridTemplateColumns: 'repeat(3,1fr)' }}>
          {[
            { label: 'Total Scans', value: stats.totalScans, color: '#00D4FF' },
            { label: 'Fake Detected', value: stats.fakeDetected, color: '#FF3B3B' },
            { label: 'Suspicious', value: stats.suspiciousDetected, color: '#FFB800' },
          ].map(({ label, value, color }) => (
            <div key={label} className="stat-card">
              <div className="stat-value" style={{ color }}>{statsLoading ? '—' : value}</div>
              <div className="stat-label">{label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Scan Types ── */}
      <div className="section">
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 16 }}>Scan &amp; Detect</h2>
        <div className="scan-grid" style={{ padding: 0 }}>
          {SCAN_TYPES.map(({ type, icon, label, sub, color, bg }) => (
            <div
              key={type}
              id={`scan-${type}`}
              className="scan-type-card"
              onClick={() => navigate(`/scan/${type}`)}
              style={{ borderColor: `${color}22` }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = `${color}55`;
                e.currentTarget.style.boxShadow = `0 0 24px ${color}20`;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = `${color}22`;
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              <div className="scan-type-icon" style={{ background: bg, color }}>
                {icon}
              </div>
              <h3>{label}</h3>
              <p>{sub}</p>
              <div style={{ marginTop: 12, color, fontSize: 12, fontWeight: 600 }}>Tap to scan →</div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Recent Scans ── */}
      {recent.length > 0 && (
        <div className="section">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h2 style={{ fontSize: 18, fontWeight: 700 }}>Recent Scans</h2>
            <Link to="/history" style={{ color: 'var(--neon-blue)', fontSize: 13, fontWeight: 600, textDecoration: 'none' }}>View All →</Link>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {recent.map((scan) => (
              <div
                key={scan.scanId}
                className="history-item"
                onClick={() => navigate(`/result/${scan.scanId}`)}
              >
                <div className="history-icon-box" style={{ background: 'rgba(0,212,255,0.1)', color: 'var(--neon-blue)', fontSize: 20 }}>
                  {{ IMAGE:'🖼️', VIDEO:'🎬', AUDIO:'🎙️', TEXT:'📝', URL:'🔗' }[scan.mediaType] || '🛡️'}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>{scan.mediaType} Scan</div>
                  <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', marginTop: 2 }}>
                    {new Date(scan.timestamp).toLocaleString()}
                  </div>
                </div>
                <VerdictBadge verdict={scan.verdict} />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
