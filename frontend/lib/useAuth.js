<<<<<<< HEAD
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
=======
// Hook d'authentification avec Supabase
import { useState, useEffect } from 'react'

// ✅ CORRECTION: URL corrigée pour pointer vers Next.js (port 3001)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001'

export function useAuth() {
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Vérification d'authentification au chargement
    const checkAuth = async () => {
      try {
        console.log('🔍 useAuth - Vérification d\'authentification...')
        const token = localStorage.getItem('auth_token')
        console.log('🔍 useAuth - Token trouvé:', token ? 'Oui' : 'Non')
        
        if (token) {
          // Vérifier le token avec le backend avec timeout
          const controller = new AbortController()
          const timeoutId = setTimeout(() => controller.abort(), 5000) // 5 secondes de timeout
          
          try {
            const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              },
              signal: controller.signal
            })
            
            clearTimeout(timeoutId)
            
            // ✅ CORRECTION: Vérifier le content-type avant de parser JSON
            const contentType = response.headers.get('content-type')
            if (!contentType || !contentType.includes('application/json')) {
              console.error('❌ useAuth - Réponse non-JSON reçue:', await response.text())
              localStorage.removeItem('auth_token')
              setUser(null)
              return
            }
            
            if (response.ok) {
              const userData = await response.json()
              setUser(userData)
              console.log('✅ useAuth - Utilisateur connecté:', userData)
            } else {
              // Token invalide, le supprimer
              localStorage.removeItem('auth_token')
              setUser(null)
              console.log('❌ useAuth - Token invalide, supprimé')
            }
          } catch (fetchError) {
            clearTimeout(timeoutId)
            if (fetchError.name === 'AbortError') {
              console.warn('⚠️ useAuth - Timeout lors de la vérification du token')
            } else if (fetchError instanceof SyntaxError) {
              console.error('❌ useAuth - Erreur de parsing JSON (probablement HTML reçu):', fetchError.message)
            } else {
              console.error('❌ useAuth - Erreur réseau lors de la vérification:', fetchError)
            }
            // En cas d'erreur réseau, supprimer le token pour forcer une nouvelle connexion
            localStorage.removeItem('auth_token')
            setUser(null)
          }
        } else {
          // Pas de token, utilisateur non connecté
          setUser(null)
          console.log('🔍 useAuth - Aucun utilisateur connecté')
        }
      } catch (error) {
        console.error('❌ useAuth - Erreur lors de la vérification d\'authentification:', error)
        setUser(null)
      } finally {
        setIsLoading(false)
        console.log('✅ useAuth - Chargement terminé, isLoading = false')
      }
