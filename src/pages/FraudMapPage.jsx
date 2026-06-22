// ─── Fraud Map Page ───────────────────────────────────────────────────────────
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const REGIONS = [
  { name: 'North America', incidents: 1842, trend: '+12%', risk: 'HIGH',   color: '#FF3B3B', x: 18, y: 28 },
  { name: 'Europe',        incidents: 2140, trend: '+8%',  risk: 'HIGH',   color: '#FF3B3B', x: 43, y: 22 },
  { name: 'South Asia',    incidents: 3201, trend: '+31%', risk: 'HIGH',   color: '#FF3B3B', x: 64, y: 38 },
  { name: 'East Asia',     incidents: 980,  trend: '+5%',  risk: 'MEDIUM', color: '#FFB800', x: 76, y: 30 },
  { name: 'SEA',           incidents: 1540, trend: '+18%', risk: 'HIGH',   color: '#FF3B3B', x: 72, y: 46 },
  { name: 'Middle East',   incidents: 890,  trend: '+22%', risk: 'MEDIUM', color: '#FFB800', x: 54, y: 36 },
  { name: 'Africa',        incidents: 620,  trend: '+9%',  risk: 'MEDIUM', color: '#FFB800', x: 46, y: 52 },
  { name: 'South America', incidents: 540,  trend: '+6%',  risk: 'LOW',    color: '#06FFA5', x: 25, y: 56 },
  { name: 'Oceania',       incidents: 210,  trend: '+3%',  risk: 'LOW',    color: '#06FFA5', x: 80, y: 62 },
];

const INCIDENT_TYPES = [
  { type: 'Image Deepfakes', count: 4821, pct: 38, color: '#00D4FF' },
  { type: 'Voice Clones',    count: 2930, pct: 23, color: '#8B5CF6' },
  { type: 'Scam Text/Email', count: 3124, pct: 25, color: '#FF3CAC' },
  { type: 'Phishing URLs',   count: 1780, pct: 14, color: '#FFB800' },
];

