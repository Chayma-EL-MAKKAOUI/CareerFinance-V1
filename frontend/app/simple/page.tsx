'use client'
import { useState, useRef } from 'react'
import { Send } from 'lucide-react'

export default function Page() {
  const [activeTab, setActiveTab] = useState('bulletin-paie')
  const [chatMessage, setChatMessage] = useState('')
  const [statusMessage, setStatusMessage] = useState('')
  const [resultData, setResultData] = useState<any>(null)
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    setUploading(true)

    try {
      const response = await fetch('http://localhost:8000/api/documents/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Erreur lors de l\'envoi du fichier')
      }

      const data = await response.json()
      setResultData(data)
      setStatusMessage('Analyse terminée ✅')
    } catch (error: any) {
      setStatusMessage('Erreur : ' + error.message)
    } finally {
      setUploading(false)
    }
  }

  const tabs = [
    { id: 'bulletin-paie', label: 'Bulletin de Paie / contrat' },
    { id: 'analyse-salariale', label: 'Analyse Salariale' },
    { id: 'coaching-carriere', label: 'Coaching Carrière' }
  ]

  const renderTabContent = () => {
    switch (activeTab) {
      case 'bulletin-paie':
        return (
          <div className="space-y-8">
            <div
              className="relative border-2 border-dashed border-blue-300 rounded-2xl p-12 text-center bg-gradient-to-br from-blue-50 to-indigo-50 hover:border-blue-400 transition-all duration-300 group cursor-pointer"
              onClick={handleClick}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-blue-400/10 to-purple-400/10 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <input
                type="file"
                accept=".pdf,.jpg,.png"
                ref={fileInputRef}
                onChange={handleFileChange}
                className="hidden"
              />
              <div className="relative">
                <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <div className="text-blue-600 text-xl font-semibold mb-2">
                  Déposez votre bulletin de paie ou contrat ici
                </div>
                <div className="text-gray-500 text-sm">
                  Format acceptés : PDF, JPG, PNG • Taille max : 10MB
                </div>
              </div>
            </div>

            <button
              className="w-full bg-gradient-to-r from-purple-500 to-cyan-400 text-white py-4 rounded-2xl font-semibold text-lg hover:shadow-2xl hover:shadow-purple-500/25 hover:scale-105 transition-all duration-300 transform"
              onClick={handleClick}
              disabled={uploading}
            >
              <span className="flex items-center justify-center space-x-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{uploading ? 'Analyse en cours...' : 'Analyser mon bulletin ou contrat'}</span>
              </span>
            </button>

            {statusMessage && <div className="text-center text-sm text-gray-600">{statusMessage}</div>}

            {resultData && (
              <div className="bg-white rounded-xl shadow p-4 text-left">
                <h2 className="font-bold text-lg mb-2">Résultat de l'analyse</h2>
                <pre className="text-xs bg-gray-100 p-3 rounded overflow-auto">{JSON.stringify(resultData, null, 2)}</pre>
              </div>
            )}
          </div>
        )
      
      case 'analyse-salariale':
        return (
          <div className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="block text-gray-700 font-semibold mb-3 flex items-center space-x-2">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                  <span>Intitulé du poste</span>
                </label>
                <input 
                  type="text" 
                  placeholder="Ex : Développeur Full-Stack"
                  className="w-full p-4 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white/70 backdrop-blur-sm transition-all duration-200 hover:shadow-md"
                />
              </div>
              <div className="space-y-2">
                <label className="block text-gray-700 font-semibold mb-3 flex items-center space-x-2">
                  <div className="w-2 h-2 bg-cyan-400 rounded-full"></div>
                  <span>Années d'expérience</span>
                </label>
                <select className="w-full p-4 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white/70 backdrop-blur-sm transition-all duration-200 hover:shadow-md">
                  <option>Sélectionnez</option>
                  <option>0-2 ans</option>
                  <option>3-5 ans</option>
                  <option>5-10 ans</option>
                  <option>10+ ans</option>
                </select>
              </div>
            </div>
            <button className="w-full bg-gradient-to-r from-purple-500 to-cyan-400 text-white py-4 rounded-2xl font-semibold text-lg hover:shadow-2xl hover:shadow-purple-500/25 hover:scale-105 transition-all duration-300 transform">
              Analyser mon positionnement
            </button>
          </div>
        )
      
      case 'coaching-carriere':
        return (
          <div className="space-y-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-blue-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-gray-800 mb-4">Coaching Carrière</h3>
              <p className="text-gray-600 mb-8">Optimisez votre parcours professionnel avec nos conseils personnalisés</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gradient-to-br from-green-50 to-blue-50 p-6 rounded-xl border border-green-200">
                <h4 className="font-semibold text-gray-800 mb-3">📈 Évolution de carrière</h4>
                <p className="text-sm text-gray-600">Identifiez les opportunités d'avancement dans votre domaine</p>
              </div>
              <div className="bg-gradient-to-br from-blue-50 to-purple-50 p-6 rounded-xl border border-blue-200">
                <h4 className="font-semibold text-gray-800 mb-3">🎯 Objectifs professionnels</h4>
                <p className="text-sm text-gray-600">Définissez et atteignez vos objectifs de carrière</p>
              </div>
            </div>
            
            <button className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white py-4 rounded-2xl font-semibold text-lg hover:shadow-2xl hover:shadow-green-500/25 hover:scale-105 transition-all duration-300 transform">
              Commencer le coaching
            </button>
          </div>
        )
      
      default:
        return <div>Contenu par défaut</div>
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 pt-6 pb-6 px-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-purple-500 to-cyan-400 rounded-2xl mb-6 shadow-lg">
            <span className="text-white font-bold text-2xl">CF</span>
          </div>
          <h1 className="text-5xl font-bold bg-gradient-to-r from-gray-900 via-purple-900 to-gray-900 bg-clip-text text-transparent mb-4">
            CareerFinance AI
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
            Votre assistant intelligent pour optimiser votre carrière et comprendre vos finances
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Navigation Tabs */}
            <div className="flex space-x-2 mb-8 bg-white/70 backdrop-blur-sm p-2 rounded-2xl shadow-lg border border-white/20">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 py-4 px-6 rounded-xl font-medium transition-all duration-300 transform hover:scale-105 ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-purple-500 to-cyan-400 text-white shadow-xl shadow-purple-500/25'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-white/50'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-xl border border-white/20">
              {renderTabContent()}
            </div>
          </div>

          {/* AI Assistant Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-cyan-400 rounded-full flex items-center justify-center">
                  <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                </div>
                <h3 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-cyan-600 bg-clip-text text-transparent">
                  Assistant IA
                </h3>
              </div>
              
              <div className="bg-gradient-to-r from-purple-50 to-cyan-50 rounded-xl p-4 mb-6 border border-purple-100">
                <p className="text-gray-700 text-sm font-medium mb-3">
                  👋 Bonjour ! Je suis votre assistant personnel.
                </p>
              </div>

              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatMessage}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setChatMessage(e.target.value)}
                  placeholder="Tapez votre message ici..."
                  className="flex-1 p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm bg-white/70 backdrop-blur-sm"
                />
                <button className="bg-gradient-to-r from-purple-500 to-cyan-400 text-white p-3 rounded-xl hover:shadow-lg hover:scale-105 transition-all duration-200">
                  <Send size={16} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}