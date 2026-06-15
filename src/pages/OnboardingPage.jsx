// ─── Onboarding Page ─────────────────────────────────────────────────────────
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const SLIDES = [
  {
    icon: '🛡️',
    title: 'Verify Reality',
    subtitle: 'Detect AI-generated deepfakes, cloned voices, and synthetic media in seconds.',
    color: '#00D4FF',
  },
  {
    icon: '🧠',
    title: 'AI-Powered Analysis',
    subtitle: 'EfficientNet, DistilBERT, and CNN models trained on millions of real-world fraud cases.',
    color: '#8B5CF6',
  },
  {
    icon: '🔍',
    title: 'Scan Anything',
    subtitle: 'Images, videos, audio, text, URLs, and social profiles — all in one place.',
    color: '#06FFA5',
  },
  {
    icon: '⚡',
    title: 'Real-Time Results',
    subtitle: 'Get instant verdicts with confidence scores, heatmaps, and detailed AI explanations.',
    color: '#FF3CAC',
  },
];

export default function OnboardingPage() {
  const [slide, setSlide] = useState(0);
  const navigate = useNavigate();
  const current = SLIDES[slide];

  const handleNext = () => {
    if (slide < SLIDES.length - 1) setSlide((s) => s + 1);
    else finish();
  };

  const finish = () => {
    localStorage.setItem('ss_onboarded', '1');
    navigate('/auth');
  };

  return (
    <div className="onboarding-page">
      {/* Background glow */}
      <div style={{
        position: 'fixed', inset: 0, pointerEvents: 'none',
        background: `radial-gradient(ellipse at 50% 40%, ${current.color}18 0%, transparent 60%)`,
        transition: 'background 0.6s ease',
      }} />

      {/* Content */}
      <div style={{ maxWidth: 440, width: '100%', position: 'relative', zIndex: 1 }}>
        {/* Icon */}
        <div style={{
          width: 120, height: 120, borderRadius: 32,
          background: `linear-gradient(135deg, ${current.color}30, ${current.color}10)`,
          border: `1px solid ${current.color}40`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 56, margin: '0 auto 36px',
          boxShadow: `0 0 60px ${current.color}30`,
          transition: 'all 0.4s ease',
          animation: 'float 3s ease-in-out infinite',
        }}>
          {current.icon}
        </div>

        <h1 style={{
          fontFamily: 'var(--font-display)', fontSize: 32, fontWeight: 800,
          color: '#fff', marginBottom: 16, letterSpacing: '-0.5px',
          transition: 'all 0.3s',
        }}>
          {current.title}
        </h1>

        <p style={{ fontSize: 16, color: 'rgba(255,255,255,0.55)', lineHeight: 1.6, maxWidth: 360, margin: '0 auto 48px' }}>
          {current.subtitle}
        </p>

        {/* Dots */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginBottom: 36 }}>
          {SLIDES.map((_, i) => (
            <button
              key={i}
              onClick={() => setSlide(i)}
              style={{
                width: i === slide ? 28 : 8, height: 8, borderRadius: 4, border: 'none', cursor: 'pointer',
                background: i === slide ? current.color : 'rgba(255,255,255,0.2)',
                transition: 'all 0.3s',
              }}
            />
          ))}
        </div>

        {/* Buttons */}
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
          {slide < SLIDES.length - 1 ? (
            <>
              <button className="btn-neon btn-outline" style={{ minWidth: 100 }} onClick={finish}>
                Skip
              </button>
              <button className="btn-neon" style={{ minWidth: 160 }} onClick={handleNext}>
                Next →
              </button>
            </>
          ) : (
            <button className="btn-neon" style={{ minWidth: 220 }} onClick={finish}>
              🚀 Get Started
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