export default function FraudMapPage() {
  const [selected, setSelected] = useState(null);
  const navigate = useNavigate();

  return (
    <div>
      <div className="page-header">
        <h1>🗺️ Global Fraud Map</h1>
        <p>Real-time deepfake &amp; fraud incident tracking worldwide</p>
      </div>

      <div className="section">
        {/* Summary stats */}
        <div className="grid-4" style={{ marginBottom:20 }}>
          {[
            { label:'Total Incidents', value:'12,655', color:'#FF3B3B' },
            { label:'Active Regions',  value:'9',      color:'#FFB800' },
            { label:'Scans Today',     value:'1,204',  color:'#00D4FF' },
            { label:'Blocked Threats', value:'847',    color:'#06FFA5' },
          ].map(({ label, value, color }) => (
            <div key={label} className="stat-card">
              <div className="stat-value" style={{ color, fontSize:26 }}>{value}</div>
              <div className="stat-label">{label}</div>
            </div>
          ))}
        </div>

        {/* Map visualization */}
        <div className="map-container" style={{ marginBottom:20 }}>
          {/* Background grid */}
          <svg style={{ position:'absolute', inset:0, width:'100%', height:'100%', opacity:0.06 }}>
            {Array.from({length:12}).map((_,i)=>(
              <line key={`v${i}`} x1={`${(i+1)*8.3}%`} y1="0" x2={`${(i+1)*8.3}%`} y2="100%" stroke="var(--neon-blue)" strokeWidth="0.5" />
            ))}
            {Array.from({length:8}).map((_,i)=>(
              <line key={`h${i}`} x1="0" y1={`${(i+1)*12.5}%`} x2="100%" y2={`${(i+1)*12.5}%`} stroke="var(--neon-blue)" strokeWidth="0.5" />
            ))}
          </svg>

          {/* Region bubbles */}
          {REGIONS.map((r) => (
            <div
              key={r.name}
              onClick={() => setSelected(selected?.name === r.name ? null : r)}
              style={{
                position:'absolute',
                left:`${r.x}%`, top:`${r.y}%`,
                transform:'translate(-50%,-50%)',
                cursor:'pointer',
              }}
            >
              {/* Pulse ring */}
              <div style={{
                position:'absolute', inset:-12,
                borderRadius:'50%',
                border:`1.5px solid ${r.color}40`,
                animation:'pulse-ring 2.5s ease-out infinite',
              }} />
              <div style={{
                width: Math.max(20, Math.min(44, r.incidents / 80)),
                height: Math.max(20, Math.min(44, r.incidents / 80)),
                borderRadius:'50%',
                background:`${r.color}30`,
                border:`2px solid ${r.color}`,
                boxShadow:`0 0 16px ${r.color}60`,
                display:'flex', alignItems:'center', justifyContent:'center',
                fontSize:10, fontWeight:700, color:r.color,
                transition:'transform 0.2s',
              }}
              onMouseEnter={(e)=>e.currentTarget.style.transform='scale(1.3)'}
              onMouseLeave={(e)=>e.currentTarget.style.transform='scale(1)'}
              >
                {r.risk[0]}
              </div>
              <div style={{ position:'absolute', top:'100%', left:'50%', transform:'translateX(-50%)', marginTop:6, whiteSpace:'nowrap', fontSize:10, color:'rgba(255,255,255,0.6)', fontWeight:600 }}>
                {r.name}
              </div>
            </div>
          ))}

          {/* Legend */}
          <div style={{ position:'absolute', bottom:20, right:20, display:'flex', flexDirection:'column', gap:8 }}>
            {[['HIGH','#FF3B3B'],['MEDIUM','#FFB800'],['LOW','#06FFA5']].map(([l,c]) => (
              <div key={l} style={{ display:'flex', alignItems:'center', gap:6, fontSize:11 }}>
                <div style={{ width:10,height:10,borderRadius:'50%',background:c }} />
                <span style={{ color:'rgba(255,255,255,0.6)' }}>{l} RISK</span>
              </div>
            ))}
          </div>

          {/* Click tooltip */}
          {selected && (
            <div style={{ position:'absolute', top:16, left:16, background:'rgba(13,13,43,0.95)', border:`1px solid ${selected.color}40`, borderRadius:12, padding:'14px 18px', minWidth:200 }}>
              <div style={{ fontWeight:700, marginBottom:6, color:selected.color }}>{selected.name}</div>
              <div style={{ fontSize:13, color:'rgba(255,255,255,0.7)', display:'flex', flexDirection:'column', gap:4 }}>
                <span>📊 Incidents: <b style={{ color:'#fff' }}>{selected.incidents.toLocaleString()}</b></span>
                <span>📈 Trend: <b style={{ color:selected.trend.startsWith('+') ? '#FF3B3B' : '#06FFA5' }}>{selected.trend}</b></span>
                <span>⚠️ Risk: <b style={{ color:selected.color }}>{selected.risk}</b></span>
              </div>
            </div>
          )}
        </div>

        {/* Incident breakdown */}
        <div className="glass-card">
          <h3 style={{ fontWeight:700, marginBottom:16 }}>Incident Type Breakdown</h3>
          <div style={{ display:'flex', flexDirection:'column', gap:14 }}>
            {INCIDENT_TYPES.map(({ type, count, pct, color }) => (
              <div key={type}>
                <div style={{ display:'flex', justifyContent:'space-between', marginBottom:6, fontSize:13 }}>
                  <span>{type}</span>
                  <span style={{ color, fontWeight:700 }}>{count.toLocaleString()} ({pct}%)</span>
                </div>
                <div className="progress-bar-track">
                  <div className="progress-bar-fill" style={{ width:`${pct}%`, background:`linear-gradient(90deg, ${color}80, ${color})` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
