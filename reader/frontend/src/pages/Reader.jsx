import { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../useAuth'

export default function Reader() {
  const { name, chapter } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loaded, setLoaded] = useState(0)
  const [showUI, setShowUI] = useState(true)
  const hideTimer = useRef(null)
  const decoded = decodeURIComponent(name)
  const { authFetch } = useAuth()

  useEffect(() => {
    authFetch('/api/chapter/' + encodeURIComponent(decoded) + '/' + chapter)
      .then(r => r.json())
      .then(d => { setData(d); setLoaded(0); })
  }, [decoded, chapter])

  useEffect(() => {
    const show = () => {
      setShowUI(true)
      clearTimeout(hideTimer.current)
      hideTimer.current = setTimeout(() => setShowUI(false), 3000)
    }
    window.addEventListener('mousemove', show)
    window.addEventListener('touchstart', show)
    show()
    return () => {
      window.removeEventListener('mousemove', show)
      window.removeEventListener('touchstart', show)
      clearTimeout(hideTimer.current)
    }
  }, [])

  useEffect(() => {
    const handler = (e) => {
      if (!data) return
      if (e.key === 'ArrowLeft' && data.prev) navigate('/read/' + encodeURIComponent(decoded) + '/' + data.prev)
      if (e.key === 'ArrowRight' && data.next) navigate('/read/' + encodeURIComponent(decoded) + '/' + data.next)
      if (e.key === 'Escape') navigate('/series/' + encodeURIComponent(decoded))
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [data, decoded, navigate])

  if (!data) return (
    <div style={{display:'flex',alignItems:'center',justifyContent:'center',minHeight:'100vh',color:'#666',fontFamily:'var(--font-body)'}}>
      Carregando capitulo...
    </div>
  )

  const progress = data.images.length > 0 ? Math.round((loaded / data.images.length) * 100) : 0

  return (
    <div className="reader">
      <div className={'reader-ui ' + (showUI ? 'ui-visible' : 'ui-hidden')}>
        <div className="reader-header">
          <Link to={'/series/' + encodeURIComponent(decoded)} className="reader-back">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="m19 12H5M12 19l-7-7 7-7"/>
            </svg>
          </Link>
          <div className="reader-info">
            <span className="reader-series">{decoded}</span>
            <span className="reader-chapter">Cap. {data.number}</span>
          </div>
          <div className="reader-nav">
            {data.prev ? (
              <Link to={'/read/' + encodeURIComponent(decoded) + '/' + data.prev} className="nav-btn" title="Capitulo anterior">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m15 18-6-6 6-6"/></svg>
              </Link>
            ) : <span className="nav-btn disabled" />}
            <span className="nav-label">{data.chapter_index + 1} / {data.total_chapters}</span>
            {data.next ? (
              <Link to={'/read/' + encodeURIComponent(decoded) + '/' + data.next} className="nav-btn" title="Proximo capitulo">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m9 18 6-6-6-6"/></svg>
              </Link>
            ) : <span className="nav-btn disabled" />}
          </div>
        </div>
        <div className="progress-bar">
          <div className="progress-fill" style={{width: progress + '%'}} />
        </div>
      </div>

      <div className="pages">
        {data.images.map((img, i) => (
          <img
            key={img}
            src={img}
            alt={'Pagina ' + (i + 1)}
            className="page-img"
            loading={i < 3 ? 'eager' : 'lazy'}
            onLoad={() => setLoaded(l => l + 1)}
          />
        ))}

        <div className="chapter-end">
          <p className="chapter-end-label">Fim do Capitulo {data.number}</p>
          <div className="chapter-end-btns">
            {data.prev && (
              <Link to={'/read/' + encodeURIComponent(decoded) + '/' + data.prev} className="end-btn end-btn-prev">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m15 18-6-6 6-6"/></svg>
                Cap. Anterior
              </Link>
            )}
            <Link to={'/series/' + encodeURIComponent(decoded)} className="end-btn end-btn-list">
              Lista
            </Link>
            {data.next && (
              <Link to={'/read/' + encodeURIComponent(decoded) + '/' + data.next} className="end-btn end-btn-next">
                Proximo Cap.
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m9 18 6-6-6-6"/></svg>
              </Link>
            )}
          </div>
        </div>
      </div>

      <style>{`
        .reader { background: #000; min-height: 100vh; }
        .reader-ui { position: fixed; top: 0; left: 0; right: 0; z-index: 100; transition: opacity 0.3s, transform 0.3s; }
        .ui-visible { opacity: 1; transform: translateY(0); }
        .ui-hidden { opacity: 0; transform: translateY(-8px); pointer-events: none; }
        .reader-header {
          display: flex; align-items: center; gap: 16px;
          background: rgba(0,0,0,0.9); backdrop-filter: blur(20px);
          padding: 0 20px; height: 56px;
          border-bottom: 1px solid var(--border);
        }
        .reader-back {
          display: flex; align-items: center; justify-content: center;
          width: 36px; height: 36px; border-radius: 8px;
          background: var(--surface); border: 1px solid var(--border);
          flex-shrink: 0; transition: border-color 0.2s;
        }
        .reader-back:hover { border-color: var(--border2); }
        .reader-info { flex: 1; overflow: hidden; }
        .reader-series {
          display: block; font-family: var(--font-sans); font-size: 13px; font-weight: 600;
          white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }
        .reader-chapter { font-family: var(--font-mono); font-size: 11px; color: var(--accent); }
        .reader-nav { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
        .nav-btn {
          display: flex; align-items: center; justify-content: center;
          width: 32px; height: 32px; border-radius: 8px;
          background: var(--surface); border: 1px solid var(--border);
          transition: border-color 0.2s;
        }
        .nav-btn:hover { border-color: var(--border2); }
        .nav-btn.disabled { opacity: 0.3; pointer-events: none; }
        .nav-label { font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); white-space: nowrap; }
        .progress-bar { height: 2px; background: rgba(255,255,255,0.08); }
        .progress-fill { height: 100%; background: var(--accent); transition: width 0.3s; }
        .pages {
          display: flex; flex-direction: column; align-items: center;
          padding: 56px 0 0; gap: 2px;
        }
        .page-img { width: 100%; max-width: 800px; display: block; }
        .chapter-end {
          width: 100%; max-width: 800px; padding: 60px 24px;
          text-align: center; border-top: 1px solid var(--border);
        }
        .chapter-end-label { font-family: var(--font-sans); font-size: 18px; font-weight: 600; color: var(--text-muted); margin-bottom: 32px; }
        .chapter-end-btns { display: flex; justify-content: center; gap: 12px; flex-wrap: wrap; }
        .end-btn {
          display: flex; align-items: center; gap: 8px;
          padding: 12px 24px; border-radius: 10px;
          font-family: var(--font-sans); font-size: 14px; font-weight: 600;
          border: 1px solid var(--border); background: var(--surface);
          transition: border-color 0.2s, background 0.2s;
        }
        .end-btn:hover { border-color: var(--border2); }
        .end-btn-next { background: var(--accent); color: #000; border-color: var(--accent); }
        .end-btn-next:hover { opacity: 0.9; }
        @media (max-width: 640px) {
          .reader-series { display: none; }
          .page-img { max-width: 100%; }
        }
      `}</style>
    </div>
  )
}
