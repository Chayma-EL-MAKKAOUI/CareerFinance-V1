'use client'

import { useState } from 'react'
import Link from 'next/link'
<<<<<<< HEAD
import { usePathname } from 'next/navigation'
import { Menu, X, User, LogOut, BarChart3, History, Home } from 'lucide-react'

export default function SimpleNavbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const pathname = usePathname()
=======
import { usePathname, useRouter } from 'next/navigation'
import { Menu, X, User, LogOut, BarChart3, History, Home, ChevronDown } from 'lucide-react'
import { useAuth } from '../../lib/useAuth'

export default function SimpleNavbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)
  const pathname = usePathname()
  const router = useRouter()
  const { user, isLoggedIn, logout } = useAuth()
>>>>>>> 5e0de77 (Auth commit)

  const navigation = [
    { name: 'Accueil', href: '/', icon: Home },
    { name: 'Dashboard', href: '/dashboard', icon: BarChart3 },
    { name: 'Historique', href: '/historique', icon: History },
  ]

  const isActive = (href: string) => {
    if (href === '/') {
      return pathname === '/'
    }
    return pathname.startsWith(href)
  }

<<<<<<< HEAD
=======
  const handleLogout = async () => {
    try {
      await logout()
      router.push('/')
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error)
    }
  }

