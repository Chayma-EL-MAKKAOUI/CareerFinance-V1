'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '../../lib/useAuth'

interface AuthGuardProps {
  children: React.ReactNode
  fallback?: React.ReactNode
}

export default function AuthGuard({ children, fallback }: AuthGuardProps) {
  const { user, isLoading, isLoggedIn } = useAuth()
  const router = useRouter()
  const [hasRedirected, setHasRedirected] = useState(false)

  useEffect(() => {
    // Éviter les redirections multiples
    if (!isLoading && !isLoggedIn && !hasRedirected) {
      setHasRedirected(true)
      // Rediriger vers la page de connexion avec l'URL de retour
      const currentPath = window.location.pathname
      router.push(`/auth/login?redirect=${encodeURIComponent(currentPath)}`)
    }
  }, [isLoading, isLoggedIn, hasRedirected, router])

  // Afficher un loader pendant la vérification d'authentification
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-cyan-400 rounded-2xl flex items-center justify-center shadow-2xl shadow-purple-500/25 mx-auto mb-4">
            <span className="text-white font-bold text-2xl">CF</span>
          </div>
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-300">Vérification de l'authentification...</p>
          {/* Message d'aide si le chargement prend trop de temps */}
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            Si le chargement prend trop de temps, vérifiez votre connexion
          </p>
        </div>
      </div>
    )
  }

  // Si l'utilisateur n'est pas connecté et qu'on a déjà redirigé, afficher le fallback ou rien
  if (!isLoggedIn && hasRedirected) {
    return fallback || null
  }

  // Si l'utilisateur est connecté, afficher le contenu protégé
  if (isLoggedIn) {
    return <>{children}</>
  }

  // État de transition - afficher un loader court
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-cyan-400 rounded-2xl flex items-center justify-center shadow-2xl shadow-purple-500/25 mx-auto mb-4">
          <span className="text-white font-bold text-2xl">CF</span>
        </div>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mx-auto"></div>
        <p className="mt-4 text-gray-600 dark:text-gray-300">Redirection...</p>
      </div>
    </div>
  )
}
