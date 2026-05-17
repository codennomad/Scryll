import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './useAuth'
import Home from './pages/Home'
import Series from './pages/Series'
import Reader from './pages/Reader'
import Login from './pages/Login'

function PrivateRoute({ children }) {
  const { token } = useAuth()
  return token ? children : <Navigate to="/login" replace />
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<PrivateRoute><Home /></PrivateRoute>} />
      <Route path="/series/:name" element={<PrivateRoute><Series /></PrivateRoute>} />
      <Route path="/read/:name/:chapter" element={<PrivateRoute><Reader /></PrivateRoute>} />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  )
}
