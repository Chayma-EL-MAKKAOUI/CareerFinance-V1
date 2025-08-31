'use client'

import Link from 'next/link'
import {
  BarChart3,
  FileText,
  TrendingUp,
  User,
  Settings,
  History,
  Plus,
  ArrowRight,
  Calendar
} from 'lucide-react'

interface User {
  name: string
  email: string
  isLoggedIn: boolean
}

interface AnalysisStats {
  totalAnalyses: number
  bulletinAnalyses: number
  salaryAnalyses: number
  careerCoaching: number
}

export default function DashboardPage() {
  const stats = {
    totalAnalyses: 3,
    bulletinAnalyses: 2,
    salaryAnalyses: 1,
    careerCoaching: 1
  }

  const quickActions = [
    {
      title: 'Analyser un bulletin',
      description: 'Téléchargez et analysez votre bulletin de paie',
      icon: FileText,
      href: '/?tab=bulletin-paie',
      color: 'from-blue-500 to-blue-600'
    },
    {
      title: 'Analyse salariale',
      description: 'Comparez votre salaire au marché',
      icon: TrendingUp,
      href: '/?tab=analyse-salariale',
      color: 'from-green-500 to-green-600'
    },
    {
      title: 'Coaching carrière',
      description: 'Obtenez des conseils personnalisés',
      icon: BarChart3,
      href: '/?tab=coaching-carriere',
      color: 'from-purple-500 to-purple-600'
    }
  ]

  const recentActivity = [
    {
      type: 'bulletin',
      title: 'Analyse bulletin de paie',
      date: '2024-01-15',
      status: 'completed'
    },
    {
      type: 'salary',
      title: 'Analyse salariale - Développeur',
      date: '2024-01-10',
      status: 'completed'
    },
    {
      type: 'coaching',
      title: 'Plan de carrière généré',
      date: '2024-01-08',
      status: 'completed'
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* En-tête */}
        <div className="mb-12">
          <div className="flex items-center space-x-4 mb-4">
            <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-cyan-400 rounded-2xl flex items-center justify-center shadow-lg">
              <span className="text-white text-2xl">👋</span>
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 via-purple-900 to-gray-900 dark:from-white dark:via-purple-300 dark:to-white bg-clip-text text-transparent">
                Bonjour, Demo User
              </h1>
              <p className="text-gray-600 dark:text-gray-300 mt-1 text-lg">
                Voici un aperçu de votre activité sur CareerFinance AI
              </p>
            </div>
          </div>
        </div>

        {/* Statistiques */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20 dark:border-gray-700/20 hover:shadow-2xl hover:scale-105 transition-all duration-300 group">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-gray-600 dark:text-gray-300 mb-2">Total analyses</p>
                <p className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-cyan-600 bg-clip-text text-transparent">{stats.totalAnalyses}</p>
              </div>
              <div className="p-3 bg-gradient-to-r from-purple-500 to-purple-600 rounded-2xl shadow-lg group-hover:shadow-purple-500/25 group-hover:scale-110 transition-all duration-300">
                <BarChart3 className="h-7 w-7 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20 dark:border-gray-700/20 hover:shadow-2xl hover:scale-105 transition-all duration-300 group animate-slide-up">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-gray-600 dark:text-gray-300 mb-2">Bulletins analysés</p>
                <p className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">{stats.bulletinAnalyses}</p>
              </div>
              <div className="p-3 bg-gradient-to-r from-blue-500 to-blue-600 rounded-2xl shadow-lg group-hover:shadow-blue-500/25 group-hover:scale-110 transition-all duration-300">
                <FileText className="h-7 w-7 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20 dark:border-gray-700/20 hover:shadow-2xl hover:scale-105 transition-all duration-300 group">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-gray-600 dark:text-gray-300 mb-2">Analyses salariales</p>
                <p className="text-3xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">{stats.salaryAnalyses}</p>
              </div>
              <div className="p-3 bg-gradient-to-r from-green-500 to-green-600 rounded-2xl shadow-lg group-hover:shadow-green-500/25 group-hover:scale-110 transition-all duration-300">
                <TrendingUp className="h-7 w-7 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20 dark:border-gray-700/20 hover:shadow-2xl hover:scale-105 transition-all duration-300 group">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-gray-600 dark:text-gray-300 mb-2">Sessions coaching</p>
                <p className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">{stats.careerCoaching}</p>
              </div>
              <div className="p-3 bg-gradient-to-r from-orange-500 to-orange-600 rounded-2xl shadow-lg group-hover:shadow-orange-500/25 group-hover:scale-110 transition-all duration-300">
                <User className="h-7 w-7 text-white" />
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Actions rapides */}
          <div className="lg:col-span-2">
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 dark:border-gray-700/20 p-8">
              <div className="flex items-center justify-between mb-8">
                <h2 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-purple-600 dark:from-white dark:to-purple-400 bg-clip-text text-transparent">Actions rapides</h2>
                <div className="p-2 bg-gradient-to-r from-purple-500 to-cyan-400 rounded-xl">
                  <Plus className="h-5 w-5 text-white" />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {quickActions.map((action, index) => {
                  const Icon = action.icon
                  return (
                    <Link
                      key={index}
                      href={action.href}
                      className="group p-6 bg-white/70 dark:bg-gray-700/70 backdrop-blur-sm border border-white/30 dark:border-gray-600/30 rounded-2xl hover:shadow-2xl hover:scale-105 transition-all duration-300"
                    >
                      <div className={`w-14 h-14 bg-gradient-to-r ${action.color} rounded-2xl flex items-center justify-center mb-4 shadow-lg group-hover:shadow-xl group-hover:scale-110 transition-all duration-300`}>
                        <Icon className="h-7 w-7 text-white" />
                      </div>
                      <h3 className="font-semibold text-gray-900 dark:text-white mb-2 text-lg">{action.title}</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-300 mb-4 leading-relaxed">{action.description}</p>
                      <div className="flex items-center text-sm font-medium text-purple-600 dark:text-purple-400 group-hover:text-purple-700 dark:group-hover:text-purple-300">
                        <span>Commencer</span>
                        <ArrowRight className="h-4 w-4 ml-2 group-hover:translate-x-2 transition-transform duration-300" />
                      </div>
                    </Link>
                  )
                })}
              </div>
            </div>
          </div>

          {/* Activité récente et profil */}
          <div className="space-y-6">
            {/* Profil utilisateur */}
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 dark:border-gray-700/20 p-6">
              <div className="flex items-center space-x-4 mb-6">
                <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-cyan-400 rounded-2xl flex items-center justify-center shadow-lg">
                  <User className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white text-lg">Demo User</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-300">demo@example.com</p>
                  <div className="flex items-center space-x-1 mt-1">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-xs text-green-600 font-medium">En ligne</span>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <Link
                  href="/historique"
                  className="flex items-center justify-between p-3 text-sm text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gradient-to-r hover:from-purple-50 hover:to-cyan-50 dark:hover:from-purple-900/30 dark:hover:to-cyan-900/30 rounded-xl transition-all duration-200 group"
                >
                  <div className="flex items-center space-x-3">
                    <History className="h-5 w-5" />
                    <span className="font-medium">Voir l'historique</span>
                  </div>
                  <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform duration-200" />
                </Link>

                <button className="flex items-center justify-between w-full p-3 text-sm text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gradient-to-r hover:from-purple-50 hover:to-cyan-50 dark:hover:from-purple-900/30 dark:hover:to-cyan-900/30 rounded-xl transition-all duration-200 group">
                  <div className="flex items-center space-x-3">
                    <Settings className="h-5 w-5" />
                    <span className="font-medium">Paramètres</span>
                  </div>
                  <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform duration-200" />
                </button>
              </div>
            </div>

            {/* Activité récente */}
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 dark:border-gray-700/20 p-6">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-6 text-lg">Activité récente</h3>

              {recentActivity.length > 0 ? (
                <div className="space-y-4">
                  {recentActivity.map((activity, index) => (
                    <div key={index} className="flex items-center space-x-4 p-3 hover:bg-gradient-to-r hover:from-purple-50 hover:to-cyan-50 dark:hover:from-purple-900/30 dark:hover:to-cyan-900/30 rounded-xl transition-all duration-200 group">
                      <div className="w-3 h-3 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full shadow-sm"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900 dark:text-white group-hover:text-purple-700 dark:group-hover:text-purple-300 transition-colors">{activity.title}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{new Date(activity.date).toLocaleDateString('fr-FR')}</p>
                      </div>
                      <div className="w-2 h-2 bg-purple-400 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="w-12 h-12 bg-gradient-to-r from-gray-200 to-gray-300 rounded-2xl flex items-center justify-center mx-auto mb-3">
                    <Calendar className="h-6 w-6 text-gray-400" />
                  </div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Aucune activité récente
                  </p>
                </div>
              )}

              <Link
                href="/historique"
                className="block text-center text-sm font-medium text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 mt-6 pt-4 border-t border-gray-200/50 dark:border-gray-700/50 hover:bg-gradient-to-r hover:from-purple-50 hover:to-cyan-50 dark:hover:from-purple-900/30 dark:hover:to-cyan-900/30 rounded-xl py-2 transition-all duration-200"
              >
                Voir tout l'historique
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
