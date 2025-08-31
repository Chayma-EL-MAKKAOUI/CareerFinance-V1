'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function AuthTestSimplePage() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [token, setToken] = useState<string | null>(null)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const router = useRouter()

  useEffect(() => {
    // Vérifier le token au chargement
    const storedToken = localStorage.getItem('auth_token')
    setToken(storedToken)
    setIsLoggedIn(!!storedToken)
    setMessage(storedToken ? 'Token trouvé dans localStorage' : 'Aucun token trouvé')
  }, [])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage('Connexion en cours...')
    
    try {
      // Simulation de connexion
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      if (!email || !password) {
        setMessage('Email et mot de passe requis')
        return
      }
      
      // Créer un token factice
      const fakeToken = `fake_token_${Date.now()}`
      localStorage.setItem('auth_token', fakeToken)
      
      setToken(fakeToken)
      setIsLoggedIn(true)
      setMessage('Connexion réussie ! Token sauvegardé.')
    } catch (error) {
      setMessage(`Erreur: ${error}`)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    setToken(null)
    setIsLoggedIn(false)
    setMessage('Déconnexion effectuée. Token supprimé.')
  }

  const clearStorage = () => {
    localStorage.clear()
    setToken(null)
    setIsLoggedIn(false)
    setMessage('localStorage nettoyé.')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-8">Test d'Authentification Simple</h1>
        
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-xl">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Formulaire de connexion */}
            <div>
              <h2 className="text-2xl font-bold mb-4">Connexion</h2>
              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="votre@email.com"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Mot de passe
                  </label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="••••••••"
                    required
                  />
                </div>
                
                <button
                  type="submit"
                  className="w-full bg-gradient-to-r from-purple-500 to-cyan-400 text-white py-3 rounded-lg hover:shadow-lg transition-all"
                >
                  Se connecter
                </button>
              </form>
            </div>

            {/* État et actions */}
            <div>
              <h2 className="text-2xl font-bold mb-4">État</h2>
              <div className="space-y-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-semibold mb-2">État actuel:</h3>
                  <ul className="space-y-1 text-sm">
                    <li>Connecté: {isLoggedIn ? 'Oui' : 'Non'}</li>
                    <li>Token: {token ? 'Présent' : 'Absent'}</li>
                    <li>Token value: {token || 'null'}</li>
                  </ul>
                </div>

                <div className="space-y-2">
                  {isLoggedIn && (
                    <button
                      onClick={handleLogout}
                      className="w-full bg-red-500 text-white py-3 rounded-lg hover:bg-red-600 transition-colors"
                    >
                      Se déconnecter
                    </button>
                  )}

                  <button
                    onClick={clearStorage}
                    className="w-full bg-orange-500 text-white py-3 rounded-lg hover:bg-orange-600 transition-colors"
                  >
                    Nettoyer localStorage
                  </button>

                  <button
                    onClick={() => {
                      setEmail('test@example.com')
                      setPassword('password123')
                    }}
                    className="w-full bg-green-500 text-white py-3 rounded-lg hover:bg-green-600 transition-colors"
                  >
                    Remplir formulaire
                  </button>
                </div>

                <div className="bg-blue-50 p-4 rounded-lg">
                  <h3 className="font-semibold mb-2">Message:</h3>
                  <p className="text-sm">{message || 'Aucun message'}</p>
                </div>

                <div className="bg-purple-50 p-4 rounded-lg">
                  <h3 className="font-semibold mb-2">Test de navigation:</h3>
                  <div className="space-y-2">
                    <button
                      onClick={() => router.push('/test')}
                      className="w-full bg-purple-500 text-white py-2 rounded text-sm hover:bg-purple-600 transition-colors"
                    >
                      Aller à /test (protégée)
                    </button>
                    <button
                      onClick={() => router.push('/auth/login')}
                      className="w-full bg-blue-500 text-white py-2 rounded text-sm hover:bg-blue-600 transition-colors"
                    >
                      Aller à /auth/login
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