>>>>>>> 5e0de77 (Auth commit)
  return (
    <nav className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md shadow-xl border-b border-white/20 dark:border-gray-700/20 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo et navigation principale */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-3 group">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-cyan-400 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl group-hover:scale-110 transition-all duration-300">
                <span className="text-white font-bold text-lg">CF</span>
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-gray-900 to-purple-600 dark:from-white dark:to-purple-400 bg-clip-text text-transparent">
                CareerFinance AI
              </span>
            </Link>

            {/* Navigation desktop */}
            <div className="hidden md:ml-10 md:flex md:space-x-8">
              {navigation.map((item) => {
                const Icon = item.icon
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 ${
                      isActive(item.href)
                        ? 'text-purple-600 dark:text-purple-400 bg-gradient-to-r from-purple-50 to-cyan-50 dark:from-purple-900/30 dark:to-cyan-900/30 shadow-md'
                        : 'text-gray-600 dark:text-gray-300 hover:text-purple-600 dark:hover:text-purple-400 hover:bg-white/70 dark:hover:bg-gray-800/70 hover:shadow-md hover:scale-105'
                    }`}
                  >
                    <Icon size={16} />
                    <span>{item.name}</span>
                  </Link>
                )
              })}
            </div>
          </div>

          {/* Actions utilisateur */}
          <div className="flex items-center space-x-4">
<<<<<<< HEAD
            <div className="flex items-center space-x-3">
              <Link
                href="/auth/login"
                className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white px-4 py-2 rounded-xl text-sm font-medium hover:bg-white/70 dark:hover:bg-gray-800/70 hover:shadow-md transition-all duration-200"
              >
                Connexion
              </Link>
              <Link
                href="/auth/register"
                className="bg-gradient-to-r from-purple-500 to-cyan-400 text-white px-6 py-2 rounded-xl text-sm font-medium hover:shadow-xl hover:shadow-purple-500/25 hover:scale-105 transition-all duration-300"
              >
                S'inscrire
              </Link>
            </div>
=======
            {isLoggedIn ? (
              <div className="relative">
                {/* Menu utilisateur desktop */}
                <button
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                  className="hidden md:flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-purple-600 dark:hover:text-purple-400 hover:bg-white/70 dark:hover:bg-gray-800/70 hover:shadow-md transition-all duration-200"
                >
                  <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-cyan-400 rounded-full flex items-center justify-center">
                    <span className="text-white font-medium text-sm">
                      {(user as any)?.first_name?.[0] || (user as any)?.username?.[0] || 'U'}
                    </span>
                  </div>
                  <span className="hidden lg:block">
                    {(user as any)?.first_name || (user as any)?.username || 'Utilisateur'}
                  </span>
                  <ChevronDown size={16} className={`transition-transform duration-200 ${isUserMenuOpen ? 'rotate-180' : ''}`} />
                </button>

                {/* Menu déroulant utilisateur */}
                {isUserMenuOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 py-2 z-50">
                    <div className="px-4 py-2 border-b border-gray-200 dark:border-gray-700">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {(user as any)?.first_name} {(user as any)?.last_name}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {(user as any)?.email}
                      </p>
                    </div>
                    <Link
                      href="/dashboard"
                      className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                      onClick={() => setIsUserMenuOpen(false)}
                    >
                      Dashboard
                    </Link>
                    <Link
                      href="/historique"
                      className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                      onClick={() => setIsUserMenuOpen(false)}
                    >
                      Historique
                    </Link>
                    <button
                      onClick={() => {
                        setIsUserMenuOpen(false)
                        handleLogout()
                      }}
                      className="block w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30"
                    >
                      <div className="flex items-center space-x-2">
                        <LogOut size={16} />
                        <span>Déconnexion</span>
                      </div>
                    </button>
                  </div>
                )}

                {/* Bouton utilisateur mobile */}
                <button
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                  className="md:hidden w-8 h-8 bg-gradient-to-r from-purple-500 to-cyan-400 rounded-full flex items-center justify-center"
                >
                  <span className="text-white font-medium text-sm">
                    {(user as any)?.first_name?.[0] || (user as any)?.username?.[0] || 'U'}
                  </span>
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <Link
                  href="/auth/login"
                  className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white px-4 py-2 rounded-xl text-sm font-medium hover:bg-white/70 dark:hover:bg-gray-800/70 hover:shadow-md transition-all duration-200"
                >
                  Connexion
                </Link>
                <Link
                  href="/auth/register"
                  className="bg-gradient-to-r from-purple-500 to-cyan-400 text-white px-6 py-2 rounded-xl text-sm font-medium hover:shadow-xl hover:shadow-purple-500/25 hover:scale-105 transition-all duration-300"
                >
                  S'inscrire
                </Link>
              </div>
            )}
>>>>>>> 5e0de77 (Auth commit)

            {/* Menu mobile */}
            <div className="md:hidden">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white focus:outline-none"
              >
                {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
            </div>
          </div>
        </div>

        {/* Menu mobile */}
        {isMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 border-t border-gray-200 dark:border-gray-700">
              {navigation.map((item) => {
                const Icon = item.icon
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`flex items-center space-x-2 px-3 py-2 rounded-md text-base font-medium ${
                      isActive(item.href)
                        ? 'text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/30'
                        : 'text-gray-600 dark:text-gray-300 hover:text-purple-600 dark:hover:text-purple-400 hover:bg-gray-50 dark:hover:bg-gray-800'
                    }`}
                    onClick={() => setIsMenuOpen(false)}
                  >
                    <Icon size={16} />
                    <span>{item.name}</span>
                  </Link>
                )
              })}
              
<<<<<<< HEAD
              <div className="pt-4 border-t border-gray-200 dark:border-gray-700 space-y-2">
                <Link
                  href="/auth/login"
                  className="block px-3 py-2 text-base font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Connexion
                </Link>
                <Link
                  href="/auth/register"
                  className="block px-3 py-2 text-base font-medium bg-gradient-to-r from-purple-500 to-cyan-400 text-white rounded-md"
                  onClick={() => setIsMenuOpen(false)}
                >
                  S'inscrire
                </Link>
              </div>
=======
              {isLoggedIn ? (
                <div className="pt-4 border-t border-gray-200 dark:border-gray-700 space-y-2">
                  <div className="px-3 py-2">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {(user as any)?.first_name} {(user as any)?.last_name}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {(user as any)?.email}
                    </p>
                  </div>
                  <Link
                    href="/dashboard"
                    className="block px-3 py-2 text-base font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Dashboard
                  </Link>
                  <Link
                    href="/historique"
                    className="block px-3 py-2 text-base font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Historique
                  </Link>
                  <button
                    onClick={() => {
                      setIsMenuOpen(false)
                      handleLogout()
                    }}
                    className="block w-full text-left px-3 py-2 text-base font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30"
                  >
                    <div className="flex items-center space-x-2">
                      <LogOut size={16} />
                      <span>Déconnexion</span>
                    </div>
                  </button>
                </div>
              ) : (
                <div className="pt-4 border-t border-gray-200 dark:border-gray-700 space-y-2">
                  <Link
                    href="/auth/login"
                    className="block px-3 py-2 text-base font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Connexion
                  </Link>
                  <Link
                    href="/auth/register"
                    className="block px-3 py-2 text-base font-medium bg-gradient-to-r from-purple-500 to-cyan-400 text-white rounded-md"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    S'inscrire
                  </Link>
                </div>
              )}
>>>>>>> 5e0de77 (Auth commit)
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
