'use client'

import { useState } from 'react'
import { useAuth } from '../../lib/useAuth'
import AuthDebug from '../../components/Auth/AuthDebug'

interface User {
  id: number
  email: string
  name: string
}

export default function AuthTestPage() {
  const { login, logout, user, isLoading, isLoggedIn } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage('Connexion en cours...')
    
    try {
      const result = await login(email, password)
      if (result.success) {
        setMessage('Connexion réussie !')
      } else {
        setMessage(`Erreur: ${result.error}`)
      }
    } catch (error) {
      setMessage(`Erreur: ${error}`)
    }
  }

  const handleLogout = () => {
    logout()
    setMessage('Déconnexion effectuée')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 p-6">
      <AuthDebug />
      
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-8">Test d'Authentification</h1>
        
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
                  disabled={isLoading}
                  className="w-full bg-gradient-to-r from-purple-500 to-cyan-400 text-white py-3 rounded-lg hover:shadow-lg transition-all disabled:opacity-50"
                >
                  {isLoading ? 'Connexion...' : 'Se connecter'}
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
                    <li>Loading: {isLoading ? 'Oui' : 'Non'}</li>
                    <li>Connecté: {isLoggedIn ? 'Oui' : 'Non'}</li>
                    <li>Utilisateur: {(user as User | null)?.email || 'Aucun'}</li>
                  </ul>
                </div>

                {isLoggedIn && (
                  <button
                    onClick={handleLogout}
                    className="w-full bg-red-500 text-white py-3 rounded-lg hover:bg-red-600 transition-colors"
                  >
                    Se déconnecter
                  </button>
                )}

                <div className="bg-blue-50 p-4 rounded-lg">
                  <h3 className="font-semibold mb-2">Message:</h3>
                  <p className="text-sm">{message || 'Aucun message'}</p>
                </div>

                <div className="bg-green-50 p-4 rounded-lg">
                  <h3 className="font-semibold mb-2">Test rapide:</h3>
                  <button
                    onClick={() => {
                      setEmail('test@example.com')
                      setPassword('password123')
                    }}
                    className="bg-green-500 text-white px-4 py-2 rounded text-sm hover:bg-green-600 transition-colors"
                  >
                    Remplir formulaire
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
