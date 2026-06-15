// ─── Layout Component — with Backend Status Indicator ────────────────────────
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';

const NAV = [
  { to: '/home',     icon: '🏠', label: 'Home'      },
  { to: '/history',  icon: '🕐', label: 'History'   },
  { to: '/map',      icon: '🗺️', label: 'Fraud Map'  },
  { to: '/settings', icon: '⚙️', label: 'Settings'  },
];

function BackendDot({ online }) {
  const color   = online === null ? '#FFB800' : online ? '#06FFA5' : '#FF3B3B';
  const label   = online === null ? 'Checking…' : online ? 'Backend Online' : 'Backend Offline (Demo)';
  return (
    <div title={label} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '6px 10px', borderRadius: 8, background: `${color}12`, border: `1px solid ${color}30` }}>
      <span style={{ width: 8, height: 8, borderRadius: '50%', background: color, display: 'inline-block', boxShadow: `0 0 6px ${color}` }} />
      <span style={{ fontSize: 11, color: color, fontWeight: 600, whiteSpace: 'nowrap' }}>{label}</span>
    </div>
  );
}

export default function Layout() {
  const { user, logout, backendOnline } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => { await logout(); navigate('/auth'); };

  return (
    <div className="app-layout">
      {/* ── Desktop Sidebar ── */}
      <aside className="sidebar">
        {/* Logo */}
        <div className="sidebar-logo">
          <div className="logo-icon">🛡️</div>
          <span>SocialShield</span>
        </div>

        {/* Navigation */}
        <nav className="sidebar-nav">
          {NAV.map(({ to, icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
            >
              <span className="nav-icon">{icon}</span>
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: 10, paddingTop: 16 }}>
          {/* Backend status */}
          <BackendDot online={backendOnline} />

          {/* User info */}
          <div style={{ padding: '12px', borderRadius: '12px', background: 'var(--glass-white)', border: '1px solid var(--glass-border)' }}>
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', marginBottom: 3 }}>Signed in as</div>
            <div style={{ fontSize: 13, fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {user?.displayName || user?.email || 'User'}
            </div>
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', marginTop: 1 }}>
              {user?.email}
            </div>
          </div>

          {/* Sign out */}
          <button
            id="sidebar-signout"
            className="btn-neon btn-outline"
            style={{ width: '100%', height: 40, fontSize: 13 }}
            onClick={handleLogout}
          >
            🚪 Sign Out
          </button>
        </div>
      </aside>

      {/* ── Main Content ── */}
      <div className="main-content">
        {/* Top status bar (mobile only shows backend status) */}
        <div className="topbar" style={{ justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
              <span>🛡️</span>
              <span style={{ display: 'none' }} className="mobile-brand">SocialShield</span>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <BackendDot online={backendOnline} />
            <div style={{ width: 34, height: 34, borderRadius: '50%', background: 'linear-gradient(135deg, rgba(0,212,255,0.3), rgba(139,92,246,0.2))', border: '1px solid rgba(0,212,255,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16, cursor: 'pointer' }} onClick={() => navigate('/settings')}>
              👤
            </div>
          </div>
        </div>

        <Outlet />
      </div>

      {/* ── Mobile Bottom Nav ── */}
      <nav className="mobile-nav">
        <div className="mobile-nav-items">
          {NAV.map(({ to, icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) => `mobile-nav-item${isActive ? ' active' : ''}`}
            >
              <span className="mobile-nav-icon">{icon}</span>
              {label}
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  );
}
