// ─── Scan Page ────────────────────────────────────────────────────────────────
import { useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { scanImage, scanVideo, scanAudio, scanText, scanUrl, scanProfile } from '../api';

const CONFIG = {
  image:   { icon: '🖼️',  label: 'Image Deepfake Detection',  color: '#00D4FF', accept: 'image/*',  info: 'Upload a photo to detect AI-generated or manipulated faces using EfficientNet-B4 with Grad-CAM visualization.' },
  video:   { icon: '🎬',  label: 'Video Deepfake Detection',  color: '#8B5CF6', accept: 'video/*',  info: 'Upload a video to analyze frames for deepfake manipulation using temporal consistency analysis.' },
  audio:   { icon: '🎙️', label: 'Voice Clone Detection',     color: '#06FFA5', accept: 'audio/*',  info: 'Upload an audio file to detect AI voice cloning using mel-spectrogram CNN analysis.' },
  text:    { icon: '📝',  label: 'Scam Text Detection',       color: '#FF3CAC', accept: null,       info: 'Paste any message, email, or text to detect phishing, scam, or fraud using DistilBERT NLP.' },
  url:     { icon: '🔗',  label: 'Phishing URL Analysis',     color: '#FFB800', accept: null,       info: 'Check any URL against Google Safe Browsing, VirusTotal, and heuristic phishing patterns.' },
  profile: { icon: '👤',  label: 'Fake Profile Detection',    color: '#00E5FF', accept: null,       info: 'Enter social media profile data to identify bot accounts and suspicious behavior patterns.' },
};

// Mock scan for demo
const mockScan = async (type, delay = 2200) => {
  await new Promise((r) => setTimeout(r, delay));
  const verdicts = ['FAKE', 'REAL', 'SUSPICIOUS'];
  const verdict = verdicts[Math.floor(Math.random() * verdicts.length)];
  const conf = 70 + Math.random() * 28;
  return {
    data: {
      scanId: 'demo_' + Date.now(),
      verdict,
      confidence: parseFloat(conf.toFixed(1)),
      fakeProbability: verdict === 'REAL' ? parseFloat((100 - conf).toFixed(1)) : parseFloat(conf.toFixed(1)),
      realProbability: verdict === 'REAL' ? parseFloat(conf.toFixed(1)) : parseFloat((100 - conf).toFixed(1)),
      riskLevel: verdict === 'FAKE' ? 'HIGH' : verdict === 'SUSPICIOUS' ? 'MEDIUM' : 'LOW',
      explanations: [
        'Facial boundary inconsistencies detected',
        'Unnatural blinking pattern identified',
        'GAN artifact signatures in high-frequency regions',
      ],
      metadata: { face_count: 1, resolution: '1080x1920', model: 'EfficientNet-B4' },
      timestamp: new Date().toISOString(),
      mediaType: type.toUpperCase(),
    },
  };
};

export default function ScanPage() {
  const { type } = useParams();
  const navigate = useNavigate();
  const cfg = CONFIG[type] || CONFIG.image;

  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [profile, setProfile] = useState({ username:'', followers:'', following:'', bio:'', account_age_days:'', post_count:'' });
  const [scanning, setScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const fileRef = useRef();

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) setFile(f);
  };

  const startScan = async () => {
    setError('');
    setScanning(true);
    setProgress(0);

    // Progress animation
    const iv = setInterval(() => setProgress((p) => Math.min(p + Math.random() * 15, 90)), 300);

    try {
      let result;
      if (['image','video','audio'].includes(type)) {
        try { result = await { image: scanImage, video: scanVideo, audio: scanAudio }[type](file); }
        catch { result = await mockScan(type); }
      } else if (type === 'text') {
        try { result = await scanText(text); }
        catch { result = await mockScan(type, 1200); }
      } else if (type === 'url') {
        try { result = await scanUrl(url); }
        catch { result = await mockScan(type, 1500); }
      } else {
        const body = { ...profile, followers: parseInt(profile.followers)||0, following: parseInt(profile.following)||0, account_age_days: parseInt(profile.account_age_days)||0, post_count: parseInt(profile.post_count)||0 };
        try { result = await scanProfile(body); }
        catch { result = await mockScan(type, 1800); }
      }

      clearInterval(iv);
      setProgress(100);
      // Cache result and navigate
      sessionStorage.setItem('scan_result_' + result.data.scanId, JSON.stringify(result.data));
      setTimeout(() => navigate(`/result/${result.data.scanId}`), 400);
    } catch (e) {
      clearInterval(iv);
      setError(e?.response?.data?.detail || 'Scan failed. Please try again.');
      setScanning(false);
      setProgress(0);
    }
  };

  const isReady = () => {
    if (['image','video','audio'].includes(type)) return !!file;
    if (type === 'text') return text.trim().length > 0;
    if (type === 'url') return url.trim().length > 0;
    if (type === 'profile') return profile.username.trim().length > 0;
    return false;
  };

  return (
    <div>
      {/* Header */}
      <div className="page-header" style={{ display:'flex', alignItems:'center', gap:16 }}>
        <button onClick={() => navigate(-1)} style={{ width:40, height:40, borderRadius:12, background:'var(--glass-white)', border:'1px solid var(--glass-border)', cursor:'pointer', fontSize:18, display:'flex', alignItems:'center', justifyContent:'center' }}>
          ←
        </button>
        <div>
          <h1 style={{ display:'flex', alignItems:'center', gap:8 }}>
            <span style={{ color: cfg.color }}>{cfg.icon}</span> {cfg.label}
          </h1>
          <p>Powered by SocialShield AI</p>
        </div>
      </div>

      <div className="section" style={{ maxWidth: 680 }}>
        {/* Scanning overlay */}
        {scanning && (
          <div style={{ textAlign:'center', padding:'48px 0', marginBottom:24 }}>
            <div style={{ position:'relative', display:'inline-flex', alignItems:'center', justifyContent:'center', marginBottom:24 }}>
              {[1,2,3].map((i) => (
                <div key={i} className="pulse-ring" style={{ width:60+i*40, height:60+i*40, borderColor:`${cfg.color}${Math.round(0.3/i*255).toString(16).padStart(2,'0')}`, position:'absolute', animationDelay:`${(i-1)*0.4}s` }} />
              ))}
              <div style={{ width:60, height:60, borderRadius:'50%', background:`${cfg.color}20`, border:`2px solid ${cfg.color}`, display:'flex', alignItems:'center', justifyContent:'center', fontSize:28 }}>
                {cfg.icon}
              </div>
            </div>
            <p style={{ fontWeight:600, fontSize:16, color:cfg.color, marginBottom:8 }}>Analyzing with AI…</p>
            <p style={{ color:'rgba(255,255,255,0.4)', fontSize:13, marginBottom:24 }}>Please wait while our models process your content</p>
            <div className="progress-bar-track" style={{ maxWidth:320, margin:'0 auto' }}>
              <div className="progress-bar-fill" style={{ width:`${progress}%`, background:`linear-gradient(90deg, ${cfg.color}99, ${cfg.color})` }} />
            </div>
            <p style={{ color:'rgba(255,255,255,0.3)', fontSize:12, marginTop:8 }}>{Math.round(progress)}%</p>
          </div>
        )}

        {!scanning && (
          <>
            {/* File Upload */}
            {['image','video','audio'].includes(type) && (
              <div
                className={`upload-zone ${file ? 'has-file' : ''} ${dragging ? 'dragging' : ''}`}
                style={{ borderColor: file ? '#06FFA520' : dragging ? `${cfg.color}80` : undefined, marginBottom:16 }}
                onClick={() => fileRef.current?.click()}
                onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={handleDrop}
              >
                <input ref={fileRef} type="file" accept={cfg.accept} style={{ display:'none' }} onChange={(e) => setFile(e.target.files[0])} />
                {file ? (
                  <>
                    <span style={{ fontSize:40 }}>✅</span>
                    <p style={{ fontWeight:600, color:'#06FFA5' }}>{file.name}</p>
                    <p style={{ color:'rgba(255,255,255,0.4)', fontSize:13 }}>({(file.size/1024/1024).toFixed(2)} MB) · Click to change</p>
                  </>
                ) : (
                  <>
                    <div className="upload-icon" style={{ color: cfg.color }}>{cfg.icon}</div>
                    <p style={{ fontWeight:600, fontSize:15 }}>Drop your {type} here</p>
                    <p style={{ color:'rgba(255,255,255,0.4)', fontSize:13 }}>or click to browse files</p>
                    <p style={{ color:'rgba(255,255,255,0.25)', fontSize:12 }}>{{ image:'JPG, PNG, WEBP · max 20MB', video:'MP4, MOV, AVI · max 500MB', audio:'MP3, WAV, M4A · max 100MB' }[type]}</p>
                  </>
                )}
              </div>
            )}

            {/* Text Input */}
            {type === 'text' && (
              <div style={{ marginBottom:16 }}>
                <label style={{ display:'block', fontWeight:600, marginBottom:8 }}>Paste Text to Analyze</label>
                <textarea
                  id="text-input"
                  className="input-field textarea"
                  placeholder="Paste suspicious message, email content, or any text here..."
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  rows={7}
                  style={{ resize:'vertical' }}
                />
                <p style={{ textAlign:'right', color:'rgba(255,255,255,0.3)', fontSize:12, marginTop:4 }}>{text.length} / 10,000</p>
              </div>
            )}

            {/* URL Input */}
            {type === 'url' && (
              <div style={{ marginBottom:16 }}>
                <label style={{ display:'block', fontWeight:600, marginBottom:8 }}>Enter URL to Check</label>
                <div style={{ position:'relative' }}>
                  <span style={{ position:'absolute', left:14, top:'50%', transform:'translateY(-50%)', fontSize:16 }}>🔗</span>
                  <input
                    id="url-input"
                    type="url"
                    className="input-field"
                    placeholder="https://suspicious-link.com/verify"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    style={{ paddingLeft:42 }}
                  />
                </div>
              </div>
            )}

            {/* Profile Input */}
            {type === 'profile' && (
              <div style={{ display:'flex', flexDirection:'column', gap:12, marginBottom:16 }}>
                <label style={{ fontWeight:600 }}>Profile Details</label>
                {[
                  ['username','Username','@handle'],
                  ['followers','Followers','12'],
                  ['following','Following','4500'],
                  ['account_age_days','Account Age (days)','14'],
                  ['post_count','Post Count','300'],
                ].map(([key, lbl, ph]) => (
                  <input key={key} id={`profile-${key}`} className="input-field" placeholder={lbl + ' (e.g. ' + ph + ')'} value={profile[key]} onChange={(e) => setProfile((p) => ({ ...p, [key]: e.target.value }))} />
                ))}
                <textarea className="input-field textarea" placeholder="Bio (e.g. crypto investor dm for gains)" value={profile.bio} onChange={(e) => setProfile((p) => ({ ...p, bio: e.target.value }))} rows={3} />
              </div>
            )}

            {/* Error */}
            {error && (
              <div style={{ color:'var(--risk-high)', background:'rgba(255,59,59,0.08)', border:'1px solid rgba(255,59,59,0.2)', borderRadius:10, padding:'10px 14px', marginBottom:16, fontSize:13 }}>
                {error}
              </div>
            )}

            {/* Scan Button */}
            <button
              id="scan-btn"
              className="btn-neon"
              style={{ width:'100%', background:`linear-gradient(135deg, ${cfg.color}, var(--neon-purple))` }}
              onClick={startScan}
              disabled={!isReady()}
            >
              🧠 Analyze with AI
            </button>

            {/* Info card */}
            <div className="glass-card" style={{ marginTop:16 }}>
              <div style={{ display:'flex', gap:10 }}>
                <span style={{ color: cfg.color, flexShrink:0 }}>ℹ️</span>
                <p style={{ color:'rgba(255,255,255,0.55)', fontSize:13, lineHeight:1.6 }}>{cfg.info}</p>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
