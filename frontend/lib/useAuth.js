// Hook d'authentification simple
import { useState, useEffect } from 'react'

export function useAuth() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulation d'une vérification d'auth
    const checkAuth = () => {
      const token = localStorage.getItem('auth_token')
      if (token) {
        setUser({ id: 1, email: 'user@example.com' })
      }
      setLoading(false)
    }

    checkAuth()
  }, [])

  const login = async (email, password) => {
    // Simulation de login
    localStorage.setItem('auth_token', 'fake_token')
    setUser({ id: 1, email })
    return { success: true }
  }

  const register = async (email, password) => {
    // Simulation de register
    localStorage.setItem('auth_token', 'fake_token')
    setUser({ id: 1, email })
    return { success: true }
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    setUser(null)
  }

  const isLoggedIn = !!user

  return {
    user,
    loading,
    isLoggedIn,
    login,
    register,
    logout
  }
}
