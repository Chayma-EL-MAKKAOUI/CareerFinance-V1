'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import {
  FileText,
  TrendingUp,
  BarChart3,
  Trash2,
  Download,
  Calendar,
  Filter,
  Search,
  AlertTriangle,
  History
} from 'lucide-react'


interface AnalysisItem {
  id: string
  type: 'bulletin' | 'salary' | 'coaching'
  title: string
  date: string
  status: 'completed' | 'processing' | 'failed'
  description: string
  fileSize?: string
}

export default function HistoriquePage() {
  const [analyses, setAnalyses] = useState<AnalysisItem[]>([])
  const [filteredAnalyses, setFilteredAnalyses] = useState<AnalysisItem[]>([])
  const [selectedItems, setSelectedItems] = useState<string[]>([])
  const [filterType, setFilterType] = useState<string>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [itemToDelete, setItemToDelete] = useState<string | null>(null)
  useEffect(() => {

    // Charger l'historique (simulation avec données d'exemple)
    const mockAnalyses: AnalysisItem[] = [
      {
        id: '1',
        type: 'bulletin',
        title: 'Bulletin de paie - Janvier 2024',
        date: '2024-01-15',
        status: 'completed',
        description: 'Analyse complète du bulletin de paie avec détection des anomalies',
        fileSize: '2.3 MB'
      },
      {
        id: '2',
        type: 'salary',
        title: 'Analyse salariale - Développeur Full-Stack',
        date: '2024-01-10',
        status: 'completed',
        description: 'Comparaison salariale pour le poste de Développeur Full-Stack à Casablanca'
      },
      {
        id: '3',
        type: 'coaching',
        title: 'Plan de carrière - Évolution vers Tech Lead',
        date: '2024-01-08',
        status: 'completed',
        description: 'Plan de développement professionnel avec étapes et recommandations'
      },
      {
        id: '4',
        type: 'bulletin',
        title: 'Bulletin de paie - Décembre 2023',
        date: '2023-12-20',
        status: 'completed',
        description: 'Analyse du bulletin de paie avec calcul des primes de fin d\'année',
        fileSize: '1.8 MB'
      },
      {
        id: '5',
        type: 'salary',
        title: 'Analyse salariale - Data Scientist',
        date: '2023-12-15',
        status: 'processing',
        description: 'Analyse en cours pour le poste de Data Scientist'
      }
    ]

    setAnalyses(mockAnalyses)
    setFilteredAnalyses(mockAnalyses)
  }, [])

  useEffect(() => {
    // Filtrer les analyses
    let filtered = analyses

    if (filterType !== 'all') {
      filtered = filtered.filter(item => item.type === filterType)
    }

    if (searchTerm) {
      filtered = filtered.filter(item => 
        item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.description.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    setFilteredAnalyses(filtered)
  }, [analyses, filterType, searchTerm])

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'bulletin':
        return FileText
      case 'salary':
        return TrendingUp
      case 'coaching':
        return BarChart3
      default:
        return FileText
    }
  }

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'bulletin':
        return 'Bulletin de paie'
      case 'salary':
        return 'Analyse salariale'
      case 'coaching':
        return 'Coaching carrière'
      default:
        return 'Analyse'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'processing':
        return 'bg-yellow-100 text-yellow-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Terminé'
      case 'processing':
        return 'En cours'
      case 'failed':
        return 'Échec'
      default:
        return 'Inconnu'
    }
  }

  const handleSelectItem = (id: string) => {
    setSelectedItems(prev => 
      prev.includes(id) 
        ? prev.filter(item => item !== id)
        : [...prev, id]
    )
  }

  const handleSelectAll = () => {
    if (selectedItems.length === filteredAnalyses.length) {
      setSelectedItems([])
    } else {
      setSelectedItems(filteredAnalyses.map(item => item.id))
    }
  }

  const handleDeleteSingle = (id: string) => {
    setItemToDelete(id)
    setShowDeleteModal(true)
  }

  const handleDeleteSelected = () => {
    if (selectedItems.length > 0) {
      setItemToDelete('multiple')
      setShowDeleteModal(true)
    }
  }

  const confirmDelete = () => {
    if (itemToDelete === 'multiple') {
      setAnalyses(prev => prev.filter(item => !selectedItems.includes(item.id)))
      setSelectedItems([])
    } else if (itemToDelete) {
      setAnalyses(prev => prev.filter(item => item.id !== itemToDelete))
    }
    setShowDeleteModal(false)
    setItemToDelete(null)
  }



  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* En-tête */}
        <div className="mb-12">
          <div className="flex items-center space-x-4 mb-4">
            <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-cyan-400 rounded-2xl flex items-center justify-center shadow-lg">
              <History className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 via-purple-900 to-gray-900 dark:from-white dark:via-purple-300 dark:to-white bg-clip-text text-transparent">
                Historique des analyses
              </h1>
              <p className="text-gray-600 dark:text-gray-300 mt-1 text-lg">
                Consultez et gérez toutes vos analyses précédentes
              </p>
            </div>
          </div>
        </div>

        {/* Filtres et recherche */}
        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 dark:border-gray-700/20 p-6 mb-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
            <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4">
              {/* Recherche */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 dark:text-gray-500" />
                <input
                  type="text"
                  placeholder="Rechercher..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-3 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white/70 dark:bg-gray-700/70 backdrop-blur-sm transition-all duration-200 hover:shadow-md text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                />
              </div>

              {/* Filtre par type */}
              <div className="relative">
                <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 dark:text-gray-500" />
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="pl-10 pr-8 py-3 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white/70 dark:bg-gray-700/70 backdrop-blur-sm transition-all duration-200 hover:shadow-md text-gray-900 dark:text-white"
                >
                  <option value="all">Tous les types</option>
                  <option value="bulletin">Bulletins de paie</option>
                  <option value="salary">Analyses salariales</option>
                  <option value="coaching">Coaching carrière</option>
                </select>
              </div>
            </div>

            {/* Actions */}
            <div className="flex space-x-2">
              {selectedItems.length > 0 && (
                <button
                  onClick={handleDeleteSelected}
                  className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-xl hover:shadow-xl hover:shadow-red-500/25 hover:scale-105 transition-all duration-300 transform"
                >
                  <Trash2 className="h-4 w-4" />
                  <span>Supprimer ({selectedItems.length})</span>
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Liste des analyses */}
        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 dark:border-gray-700/20">
          {filteredAnalyses.length > 0 ? (
            <>
              {/* En-tête du tableau */}
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={selectedItems.length === filteredAnalyses.length && filteredAnalyses.length > 0}
                    onChange={handleSelectAll}
                    className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 dark:border-gray-600 rounded"
                  />
                  <span className="ml-3 text-sm font-medium text-gray-900 dark:text-white">
                    Sélectionner tout ({filteredAnalyses.length})
                  </span>
                </div>
              </div>

              {/* Liste */}
              <div className="divide-y divide-gray-200">
                {filteredAnalyses.map((item) => {
                  const Icon = getTypeIcon(item.type)
                  return (
                    <div key={item.id} className="px-6 py-4 hover:bg-gradient-to-r hover:from-purple-50 hover:to-cyan-50 transition-all duration-200 group">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <input
                            type="checkbox"
                            checked={selectedItems.includes(item.id)}
                            onChange={() => handleSelectItem(item.id)}
                            className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 dark:border-gray-600 rounded"
                          />

                          <div className="flex items-center space-x-3">
                            <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg">
                              <Icon className="h-5 w-5 text-gray-600 dark:text-gray-300" />
                            </div>

                            <div>
                              <h3 className="text-sm font-medium text-gray-900 dark:text-white">{item.title}</h3>
                              <p className="text-sm text-gray-500 dark:text-gray-400">{item.description}</p>
                              <div className="flex items-center space-x-4 mt-1">
                                <span className="text-xs text-gray-400 dark:text-gray-500 flex items-center">
                                  <Calendar className="h-3 w-3 mr-1" />
                                  {new Date(item.date).toLocaleDateString('fr-FR')}
                                </span>
                                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                                  {getStatusLabel(item.status)}
                                </span>
                                <span className="text-xs text-gray-400 dark:text-gray-500">{getTypeLabel(item.type)}</span>
                                {item.fileSize && (
                                  <span className="text-xs text-gray-400 dark:text-gray-500">{item.fileSize}</span>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center space-x-2">
                          {item.status === 'completed' && (
                            <>
                              <button className="p-2 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700">
                                <Download className="h-4 w-4" />
                              </button>
                            </>
                          )}
                          <button
                            onClick={() => handleDeleteSingle(item.id)}
                            className="p-2 text-gray-400 dark:text-gray-500 hover:text-red-600 dark:hover:text-red-400 rounded-md hover:bg-red-50 dark:hover:bg-red-900/20"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </>
          ) : (
            <div className="px-6 py-12 text-center">
              <FileText className="h-12 w-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Aucune analyse trouvée</h3>
              <p className="text-gray-500 dark:text-gray-400 mb-6">
                {searchTerm || filterType !== 'all'
                  ? 'Aucun résultat ne correspond à vos critères de recherche.'
                  : 'Vous n\'avez pas encore effectué d\'analyses.'
                }
              </p>
              {!searchTerm && filterType === 'all' && (
                <button
                  onClick={() => router.push('/')}
                  className="bg-gradient-to-r from-purple-500 to-cyan-400 text-white px-6 py-2 rounded-md hover:shadow-lg transition-all"
                >
                  Commencer une analyse
                </button>
              )}
            </div>
          )}
        </div>

        {/* Modal de confirmation de suppression */}
        {showDeleteModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-full">
                  <AlertTriangle className="h-6 w-6 text-red-600 dark:text-red-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">Confirmer la suppression</h3>
              </div>

              <p className="text-gray-600 dark:text-gray-300 mb-6">
                {itemToDelete === 'multiple'
                  ? `Êtes-vous sûr de vouloir supprimer ${selectedItems.length} analyse(s) ? Cette action est irréversible.`
                  : 'Êtes-vous sûr de vouloir supprimer cette analyse ? Cette action est irréversible.'
                }
              </p>

              <div className="flex space-x-3 justify-end">
                <button
                  onClick={() => setShowDeleteModal(false)}
                  className="px-4 py-2 text-gray-600 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  Annuler
                </button>
                <button
                  onClick={confirmDelete}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                >
                  Supprimer
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