>>>>>>> 5e0de77 (Auth commit)
    }

    checkAuth()
  }, [])

  const login = async (email, password) => {
<<<<<<< HEAD
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
=======
    try {
      console.log('🔍 useAuth - Tentative de connexion avec:', email)
      
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 10000) // 10 secondes de timeout
      
      try {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ email, password }),
          signal: controller.signal
        })
        
        clearTimeout(timeoutId)
        
        // ✅ CORRECTION: Vérifier le content-type avant de parser JSON
        const contentType = response.headers.get('content-type')
        if (!contentType || !contentType.includes('application/json')) {
          const htmlResponse = await response.text()
          console.error('❌ useAuth - Réponse HTML reçue au lieu de JSON:', htmlResponse)
          return { success: false, error: 'Erreur de configuration du serveur - route API introuvable' }
        }
        
        const data = await response.json()
        
        if (response.ok && data.success) {
          // Connexion réussie
          localStorage.setItem('auth_token', data.access_token)
          setUser(data.user)
          console.log('✅ useAuth - Connexion réussie:', data.user)
          return { success: true, user: data.user }
        } else {
          // Erreur de connexion
          console.log('❌ useAuth - Erreur de connexion:', data.detail || data.error)
          return { success: false, error: data.detail || data.error || 'Email ou mot de passe incorrect' }
        }
      } catch (fetchError) {
        clearTimeout(timeoutId)
        if (fetchError.name === 'AbortError') {
          return { success: false, error: 'Délai d\'attente dépassé. Vérifiez votre connexion.' }
        }
        if (fetchError instanceof SyntaxError) {
          console.error('❌ useAuth - Erreur de parsing JSON:', fetchError.message)
          return { success: false, error: 'Erreur de configuration du serveur' }
        }
        throw fetchError
      }
    } catch (error) {
      console.error('❌ useAuth - Erreur lors de la connexion:', error)
      return { success: false, error: 'Erreur de connexion au serveur' }
    }
  }

  const register = async (userData) => {
    try {
      console.log('🔍 useAuth - Tentative d\'inscription avec:', userData.email)
      console.log('🚀 useAuth - URL utilisée:', `${API_BASE_URL}/api/auth/register`)
      
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 10000) // 10 secondes de timeout
      
      try {
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(userData),
          signal: controller.signal
        })
        
        clearTimeout(timeoutId)
        
        console.log('📡 useAuth - Response status:', response.status)
        console.log('📡 useAuth - Response ok:', response.ok)
        
        // ✅ CORRECTION: Vérifier le content-type avant de parser JSON
        const contentType = response.headers.get('content-type')
        if (!contentType || !contentType.includes('application/json')) {
          const htmlResponse = await response.text()
          console.error('❌ useAuth - Réponse HTML reçue au lieu de JSON:', htmlResponse)
          return { success: false, error: 'Erreur de configuration du serveur - route API introuvable' }
        }
        
        const data = await response.json()
        console.log('📦 useAuth - Response data:', data)
        
        if (response.ok && data.success) {
          // Inscription réussie
          localStorage.setItem('auth_token', data.access_token)
          setUser(data.user)
          console.log('✅ useAuth - Inscription réussie:', data.user)
          return { success: true, user: data.user }
        } else {
          // Erreur d'inscription
          console.log('❌ useAuth - Erreur d\'inscription:', data.detail || data.error)
          return { success: false, error: data.detail || data.error || 'Erreur lors de l\'inscription' }
        }
      } catch (fetchError) {
        clearTimeout(timeoutId)
        if (fetchError.name === 'AbortError') {
          return { success: false, error: 'Délai d\'attente dépassé. Vérifiez votre connexion.' }
        }
        if (fetchError instanceof SyntaxError) {
          console.error('❌ useAuth - Erreur de parsing JSON:', fetchError.message)
          return { success: false, error: 'Erreur de configuration du serveur' }
        }
        console.error('💥 useAuth - Fetch error:', fetchError)
        throw fetchError
      }
    } catch (error) {
      console.error('❌ useAuth - Erreur lors de l\'inscription:', error)
      return { success: false, error: 'Erreur de connexion au serveur' }
    }
  }

  const logout = async () => {
    try {
      console.log('🔍 useAuth - Déconnexion...')
      const token = localStorage.getItem('auth_token')
      
      if (token) {
        // Appeler l'API de déconnexion avec timeout
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 5000) // 5 secondes de timeout
        
        try {
          await fetch(`${API_BASE_URL}/api/auth/logout`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            signal: controller.signal
          })
          clearTimeout(timeoutId)
        } catch (fetchError) {
          clearTimeout(timeoutId)
          console.warn('⚠️ useAuth - Erreur lors de l\'appel API de déconnexion:', fetchError)
        }
      }
      
      // Supprimer le token localement
      localStorage.removeItem('auth_token')
      setUser(null)
      console.log('✅ useAuth - Déconnexion réussie')
      return { success: true }
    } catch (error) {
      console.error('❌ useAuth - Erreur lors de la déconnexion:', error)
      return { success: false, error: error.message }
    }
>>>>>>> 5e0de77 (Auth commit)
  }

  const isLoggedIn = !!user

<<<<<<< HEAD
  return {
    user,
    loading,
=======
  // Log de l'état actuel
  console.log('🔍 useAuth - État actuel:', {
    isLoading,
    isLoggedIn,
    user: user ? { id: user.id, email: user.email } : null,
    API_BASE_URL // ✅ Ajouté pour debug
  })

  return {
    user,
    isLoading,
>>>>>>> 5e0de77 (Auth commit)
    isLoggedIn,
    login,
    register,
    logout
  }
<<<<<<< HEAD
}
=======
}
>>>>>>> 5e0de77 (Auth commit)
