'use client'

import { useAuth } from '../../lib/useAuth'

export default function AuthDebug() {
  const { user, isLoading, isLoggedIn, logout } = useAuth()

  return (
    <div className="fixed top-4 right-4 bg-white/90 backdrop-blur-sm rounded-lg p-4 shadow-lg border border-gray-200 z-50 max-w-sm">
      <h3 className="font-semibold text-gray-900 mb-2">Debug Auth</h3>
      <div className="space-y-2 text-sm">
        <div>
          <span className="font-medium">Loading:</span> {isLoading ? 'true' : 'false'}
        </div>
        <div>
          <span className="font-medium">Logged In:</span> {isLoggedIn ? 'true' : 'false'}
        </div>
        <div>
          <span className="font-medium">User:</span> {user ? JSON.stringify(user) : 'null'}
        </div>
        <div>
          <span className="font-medium">Token:</span> {typeof window !== 'undefined' ? localStorage.getItem('auth_token') || 'null' : 'null'}
        </div>
        {isLoggedIn && (
          <button
            onClick={logout}
            className="w-full bg-red-500 text-white px-3 py-1 rounded text-xs hover:bg-red-600 transition-colors"
          >
            Déconnexion
          </button>
        )}
      </div>
    </div>
  )
}
