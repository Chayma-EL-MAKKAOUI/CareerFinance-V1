'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import AuthGuard from '../../components/Auth/AuthGuard'

export default function TestAuthPage() {
  const [token, setToken] = useState<string | null>(null)
  const router = useRouter()

  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token')
    setToken(storedToken)
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    setToken(null)
    router.push('/auth/login')
  }

  return (
    <AuthGuard>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-xl">
            <h1 className="text-3xl font-bold text-center mb-8">Test d'Authentification</h1>
            
            <div className="space-y-6">
              <div className="bg-green-50 p-6 rounded-xl border border-green-200">
                <h2 className="text-xl font-semibold text-green-800 mb-4">✅ Authentification Réussie</h2>
                <p className="text-green-700 mb-4">
                  Cette page est protégée et vous y avez accès car vous êtes connecté.
                </p>
                <div className="bg-white p-4 rounded-lg">
                  <p className="text-sm font-medium text-gray-700">Token actuel:</p>
                  <p className="text-xs text-gray-500 font-mono break-all mt-1">
                    {token || 'Aucun token'}
                  </p>
                </div>
              </div>

              <div className="bg-blue-50 p-6 rounded-xl border border-blue-200">
                <h2 className="text-xl font-semibold text-blue-800 mb-4">🔒 Protection Active</h2>
                <p className="text-blue-700 mb-4">
                  Cette page utilise le composant AuthGuard qui vérifie automatiquement l'authentification.
                </p>
                <ul className="text-blue-700 text-sm space-y-2">
                  <li>• Vérification du token dans localStorage</li>
                  <li>• Redirection automatique si non connecté</li>
                  <li>• Affichage du contenu uniquement si authentifié</li>
                </ul>
              </div>

              <div className="bg-purple-50 p-6 rounded-xl border border-purple-200">
                <h2 className="text-xl font-semibold text-purple-800 mb-4">🧪 Test de Fonctionnalités</h2>
                <div className="space-y-4">
                  <button
                    onClick={() => router.push('/')}
                    className="w-full bg-purple-500 text-white py-3 rounded-lg hover:bg-purple-600 transition-colors"
                  >
                    Aller à la page principale
                  </button>
                  <button
                    onClick={() => router.push('/dashboard')}
                    className="w-full bg-blue-500 text-white py-3 rounded-lg hover:bg-blue-600 transition-colors"
                  >
                    Aller au dashboard
                  </button>
                  <button
                    onClick={() => router.push('/analyse-salariale')}
                    className="w-full bg-green-500 text-white py-3 rounded-lg hover:bg-green-600 transition-colors"
                  >
                    Aller à l'analyse salariale
                  </button>
                  <button
                    onClick={() => router.push('/coaching-carriere')}
                    className="w-full bg-orange-500 text-white py-3 rounded-lg hover:bg-orange-600 transition-colors"
                  >
                    Aller au coaching carrière
                  </button>
                </div>
              </div>

              <div className="bg-red-50 p-6 rounded-xl border border-red-200">
                <h2 className="text-xl font-semibold text-red-800 mb-4">🚪 Déconnexion</h2>
                <p className="text-red-700 mb-4">
                  Testez la déconnexion pour voir la protection en action.
                </p>
                <button
                  onClick={handleLogout}
                  className="w-full bg-red-500 text-white py-3 rounded-lg hover:bg-red-600 transition-colors"
                >
                  Se déconnecter
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AuthGuard>
  )
}
