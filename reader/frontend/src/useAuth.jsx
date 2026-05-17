import { createContext, useContext, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('scryll_token'))

  const login = useCallback((t) => {
    localStorage.setItem('scryll_token', t)
    setToken(t)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('scryll_token')
    setToken(null)
  }, [])

  const authFetch = useCallback((url, opts = {}) => {
    const headers = { ...opts.headers }
    if (token) headers['Authorization'] = `Bearer ${token}`
    return fetch(url, { ...opts, headers }).then(res => {
      if (res.status === 401 || res.status === 403) {
        localStorage.removeItem('scryll_token')
        setToken(null)
      }
      return res
    })
  }, [token])

  return (
    <AuthContext.Provider value={{ token, login, logout, authFetch }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
