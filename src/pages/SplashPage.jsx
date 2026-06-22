// ─── Splash Page ─────────────────────────────────────────────────────────────
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';

export default function SplashPage() {
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    const onboarded = localStorage.getItem('ss_onboarded');
    const timer = setTimeout(() => {
      if (user) navigate('/home');
      else if (onboarded) navigate('/auth');
      else navigate('/onboarding');
    }, 2200);
    return () => clearTimeout(timer);
  }, [navigate, user]);

  return (
    <div className="splash-page">
      <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 32 }}>
        {/* Pulse rings */}
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="pulse-ring"
            style={{
              width: 96 + i * 48,
              height: 96 + i * 48,
              borderColor: `rgba(0,212,255,${0.2 / i})`,
              animationDelay: `${(i - 1) * 0.5}s`,
              position: 'absolute',
            }}
          />
        ))}
        <div className="splash-logo">🛡️</div>
      </div>

      <div style={{ textAlign: 'center' }}>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '32px', fontWeight: 900, color: '#fff', letterSpacing: '-0.5px' }}>
          Social<span style={{ color: 'var(--neon-blue)' }}>Shield</span>
        </h1>
        <p style={{ marginTop: 10, color: 'rgba(255,255,255,0.45)', fontSize: 15 }}>
          AI-Powered Fraud &amp; Deepfake Detection
        </p>
      </div>

      <div style={{ marginTop: 48, display: 'flex', gap: 6 }}>
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            style={{
              width: i === 1 ? 24 : 8,
              height: 8,
              borderRadius: 4,
              background: i === 1 ? 'var(--neon-blue)' : 'rgba(255,255,255,0.2)',
              transition: 'all 0.3s',
            }}
          />
        ))}
      </div>
    </div>
  );
}
