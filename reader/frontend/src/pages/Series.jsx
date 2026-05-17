import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../useAuth'

export default function Series() {
  const { name } = useParams()
  const navigate = useNavigate()
  const [series, setSeries] = useState(null)
  const [imgError, setImgError] = useState(false)
  const [desc, setDesc] = useState(true)
  const decoded = decodeURIComponent(name)
  const { authFetch } = useAuth()

  useEffect(() => {
    authFetch('/api/series/' + encodeURIComponent(decoded))
      .then(r => r.json())
      .then(setSeries)
  }, [decoded])

  if (!series) return (
    <div style={{display:'flex',alignItems:'center',justifyContent:'center',minHeight:'100vh',color:'#666',fontFamily:'var(--font-body)'}}>
      Carregando...
    </div>
  )

  const chapters = desc ? [...series.chapters].reverse() : [...series.chapters]

  return (
    <div className="page">
      <div className="grid-pattern page-bg" />
      <header className="header">
        <div className="header-inner">
          <button className="back-btn" onClick={() => navigate('/')}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="m19 12H5M12 19l-7-7 7-7"/>
            </svg>
            <span>Biblioteca</span>
          </button>
          <div className="logo"><span className="logo-s">S</span>cryll</div>
        </div>
      </header>

      <main className="main">
        <div className="series-hero anim-in">
          <div className="series-cover-wrap">
            {series.cover && !imgError ? (
              <img src={series.cover} alt={series.name} className="series-cover" onError={() => setImgError(true)} />
            ) : (
              <div className="series-cover-ph"><span>{series.name[0]}</span></div>
            )}
          </div>
          <div className="series-meta anim-in anim-in-2">
            <p className="series-tag">MANHWA</p>
            <h1 className="series-name">{series.name}</h1>
            <div className="series-stats">
              <div className="stat">
                <span className="stat-val">{series.chapter_count}</span>
                <span className="stat-label">Capítulos</span>
              </div>
            </div>
            {series.chapters.length > 0 && (
              <Link
                to={'/read/' + encodeURIComponent(series.name) + '/' + series.chapters[0].id}
                className="read-btn"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
                Ler do início
              </Link>
            )}
          </div>
        </div>

        <div className="chapters-section anim-in anim-in-3">
          <div className="chapters-header">
            <h2 className="chapters-title">Capítulos</h2>
            <button
              className="order-toggle"
              onClick={() => setDesc(d => !d)}
              title={desc ? 'Mudar para mais antigo primeiro' : 'Mudar para mais recente primeiro'}
            >
              {desc ? (
                <>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <path d="M12 5v14M5 12l7 7 7-7"/>
                  </svg>
                  Mais recente
                </>
              ) : (
                <>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <path d="M12 19V5M5 12l7-7 7 7"/>
                  </svg>
                  Mais antigo
                </>
              )}
            </button>
          </div>
          <div className="chapters-list">
            {chapters.map((ch, i) => (
              <Link
                key={ch.id}
                to={'/read/' + encodeURIComponent(series.name) + '/' + ch.id}
                className="chapter-row"
                style={{animationDelay: Math.min(i * 0.02, 0.4) + 's'}}
              >
                <span className="chapter-num">Cap. {ch.number}</span>
                <span className="chapter-title-text">{ch.title}</span>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="chapter-arrow">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </Link>
            ))}
          </div>
        </div>
      </main>

      <style>{`
        .page { min-height: 100vh; position: relative; }
        .page-bg { position: fixed; inset: 0; z-index: 0; pointer-events: none; }
        .header { position: sticky; top: 0; z-index: 50; background: rgba(10,10,10,0.85); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border); }
        .header-inner { max-width: 1200px; margin: 0 auto; padding: 0 24px; height: 64px; display: flex; align-items: center; gap: 16px; }
        .back-btn { display: flex; align-items: center; gap: 8px; background: var(--surface); border: 1px solid var(--border); color: var(--text); padding: 8px 16px; border-radius: 8px; cursor: pointer; font-size: 14px; font-family: var(--font-body); transition: border-color 0.2s; }
        .back-btn:hover { border-color: var(--border2); }
        .logo { font-family: var(--font-sans); font-size: 22px; font-weight: 700; margin-left: auto; }
        .logo-s { color: var(--accent); }
        .main { max-width: 1200px; margin: 0 auto; padding: 40px 24px 80px; position: relative; z-index: 1; }
        .series-hero { display: grid; grid-template-columns: 200px 1fr; gap: 40px; margin-bottom: 48px; align-items: start; }
        .series-cover-wrap { position: relative; aspect-ratio: 3/4; border-radius: 14px; overflow: hidden; background: var(--surface); box-shadow: 0 20px 60px rgba(0,0,0,0.5); }
        .series-cover { width: 100%; height: 100%; object-fit: cover; }
        .series-cover-ph { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background: var(--surface2); }
        .series-cover-ph span { font-family: var(--font-sans); font-size: 64px; font-weight: 700; color: var(--text-dim); }
        .series-meta { display: flex; flex-direction: column; gap: 16px; padding-top: 8px; }
        .series-tag { font-family: var(--font-mono); font-size: 11px; color: var(--accent); text-transform: uppercase; letter-spacing: 0.1em; }
        .series-name { font-family: var(--font-sans); font-size: 28px; font-weight: 700; line-height: 1.2; letter-spacing: -0.3px; }
        .series-stats { display: flex; gap: 24px; }
        .stat { display: flex; flex-direction: column; }
        .stat-val { font-family: var(--font-sans); font-size: 28px; font-weight: 700; color: var(--accent); line-height: 1; }
        .stat-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; font-family: var(--font-mono); margin-top: 4px; }
        .read-btn { display: inline-flex; align-items: center; gap: 10px; background: var(--accent); color: #000; font-family: var(--font-sans); font-size: 15px; font-weight: 700; padding: 13px 26px; border-radius: 10px; transition: opacity 0.2s, transform 0.2s; width: fit-content; position: relative; overflow: hidden; }
        .read-btn::after { content: ''; position: absolute; top: 0; left: -100%; width: 60%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent); transform: skewX(-20deg); }
        .read-btn:hover::after { animation: shimmer 0.6s ease-out; }
        .read-btn:hover { transform: translateY(-2px); opacity: 0.92; }
        .chapters-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
        .chapters-title { font-family: var(--font-sans); font-size: 18px; font-weight: 700; }
        .order-toggle {
          display: flex; align-items: center; gap: 7px;
          background: var(--surface); border: 1px solid var(--border);
          color: var(--text-muted); padding: 7px 14px; border-radius: 8px;
          cursor: pointer; font-size: 13px; font-family: var(--font-body);
          transition: border-color 0.2s, color 0.2s, background 0.2s;
        }
        .order-toggle:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-dim); }
        .chapters-list { display: flex; flex-direction: column; gap: 2px; }
        .chapter-row { display: flex; align-items: center; gap: 16px; padding: 13px 14px; border-radius: 10px; border: 1px solid transparent; transition: background 0.15s, border-color 0.15s; }
        .chapter-row:hover { background: var(--surface); border-color: var(--border); }
        .chapter-num { font-family: var(--font-mono); font-size: 12px; color: var(--accent); min-width: 65px; }
        .chapter-title-text { flex: 1; font-size: 14px; color: var(--text-muted); }
        .chapter-arrow { color: var(--text-dim); flex-shrink: 0; }
        .chapter-row:hover .chapter-arrow { color: var(--text-muted); }
        @media (max-width: 640px) {
          .series-hero { grid-template-columns: 130px 1fr; gap: 20px; }
          .series-name { font-size: 20px; }
          .stat-val { font-size: 22px; }
          .main { padding: 24px 16px 60px; }
          .header-inner { padding: 0 16px; }
        }
      `}</style>
    </div>
  )
}
