'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

interface ProtectedRouteSimpleProps {
  children: React.ReactNode
  redirectTo?: string
}

export default function ProtectedRouteSimple({ children, redirectTo = '/auth/login' }: ProtectedRouteSimpleProps) {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  useEffect(() => {
    console.log('🔒 ProtectedRouteSimple - Vérification de l\'authentification...')
    
    // Vérifier directement le localStorage
    const token = localStorage.getItem('auth_token')
    console.log('🔒 ProtectedRouteSimple - Token trouvé:', token ? 'Oui' : 'Non')
    
    if (token) {
      setIsLoggedIn(true)
      console.log('🔒 ProtectedRouteSimple - Utilisateur connecté')
    } else {
      setIsLoggedIn(false)
      console.log('🔒 ProtectedRouteSimple - Utilisateur non connecté')
    }
    
    setIsLoading(false)
  }, [])

  useEffect(() => {
    console.log('🔒 ProtectedRouteSimple - useEffect redirection:', { isLoading, isLoggedIn })
    
    if (!isLoading && !isLoggedIn) {
      console.log('🔒 ProtectedRouteSimple - Redirection vers:', redirectTo)
      router.push(redirectTo)
    }
  }, [isLoading, isLoggedIn, router, redirectTo])

  if (isLoading) {
    console.log('🔒 ProtectedRouteSimple - Affichage du loader')
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-cyan-400 rounded-2xl flex items-center justify-center mx-auto mb-4 animate-pulse">
            <span className="text-white font-bold text-2xl">CF</span>
          </div>
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Vérification de l'authentification...</p>
        </div>
      </div>
    )
  }

  if (!isLoggedIn) {
    console.log('🔒 ProtectedRouteSimple - Utilisateur non connecté, pas de rendu')
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-red-500 to-red-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-2xl">🔒</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Accès Refusé</h2>
          <p className="text-gray-600 mb-4">Vous devez être connecté pour accéder à cette page.</p>
          <button
            onClick={() => router.push(redirectTo)}
            className="bg-gradient-to-r from-purple-500 to-cyan-400 text-white px-6 py-3 rounded-lg hover:shadow-lg transition-all"
          >
            Se connecter
          </button>
        </div>
      </div>
    )
  }

  console.log('🔒 ProtectedRouteSimple - Affichage du contenu protégé')
  return <>{children}</>
}
