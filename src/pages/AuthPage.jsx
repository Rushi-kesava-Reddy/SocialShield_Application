// ─── Auth Page ────────────────────────────────────────────────────────────────
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';

export default function AuthPage() {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login, signUp, loginWithGoogle } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!email || !password) { setError('Email and password are required.'); return; }
    if (password.length < 6) { setError('Password must be at least 6 characters.'); return; }

    setLoading(true);
    try {
      if (isSignUp) {
        await signUp(email, password);
      } else {
        await login(email, password);
      }
      navigate('/home');
    } catch (err) {
      const msg = err?.code === 'auth/user-not-found' ? 'No account found with this email.' :
                  err?.code === 'auth/wrong-password' ? 'Incorrect password.' :
                  err?.code === 'auth/email-already-in-use' ? 'Email already registered.' :
                  err?.message || 'Authentication failed. Please try again.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setLoading(true);
    setError('');
    try {
      await loginWithGoogle();
      navigate('/home');
    } catch (err) {
      setError(err?.message || 'Google sign-in failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card animate-fade-up">
        {/* Logo */}
        <div className="auth-logo">
          <div className="logo-icon">🛡️</div>
          <span style={{ fontFamily: 'var(--font-display)', fontSize: 18, fontWeight: 700 }}>SocialShield</span>
        </div>

        <h1 style={{ textAlign: 'center', fontSize: 24, fontWeight: 800, marginBottom: 6 }}>
          {isSignUp ? 'Create Account' : 'Welcome Back'}
        </h1>
        <p style={{ textAlign: 'center', color: 'rgba(255,255,255,0.45)', fontSize: 14, marginBottom: 28 }}>
          {isSignUp ? 'Join the fight against digital fraud' : 'Sign in to your secure dashboard'}
        </p>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {/* Email */}
          <div style={{ position: 'relative' }}>
            <span style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', fontSize: 16 }}>✉️</span>
            <input
              id="email"
              type="email"
              className="input-field"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{ paddingLeft: 40 }}
              autoComplete="email"
            />
          </div>

          {/* Password */}
          <div style={{ position: 'relative' }}>
            <span style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', fontSize: 16 }}>🔒</span>
            <input
              id="password"
              type={showPass ? 'text' : 'password'}
              className="input-field"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ paddingLeft: 40, paddingRight: 44 }}
              autoComplete={isSignUp ? 'new-password' : 'current-password'}
            />
            <button
              type="button"
              onClick={() => setShowPass((v) => !v)}
              style={{ position: 'absolute', right: 14, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', fontSize: 16 }}
            >
              {showPass ? '🙈' : '👁️'}
            </button>
          </div>

          {error && (
            <div style={{ color: 'var(--risk-high)', fontSize: 13, textAlign: 'center', padding: '8px 12px', background: 'rgba(255,59,59,0.08)', borderRadius: 8, border: '1px solid rgba(255,59,59,0.2)' }}>
              {error}
            </div>
          )}

          <button id="submit-btn" type="submit" className="btn-neon" style={{ width: '100%', marginTop: 4 }} disabled={loading}>
            {loading ? <span className="spinner" /> : (isSignUp ? 'Create Account' : 'Sign In')}
          </button>
        </form>

        <div className="divider" style={{ margin: '20px 0' }}>or</div>

        <button
          id="google-signin-btn"
          className="btn-neon btn-outline"
          style={{ width: '100%' }}
          onClick={handleGoogleSignIn}
          disabled={loading}
        >
          <span style={{ fontSize: 18 }}>🇬</span> Continue with Google
        </button>

        <p style={{ textAlign: 'center', marginTop: 20, fontSize: 14, color: 'rgba(255,255,255,0.4)' }}>
          {isSignUp ? 'Already have an account?' : "Don't have an account?"}
          {' '}
          <button
            style={{ background: 'none', border: 'none', color: 'var(--neon-blue)', cursor: 'pointer', fontWeight: 600, fontSize: 14 }}
            onClick={() => { setIsSignUp((v) => !v); setError(''); }}
          >
            {isSignUp ? 'Sign In' : 'Sign Up'}
          </button>
        </p>
      </div>
    </div>
  );
}
