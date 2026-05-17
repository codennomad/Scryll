import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../useAuth'

export default function Login() {
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const { token, login } = useAuth()
  const navigate = useNavigate()
  const inputRef = useRef(null)

  useEffect(() => {
    if (token) navigate('/', { replace: true })
    else inputRef.current?.focus()
  }, [token, navigate])

  async function handleSubmit(e) {
    e.preventDefault()
    if (!password || loading) return
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password }),
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data.detail || 'Erro ao fazer login')
        setPassword('')
        inputRef.current?.focus()
      } else {
        login(data.token)
        navigate('/', { replace: true })
      }
    } catch {
      setError('Falha na conexão')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="grid-pattern login-bg" />
      <div className="login-box anim-in">
        <div className="login-logo">
          <span className="login-logo-s">S</span>cryll
        </div>
        <p className="login-sub">Acesso privado</p>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="login-field">
            <label className="login-label">Senha</label>
            <div className="login-input-wrap">
              <svg className="login-input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
              <input
                ref={inputRef}
                type="password"
                className={`login-input ${error ? 'login-input--error' : ''}`}
                placeholder="••••••••••"
                value={password}
                onChange={e => { setPassword(e.target.value); setError(null) }}
                disabled={loading}
                autoComplete="current-password"
              />
            </div>
          </div>

          {error && (
            <div className="login-error">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/>
              </svg>
              {error}
            </div>
          )}

          <button type="submit" className="login-btn" disabled={!password || loading}>
            {loading
              ? <><span className="spinner" />Entrando...</>
              : <>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3"/>
                  </svg>
                  Entrar
                </>
            }
          </button>
        </form>
      </div>

      <style>{`
        .login-page {
          min-height: 100vh; display: flex; align-items: center; justify-content: center;
          position: relative;
        }
        .login-bg { position: fixed; inset: 0; z-index: 0; pointer-events: none; }
        .login-box {
          position: relative; z-index: 1;
          background: var(--surface); border: 1px solid var(--border);
          border-radius: 20px; padding: 40px;
          width: 100%; max-width: 360px;
          box-shadow: 0 40px 80px rgba(0,0,0,0.6);
        }
        .login-logo {
          font-family: var(--font-sans); font-size: 32px; font-weight: 700;
          letter-spacing: -1px; text-align: center; margin-bottom: 4px;
        }
        .login-logo-s { color: var(--accent); }
        .login-sub {
          text-align: center; font-size: 13px; color: var(--text-muted);
          font-family: var(--font-mono); margin-bottom: 32px;
          text-transform: uppercase; letter-spacing: 0.08em;
        }
        .login-form { display: flex; flex-direction: column; gap: 16px; }
        .login-label {
          display: block; font-family: var(--font-mono); font-size: 11px;
          text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted);
          margin-bottom: 8px;
        }
        .login-input-wrap { position: relative; }
        .login-input-icon {
          position: absolute; left: 14px; top: 50%; transform: translateY(-50%);
          color: var(--text-dim); pointer-events: none;
        }
        .login-input {
          width: 100%; background: var(--bg); border: 1px solid var(--border);
          border-radius: 10px; padding: 13px 16px 13px 42px;
          color: var(--text); font-size: 15px; font-family: var(--font-body);
          outline: none; transition: border-color 0.2s; letter-spacing: 0.05em;
        }
        .login-input:focus { border-color: var(--accent); }
        .login-input--error { border-color: #ff4444; }
        .login-error {
          display: flex; align-items: center; gap: 8px;
          background: rgba(255,68,68,0.1); border: 1px solid rgba(255,68,68,0.25);
          color: #ff6666; font-size: 13px; padding: 10px 14px; border-radius: 9px;
        }
        .login-btn {
          display: flex; align-items: center; justify-content: center; gap: 10px;
          background: var(--accent); color: #000;
          border: none; border-radius: 10px; padding: 14px;
          font-family: var(--font-sans); font-size: 15px; font-weight: 700;
          cursor: pointer; transition: opacity 0.2s, transform 0.2s;
          margin-top: 4px;
        }
        .login-btn:hover:not(:disabled) { opacity: 0.88; transform: translateY(-1px); }
        .login-btn:disabled { opacity: 0.4; cursor: not-allowed; }
        .spinner {
          width: 15px; height: 15px; border-radius: 50%;
          border: 2px solid rgba(0,0,0,0.3); border-top-color: #000;
          animation: spin 0.7s linear infinite; flex-shrink: 0;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  )
}
