import { useEffect, useState, useRef } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../useAuth'

function MangaCard({ series, index }) {
  const [imgError, setImgError] = useState(false)
  const delay = Math.min(index * 0.04, 0.4)
  return (
    <Link
      to={'/series/' + encodeURIComponent(series.name)}
      style={{ animationDelay: delay + 's' }}
      className="anim-in"
    >
      <div className="manga-card">
        <div className="manga-cover-wrap">
          {series.cover && !imgError ? (
            <img
              src={series.cover}
              alt={series.name}
              onError={() => setImgError(true)}
              className="manga-cover-img"
            />
          ) : (
            <div className="manga-cover-placeholder">
              <span>{series.name[0]}</span>
            </div>
          )}
          <div className="manga-cover-overlay" />
          <div className="manga-badge">Cap. {series.latest_chapter}</div>
        </div>
        <div className="manga-info">
          <h3 className="manga-title">{series.name}</h3>
          <p className="manga-meta">{series.chapter_count} capítulos</p>
        </div>
      </div>
    </Link>
  )
}

function AddSidebar({ open, onClose, onAdded }) {
  const [url, setUrl] = useState('')
  const [status, setStatus] = useState(null) // null | 'loading' | {ok, name} | {error}
  const inputRef = useRef(null)
  const { authFetch } = useAuth()

  useEffect(() => {
    if (open) {
      setUrl('')
      setStatus(null)
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [open])

  useEffect(() => {
    if (!open) return
    const handler = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [open, onClose])

  async function handleAdd() {
    const trimmed = url.trim()
    if (!trimmed) return
    setStatus('loading')
    try {
      const res = await authFetch('/api/manga/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: trimmed }),
      })
      const data = await res.json()
      if (!res.ok) {
        setStatus({ error: data.detail || 'Erro ao adicionar' })
      } else {
        setStatus({ ok: true, name: data.name })
        setUrl('')
        onAdded && onAdded(data)
      }
    } catch {
      setStatus({ error: 'Falha na conexão com a API' })
    }
  }

  function handleKey(e) {
    if (e.key === 'Enter') handleAdd()
  }

  const detectedSite = url.includes('manhuaus.com') ? 'ManhuaUS'
    : url.includes('mangadex.org') ? 'MangaDex'
    : url.includes('comicpark.net') ? 'ComicPark'
    : url.includes('vortexscans.com') ? 'VortexScans'
    : null

  return (
    <>
      <div
        className={`sidebar-backdrop ${open ? 'sidebar-backdrop--open' : ''}`}
        onClick={onClose}
      />
      <aside className={`sidebar ${open ? 'sidebar--open' : ''}`}>
        <div className="sidebar-header">
          <h2 className="sidebar-title">Adicionar Manhwa</h2>
          <button className="sidebar-close" onClick={onClose} aria-label="Fechar">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 6 6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <div className="sidebar-body">
          <p className="sidebar-hint">Cole o link do manhwa que quer acompanhar. Sites suportados: ManhuaUS, MangaDex, ComicPark, VortexScans.</p>

          <div className="add-input-wrap">
            <label className="add-label">URL do Manhwa</label>
            <input
              ref={inputRef}
              className={`add-input ${status?.error ? 'add-input--error' : ''}`}
              placeholder="https://manhuaus.com/manga/..."
              value={url}
              onChange={e => { setUrl(e.target.value); setStatus(null) }}
              onKeyDown={handleKey}
              disabled={status === 'loading'}
            />
            {detectedSite && (
              <span className="site-badge">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="10"/></svg>
                {detectedSite}
              </span>
            )}
          </div>

          {status?.error && (
            <div className="add-feedback add-feedback--error">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/>
              </svg>
              {status.error}
            </div>
          )}

          {status?.ok && (
            <div className="add-feedback add-feedback--ok">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M20 6 9 17l-5-5"/>
              </svg>
              <span><strong>{status.name}</strong> adicionado! Será baixado na próxima execução.</span>
            </div>
          )}

          <button
            className="add-btn-submit"
            onClick={handleAdd}
            disabled={!url.trim() || status === 'loading'}
          >
            {status === 'loading' ? (
              <><span className="spinner" />Buscando...</>
            ) : (
              <><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M12 5v14M5 12h14"/></svg>Adicionar</>
            )}
          </button>
        </div>

        <div className="sidebar-footer">
          <p className="sidebar-footer-text">Os capítulos são baixados automaticamente a cada 3 horas.</p>
        </div>
      </aside>
    </>
  )
}

export default function Home() {
  const [library, setLibrary] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { authFetch, logout } = useAuth()

  useEffect(() => {
    authFetch('/api/library')
      .then(r => r.json())
      .then(d => { setLibrary(d); setLoading(false); })
      .catch(() => setLoading(false))
  }, [])

  const filtered = library.filter(s =>
    s.name.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="page">
      <div className="grid-pattern page-bg" />
      <header className="header">
        <div className="header-inner">
          <div className="logo">
            <span className="logo-s">S</span>cryll
          </div>
          <div className="search-wrap">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="search-icon">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
            <input
              className="search"
              placeholder="Buscar manhwa..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
          <button className="header-add-btn" onClick={() => setSidebarOpen(true)}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M12 5v14M5 12h14"/>
            </svg>
            <span>Adicionar</span>
          </button>
          <button className="header-logout-btn" onClick={logout} title="Sair">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>
            </svg>
          </button>
        </div>
      </header>

      <main className="main">
        <div className="section-header anim-in">
          <h1 className="section-title">Biblioteca</h1>
          <span className="section-count">{filtered.length} series</span>
        </div>

        {loading ? (
          <div className="skeleton-grid">
            {Array.from({length: 12}).map((_, i) => (
              <div key={i} className="skeleton-card" style={{animationDelay: (i*0.05) + 's'}} />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="empty-state anim-in">
            <p>Nenhum manhwa encontrado</p>
          </div>
        ) : (
          <div className="manga-grid">
            {filtered.map((s, i) => <MangaCard key={s.name} series={s} index={i} />)}
          </div>
        )}
      </main>

      <AddSidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onAdded={() => {}}
      />

      <style>{`
        .page { min-height: 100vh; position: relative; }
        .page-bg { position: fixed; inset: 0; z-index: 0; pointer-events: none; }
        .header {
          position: sticky; top: 0; z-index: 50;
          background: rgba(10,10,10,0.85);
          backdrop-filter: blur(20px);
          border-bottom: 1px solid var(--border);
        }
        .header-inner {
          max-width: 1400px; margin: 0 auto;
          padding: 0 24px;
          height: 64px; display: flex; align-items: center; gap: 16px;
        }
        .logo { font-family: var(--font-sans); font-size: 22px; font-weight: 700; letter-spacing: -0.5px; flex-shrink: 0; }
        .logo-s { color: var(--accent); }
        .search-wrap { flex: 1; max-width: 400px; position: relative; display: flex; align-items: center; }
        .search-icon { position: absolute; left: 14px; color: var(--text-muted); pointer-events: none; }
        .search {
          width: 100%; background: var(--surface); border: 1px solid var(--border);
          border-radius: 10px; padding: 10px 16px 10px 40px;
          color: var(--text); font-size: 14px; font-family: var(--font-body);
          outline: none; transition: border-color 0.2s;
        }
        .search:focus { border-color: var(--border2); }
        .search::placeholder { color: var(--text-muted); }
        .header-add-btn {
          display: flex; align-items: center; gap: 8px;
          background: var(--accent); color: #000;
          border: none; border-radius: 9px;
          padding: 9px 16px; cursor: pointer;
          font-family: var(--font-sans); font-size: 13px; font-weight: 700;
          transition: opacity 0.2s, transform 0.2s;
          flex-shrink: 0; margin-left: auto;
        }
        .header-add-btn:hover { opacity: 0.88; transform: translateY(-1px); }
        .header-logout-btn {
          width: 36px; height: 36px; border-radius: 9px;
          background: var(--surface); border: 1px solid var(--border);
          color: var(--text-muted); cursor: pointer; display: flex; align-items: center; justify-content: center;
          flex-shrink: 0; transition: border-color 0.2s, color 0.2s;
        }
        .header-logout-btn:hover { border-color: var(--border2); color: var(--text); }

        /* Sidebar */
        .sidebar-backdrop {
          position: fixed; inset: 0; z-index: 100;
          background: rgba(0,0,0,0);
          pointer-events: none;
          transition: background 0.3s;
        }
        .sidebar-backdrop--open {
          background: rgba(0,0,0,0.6);
          pointer-events: all;
          backdrop-filter: blur(4px);
        }
        .sidebar {
          position: fixed; top: 0; right: 0; bottom: 0; z-index: 101;
          width: 380px; max-width: 100vw;
          background: #111;
          border-left: 1px solid var(--border);
          display: flex; flex-direction: column;
          transform: translateX(100%);
          transition: transform 0.35s cubic-bezier(0.16,1,0.3,1);
          box-shadow: -20px 0 60px rgba(0,0,0,0.5);
        }
        .sidebar--open { transform: translateX(0); }
        .sidebar-header {
          display: flex; align-items: center; justify-content: space-between;
          padding: 20px 24px; border-bottom: 1px solid var(--border);
          flex-shrink: 0;
        }
        .sidebar-title { font-family: var(--font-sans); font-size: 17px; font-weight: 700; }
        .sidebar-close {
          width: 32px; height: 32px; border-radius: 8px;
          background: var(--surface); border: 1px solid var(--border);
          color: var(--text-muted); cursor: pointer; display: flex; align-items: center; justify-content: center;
          transition: border-color 0.2s, color 0.2s;
        }
        .sidebar-close:hover { border-color: var(--border2); color: var(--text); }
        .sidebar-body { flex: 1; padding: 24px; display: flex; flex-direction: column; gap: 16px; overflow-y: auto; }
        .sidebar-hint { font-size: 13px; color: var(--text-muted); line-height: 1.5; }
        .add-label { display: block; font-family: var(--font-mono); font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); margin-bottom: 8px; }
        .add-input-wrap { position: relative; display: flex; flex-direction: column; }
        .add-input {
          background: var(--surface); border: 1px solid var(--border);
          border-radius: 10px; padding: 12px 14px;
          color: var(--text); font-size: 13px; font-family: var(--font-body);
          outline: none; transition: border-color 0.2s;
          width: 100%;
        }
        .add-input:focus { border-color: var(--accent); }
        .add-input--error { border-color: #ff4444 !important; }
        .add-input::placeholder { color: var(--text-dim); }
        .site-badge {
          display: inline-flex; align-items: center; gap: 5px;
          margin-top: 6px; align-self: flex-start;
          background: rgba(204,255,0,0.1); border: 1px solid rgba(204,255,0,0.25);
          color: var(--accent); font-family: var(--font-mono); font-size: 11px;
          padding: 3px 8px; border-radius: 6px;
        }
        .add-feedback {
          display: flex; align-items: flex-start; gap: 8px;
          padding: 12px 14px; border-radius: 10px;
          font-size: 13px; line-height: 1.4;
        }
        .add-feedback--error { background: rgba(255,68,68,0.1); border: 1px solid rgba(255,68,68,0.25); color: #ff6666; }
        .add-feedback--ok { background: rgba(204,255,0,0.08); border: 1px solid rgba(204,255,0,0.2); color: var(--text); }
        .add-feedback svg { flex-shrink: 0; margin-top: 1px; }
        .add-feedback--ok svg { color: var(--accent); }
        .add-btn-submit {
          display: flex; align-items: center; justify-content: center; gap: 8px;
          background: var(--accent); color: #000;
          border: none; border-radius: 10px;
          padding: 13px; cursor: pointer;
          font-family: var(--font-sans); font-size: 14px; font-weight: 700;
          transition: opacity 0.2s;
          margin-top: 4px;
        }
        .add-btn-submit:hover:not(:disabled) { opacity: 0.88; }
        .add-btn-submit:disabled { opacity: 0.45; cursor: not-allowed; }
        .spinner {
          width: 14px; height: 14px; border-radius: 50%;
          border: 2px solid rgba(0,0,0,0.3);
          border-top-color: #000;
          animation: spin 0.7s linear infinite;
          flex-shrink: 0;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .sidebar-footer {
          padding: 16px 24px; border-top: 1px solid var(--border);
          flex-shrink: 0;
        }
        .sidebar-footer-text { font-size: 12px; color: var(--text-dim); line-height: 1.4; }

        /* Library */
        .main { max-width: 1400px; margin: 0 auto; padding: 40px 24px 80px; position: relative; z-index: 1; }
        .section-header { display: flex; align-items: baseline; gap: 12px; margin-bottom: 28px; }
        .section-title { font-family: var(--font-sans); font-size: 24px; font-weight: 700; }
        .section-count { font-family: var(--font-mono); font-size: 12px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
        .manga-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 20px; }
        .manga-card {
          background: var(--surface); border: 1px solid var(--border);
          border-radius: 12px; overflow: hidden;
          transition: transform 0.25s cubic-bezier(0.16,1,0.3,1), border-color 0.2s, box-shadow 0.2s;
          cursor: pointer;
        }
        .manga-card:hover {
          transform: translateY(-4px);
          border-color: var(--border2);
          box-shadow: 0 16px 40px rgba(0,0,0,0.5), 0 0 0 1px rgba(204,255,0,0.08);
        }
        .manga-cover-wrap { position: relative; aspect-ratio: 3/4; overflow: hidden; background: var(--surface2); }
        .manga-cover-img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.4s; }
        .manga-card:hover .manga-cover-img { transform: scale(1.05); }
        .manga-cover-overlay { position: absolute; inset: 0; background: linear-gradient(to top, rgba(10,10,10,0.8) 0%, transparent 60%); }
        .manga-cover-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background: var(--surface2); }
        .manga-cover-placeholder span { font-family: var(--font-sans); font-size: 48px; font-weight: 700; color: var(--text-dim); text-transform: uppercase; }
        .manga-badge { position: absolute; bottom: 8px; right: 8px; background: var(--accent); color: #000; font-family: var(--font-mono); font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 6px; letter-spacing: 0.03em; }
        .manga-info { padding: 12px; }
        .manga-title { font-family: var(--font-sans); font-size: 13px; font-weight: 600; line-height: 1.3; margin-bottom: 4px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
        .manga-meta { font-size: 11px; color: var(--text-muted); font-family: var(--font-mono); }
        .skeleton-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 20px; }
        .skeleton-card { aspect-ratio: 3/4; background: var(--surface); border-radius: 12px; border: 1px solid var(--border); animation: pulse 1.5s ease-in-out infinite; }
        .empty-state { text-align: center; padding: 80px; color: var(--text-muted); font-size: 16px; }
        @media (max-width: 640px) {
          .manga-grid { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; }
          .main { padding: 24px 16px 60px; }
          .header-inner { padding: 0 16px; gap: 12px; }
          .header-add-btn span { display: none; }
          .header-add-btn { padding: 9px; }
          .sidebar { width: 100vw; }
        }
      `}</style>
    </div>
  )
}
