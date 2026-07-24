// ─── Settings Page ────────────────────────────────────────────────────────────
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { clearHistory } from '../api';

function Toggle({ id, checked, onChange }) {
  return (
    <label className="toggle-switch" htmlFor={id}>
      <input id={id} type="checkbox" checked={checked} onChange={onChange} />
      <span className="toggle-slider" />
    </label>
  );
}

function Section({ title, children }) {
  return (
    <div className="glass-card" style={{ marginBottom: 16 }}>
      <h3 className="text-muted" style={{ fontSize: 12, fontWeight: 700, letterSpacing: 1, marginBottom: 16 }}>
        {title}
      </h3>
      {children}
    </div>
  );
}

function Row({ label, desc, right }) {
  return (
    <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', padding:'10px 0', borderBottom:'1px solid var(--glass-border)' }}>
      <div>
        <div style={{ fontWeight: 500, fontSize: 14 }}>{label}</div>
        {desc && <div className="text-muted" style={{ fontSize: 12, marginTop: 2 }}>{desc}</div>}
      </div>
      {right}
    </div>
  );
}

export default function SettingsPage() {
  const { user, logout, updateUser } = useAuth();
  const navigate = useNavigate();

  const [prefs, setPrefs] = useState(() => {
    const stored = localStorage.getItem('ss_prefs');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        document.body.classList.toggle('light-mode', !parsed.darkMode);
        return parsed;
      } catch {}
    }
    return {
      darkMode:       true,
      notifications:  true,
      autoScan:       false,
      saveHistory:    true,
      highQuality:    false,
      betaFeatures:   false,
    };
  });

  const [editing, setEditing] = useState(false);
  const [newName, setNewName] = useState(user?.displayName || '');
  const [clearing, setClearing] = useState(false);

  const toggle = (key) => {
    setPrefs((p) => {
      const next = { ...p, [key]: !p[key] };
      if (key === 'darkMode') {
        document.body.classList.toggle('light-mode', !next.darkMode);
      }
      localStorage.setItem('ss_prefs', JSON.stringify(next));
      return next;
    });
  };

  const handleLogout = () => { logout(); navigate('/auth'); };

  const handleClearHistory = async () => {
    if (window.confirm("Are you sure you want to permanently clear all scan history?")) {
      setClearing(true);
      try {
        await clearHistory();
        alert("Scan history cleared successfully!");
      } catch (err) {
        alert("Failed to clear history on backend. Cleared locally.");
      } finally {
        setClearing(false);
      }
    }
  };

  const MODELS = [
    { name: 'EfficientNet-B4', purpose: 'Image Deepfake', acc: '95%', color: '#00D4FF' },
    { name: 'CNN Temporal',    purpose: 'Video Analysis',  acc: '92%', color: '#8B5CF6' },
    { name: 'Mel-CNN',        purpose: 'Audio Detection', acc: '88%', color: '#06FFA5' },
    { name: 'DistilBERT',     purpose: 'Text Scam NLP',   acc: '94%', color: '#FF3CAC' },
  ];

  return (
    <div>
      <div className="page-header">
        <h1>⚙️ Settings</h1>
        <p>Manage your preferences and account</p>
      </div>

      <div className="section" style={{ maxWidth: 680 }}>
        {/* Profile */}
        <div className="glass-card" style={{ display:'flex', alignItems:'center', gap:16, marginBottom:16 }}>
          <div style={{ width:56, height:56, borderRadius:'50%', background:'linear-gradient(135deg, rgba(0,212,255,0.3), rgba(139,92,246,0.3))', border:'2px solid rgba(0,212,255,0.4)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:24, flexShrink:0 }}>
            👤
          </div>
          <div style={{ flex:1, minWidth:0 }}>
            {editing ? (
              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <input
                  type="text"
                  className="input-field"
                  style={{ height: 32, fontSize: 14, padding: '0 8px', maxWidth: 160 }}
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                />
                <button
                  className="btn-neon"
                  style={{ height: 32, padding: '0 12px', fontSize: 12 }}
                  onClick={async () => {
                    await updateUser({ displayName: newName });
                    setEditing(false);
                  }}
                >
                  Save
                </button>
                <button
                  className="btn-neon btn-outline"
                  style={{ height: 32, padding: '0 12px', fontSize: 12 }}
                  onClick={() => { setEditing(false); setNewName(user?.displayName || ''); }}
                >
                  Cancel
                </button>
              </div>
            ) : (
              <>
                <div style={{ fontWeight:700, fontSize:16 }}>{user?.displayName || 'Shield User'}</div>
                <div className="text-muted" style={{ fontSize:13, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{user?.email}</div>
                <div style={{ marginTop:4 }}>
                  <span style={{ fontSize:11, background:'rgba(0,212,255,0.15)', border:'1px solid rgba(0,212,255,0.3)', color:'var(--neon-blue)', padding:'2px 10px', borderRadius:20, fontWeight:600 }}>
                    Pro Plan
                  </span>
                </div>
              </>
            )}
          </div>
          {!editing && (
            <button
              className="btn-neon btn-outline"
              style={{ height:36, padding:'0 16px', fontSize:13, flexShrink:0 }}
              onClick={() => { setEditing(true); setNewName(user?.displayName || ''); }}
            >
              Edit
            </button>
          )}
        </div>

        {/* Preferences */}
        <Section title="Preferences">
          <Row label="Dark Mode" desc="Always-on dark interface" right={<Toggle id="dark-mode" checked={prefs.darkMode} onChange={() => toggle('darkMode')} />} />
          <Row label="Notifications" desc="Scan completion alerts" right={<Toggle id="notifications" checked={prefs.notifications} onChange={() => toggle('notifications')} />} />
          <Row label="Auto-Scan Clipboard" desc="Automatically scan copied URLs" right={<Toggle id="auto-scan" checked={prefs.autoScan} onChange={() => toggle('autoScan')} />} />
          <Row label="Save History" desc="Keep a record of all scans" right={<Toggle id="save-history" checked={prefs.saveHistory} onChange={() => toggle('saveHistory')} />} />
        </Section>

        {/* Advanced */}
        <Section title="Advanced">
          <Row label="High-Quality Processing" desc="Slower but more accurate scans" right={<Toggle id="high-quality" checked={prefs.highQuality} onChange={() => toggle('highQuality')} />} />
          <Row label="Beta Features" desc="Enable experimental AI models" right={<Toggle id="beta" checked={prefs.betaFeatures} onChange={() => toggle('betaFeatures')} />} />
          <Row
            label="Backend URL"
            desc={import.meta.env.VITE_API_URL || 'http://localhost:8000'}
            right={<span style={{ fontSize:12, color:'var(--neon-cyan)' }}>●&nbsp;Connected</span>}
          />
        </Section>

        {/* AI Models */}
        <Section title="AI Models">
          <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
            {MODELS.map(({ name, purpose, acc, color }) => (
              <div key={name} style={{ display:'flex', justifyContent:'space-between', alignItems:'center', padding:'10px 14px', background:`${color}08`, border:`1px solid ${color}20`, borderRadius:'var(--r-md)' }}>
                <div>
                  <div style={{ fontWeight:600, fontSize:14 }}>{name}</div>
                  <div className="text-muted" style={{ fontSize:12 }}>{purpose}</div>
                </div>
                <div style={{ textAlign:'right' }}>
                  <div style={{ color, fontWeight:700, fontSize:15 }}>{acc}</div>
                  <div className="text-muted" style={{ fontSize:11 }}>accuracy</div>
                </div>
              </div>
            ))}
          </div>
        </Section>

        {/* About */}
        <Section title="About">
          <Row label="Version" right={<span style={{ color:'rgba(255,255,255,0.4)', fontSize:13 }}>1.0.0</span>} />
          <Row label="License" right={<span style={{ color:'rgba(255,255,255,0.4)', fontSize:13 }}>MIT</span>} />
          <Row label="GitHub" right={<a href="https://github.com" target="_blank" rel="noreferrer" style={{ color:'var(--neon-blue)', fontSize:13, textDecoration:'none', fontWeight:600 }}>View Source ↗</a>} />
        </Section>

        {/* Danger */}
        <div className="glass-card" style={{ border:'1px solid rgba(255,59,59,0.2)' }}>
          <h3 style={{ fontSize:12, fontWeight:700, color:'var(--risk-high)', letterSpacing:1, marginBottom:16 }}>
            Danger Zone
          </h3>
          <div style={{ display:'flex', gap:12, flexWrap:'wrap' }}>
            <button
              className="btn-neon"
              style={{ background:'rgba(255,59,59,0.12)', color:'var(--risk-high)', border:'1px solid rgba(255,59,59,0.3)', boxShadow:'none', height:40, fontSize:13 }}
              onClick={handleClearHistory}
              disabled={clearing}
            >
              {clearing ? 'Clearing…' : '🗑️ Clear History'}
            </button>
            <button id="logout-btn" className="btn-neon" style={{ background:'rgba(255,59,59,0.12)', color:'var(--risk-high)', border:'1px solid rgba(255,59,59,0.3)', boxShadow:'none', height:40, fontSize:13 }} onClick={handleLogout}>
              🚪 Sign Out
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
