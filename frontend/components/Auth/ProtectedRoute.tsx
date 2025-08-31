'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '../../lib/useAuth'

<<<<<<< HEAD
=======
interface User {
  id: number
  email: string
  name: string
}

>>>>>>> 5e0de77 (Auth commit)
interface ProtectedRouteProps {
  children: React.ReactNode
  redirectTo?: string
}

export default function ProtectedRoute({ children, redirectTo = '/auth/login' }: ProtectedRouteProps) {
  const { user, isLoading, isLoggedIn } = useAuth()
  const router = useRouter()

<<<<<<< HEAD
  useEffect(() => {
    if (!isLoading && !isLoggedIn) {
=======
  // Log de debug
  console.log('🔒 ProtectedRoute - État:', {
    isLoading,
    isLoggedIn,
    user: user ? { id: (user as User).id, email: (user as User).email } : null,
    redirectTo
  })

  useEffect(() => {
    console.log('🔒 ProtectedRoute - useEffect déclenché:', {
      isLoading,
      isLoggedIn,
      redirectTo
    })
    
    if (!isLoading && !isLoggedIn) {
      console.log('🔒 ProtectedRoute - Redirection vers:', redirectTo)
>>>>>>> 5e0de77 (Auth commit)
      router.push(redirectTo)
    }
  }, [isLoading, isLoggedIn, router, redirectTo])

  if (isLoading) {
<<<<<<< HEAD
=======
    console.log('🔒 ProtectedRoute - Affichage du loader')
>>>>>>> 5e0de77 (Auth commit)
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-cyan-400 rounded-2xl flex items-center justify-center mx-auto mb-4 animate-pulse">
            <span className="text-white font-bold text-2xl">CF</span>
          </div>
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Chargement...</p>
        </div>
      </div>
    )
  }

  if (!isLoggedIn) {
<<<<<<< HEAD
    return null // La redirection est gérée par useEffect
  }

=======
    console.log('🔒 ProtectedRoute - Utilisateur non connecté, pas de rendu')
    return null // La redirection est gérée par useEffect
  }

  console.log('🔒 ProtectedRoute - Affichage du contenu protégé')
>>>>>>> 5e0de77 (Auth commit)
  return <>{children}</>
}
