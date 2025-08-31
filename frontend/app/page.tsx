// app/page.tsx
'use client'

<<<<<<< HEAD
import { useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
=======
import { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import AuthGuard from '../components/Auth/AuthGuard'
>>>>>>> 5e0de77 (Auth commit)

// Bulletin
import BulletinAnalysisResult from '../components/Results/BulletinAnalysisResult'
import type { BulletinResponse } from '../components/Results/BulletinAnalysisResult'

// Salaire
import SalaryAnalysisResult, { type SalaryData } from '../components/Results/SalaryAnalysisResult'

// Coaching
import CareerCoachingResult from '../components/Results/CareerCoachingResult'

export default function Home() {
<<<<<<< HEAD
=======
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  // Vérification d'authentification directe
  useEffect(() => {
    console.log('🔒 Page principale - Vérification d\'authentification...')
    const token = localStorage.getItem('auth_token')
    console.log('🔒 Page principale - Token trouvé:', token ? 'Oui' : 'Non')
    
    if (!token) {
      console.log('🔒 Page principale - Pas de token, redirection vers /auth/login')
      router.push('/auth/login')
    } else {
      console.log('🔒 Page principale - Token trouvé, authentification réussie')
      setIsAuthenticated(true)
    }
    setIsLoading(false)
  }, [router])

>>>>>>> 5e0de77 (Auth commit)
  const [careerUploading, setCareerUploading] = useState(false)
  const [careerStatusMessage, setCareerStatusMessage] = useState('')
  const [careerData, setCareerData] = useState<any>(null)

  const [uploading, setUploading] = useState(false)
  const [statusMessage, setStatusMessage] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [resultData, setResultData] = useState<SalaryData | null>(null)
  const [activeTab, setActiveTab] = useState<'bulletin-paie' | 'analyse-salariale' | 'coaching-carriere'>('bulletin-paie')
<<<<<<< HEAD
  const router = useRouter()
=======
>>>>>>> 5e0de77 (Auth commit)

  // Modals
  const [showBulletinResult, setShowBulletinResult] = useState(false)
  const [showSalaryResult, setShowSalaryResult] = useState(false)
  const [showCareerResult, setShowCareerResult] = useState(false)

  // Bulletin data (on conserve tout)
  const [bulletinData, setBulletinData] = useState<BulletinResponse | null>(null)

  // Formulaires
  const [salaryFormData, setSalaryFormData] = useState({
    poste: '',
    experience: '',
    localisation: '',
    salaireActuel: 0,
  })

  const [careerFormData, setCareerFormData] = useState({
    objectif: '',
    competences: '',
    secteur: '',
  })

  const clearField = (field: string) => {
    setCareerFormData({ ...careerFormData, [field]: '' })
  }

  // -------- Helpers --------
  const parseExperienceYears = (label: string): number => {
    const s = (label || '').toLowerCase().replace(/\s/g, '')
    if (s.includes('0-2')) return 1
    if (s.includes('2-5') || s.includes('3-5')) return 3
    if (s.includes('5-10')) return 6
    if (s.includes('10') || s.includes('10+')) return 10
    const n = parseInt(label as any, 10)
    return Number.isFinite(n) ? n : 0
  }

  // ====== Upload bulletin / contrat ======
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    setUploading(true)
    setStatusMessage('Analyse en cours...')

    try {
      const response = await fetch('http://localhost:8000/api/documents/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) throw new Error('Erreur serveur')

      const data: BulletinResponse = await response.json()
      setBulletinData(data)
      setStatusMessage('Analyse terminée ✅')
      setShowBulletinResult(true)
    } catch (err: any) {
      setStatusMessage('Erreur : ' + err.message)
    } finally {
      setUploading(false)
    }
  }

  // ====== Démo locale (optionnelle) ======
  const handleBulletinAnalysis = () => {
    const mockBulletinData: BulletinResponse = {
      fileName: 'bulletin_juillet_2025.pdf',
      analysis: {
        resume: {
          salaireBrut: 25000,
          salaireNet: 18500,
          cotisations: 4500,
          impots: 2000,
        },
        details: {
          salaireBase: 20000,
          primes: [
            { libelle: 'Congés payés', montant: 1000 },
            { libelle: 'Prime de rendement', montant: 2000 },
          ],
          heuresSupp: [{ libelle: 'Heures nuit', montant: 1500 }],
          cotisations: [
            { libelle: 'CNSS', montant: 1500, type: 'patronale' },
            { libelle: 'AMO', montant: 1200, type: 'patronale' },
            { libelle: 'Retraite Complémentaire', montant: 1000, type: 'salariale' },
            { libelle: 'Assurance Chômage', montant: 800, type: 'salariale' },
          ],
          impots: [{ libelle: 'IR', montant: 2000 }],
          netAPayer: 18500,
        },
        anomalies: [
          {
            type: 'warning',
            title: 'Cotisation élevée',
            description: 'La cotisation retraite semble plus élevée que la moyenne.',
            impact: 'Moyen',
          },
        ],
        recommandations: [
          'Vérifiez votre taux de cotisation.',
          "Discutez avec l’employeur des options d’optimisation.",
        ],
      },
      analysis_global: {
        status: 'ok',
        title: 'Bulletin conforme',
        deductionRate: 22.0,
        summary:
          'Votre bulletin présente un taux de prélèvement de 22.0%. Les résultats semblent conformes.',
        highlights: ['Salaire brut: 25000 MAD', 'Salaire net: 18500 MAD', 'Taux: 22.0%'],
      },
    }

    setBulletinData(mockBulletinData)
    setShowBulletinResult(true)
  }

  // ====== Analyse salariale ======
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000'

  const handleSalaryAnalysis = async () => {
  try {
    // (facultatif) UI state
    setShowSalaryResult(false);
    // setLoading?.(true); // si vous avez un état de chargement

    const experienceYears = parseExperienceYears(salaryFormData.experience);
    const payload = {
      jobTitle: salaryFormData.poste,
      location: salaryFormData.localisation,
      experienceYears,
      currentSalary: Number(salaryFormData.salaireActuel || 0),
    };

    // OPTIONAL: si vous voulez forcer la (ré)création des embeddings/FAISS
    // avant chaque analyse, décommentez ces deux lignes :
    // await fetch(`${API_BASE}/api/salary-enhanced/dataset/backfill`, { method: 'POST' });
    // await fetch(`${API_BASE}/api/salary-enhanced/dataset/reload`,   { method: 'POST' });

    // Analyse unique via Supabase RAG + Gemini
    const res = await fetch(`${API_BASE}/api/salary-enhanced/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    // gestion d’erreur lisible
    if (!res.ok) {
      const errText = await res.text();
      throw new Error(errText || `Request failed with status ${res.status}`);
    }

    const data: SalaryData = await res.json();
    setResultData(data);
    setShowSalaryResult(true);
  } catch (err: any) {
    console.error('Erreur analyse salariale :', err?.message || err);
    // showToast?.(err?.message ?? 'Erreur inconnue'); // si vous avez un toast
  } finally {
    // setLoading?.(false);
  }
};

  // ====== Coaching carrière ======
const handleCareerCoaching = async () => {
  setCareerUploading(true)
  setCareerStatusMessage('🔍 Vérification du système LinkedIn...')

  try {
    let endpoint = 'http://localhost:8000/api/supabase-career/coaching' // Endpoint correct
    let useRAG = true
    let ragProfilesCount = 0

    try {
      // Vérifier le statut du système Supabase RAG
      const ragStatusResponse = await fetch('http://localhost:8000/api/supabase-career/status')
      if (ragStatusResponse.ok) {
        const ragStatus = await ragStatusResponse.json()

        if (ragStatus.isInitialized && ragStatus.profilesCount > 0) {
          useRAG = true
          ragProfilesCount = ragStatus.profilesCount
          setCareerStatusMessage(
            `✨ Analyse enrichie avec ${ragProfilesCount} profils LinkedIn...`
          )
        } else {
          useRAG = false
          setCareerStatusMessage(
            "📊 Analyse classique (RAG LinkedIn en cours d'initialisation)..."
          )
        }
      } else {
        useRAG = false
        setCareerStatusMessage('📊 Analyse classique (RAG LinkedIn non disponible)...')
      }
    } catch {
      useRAG = false
      setCareerStatusMessage('📊 Analyse classique...')
    }

    // Construire le body de la requête selon le format attendu par l'API
    const requestBody = {
      user_id: 1, // Ajout du user_id requis
      goal: careerFormData.objectif || "Évoluer vers un poste de management",
      skills: careerFormData.competences
        ? careerFormData.competences.split(',').map((c) => c.trim())
        : ['JavaScript', 'React', 'Node.js'],
      sector: careerFormData.secteur || 'Technologie',
      useRAG: useRAG // Utiliser le bon paramètre
    }

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    })

    const result = await response.json()

    if (!response.ok) {
      setCareerStatusMessage('Erreur : ' + (result.detail || 'Erreur inconnue'))
      return
    }

    // Adapter la réponse selon le format retourné par l'API
    if (result.success && result.data) {
      setCareerData(result.data)
    } else {
      setCareerData(result)
    }
    
    setShowCareerResult(true)

    setCareerStatusMessage(
      useRAG
        ? `🎉 Analyse terminée avec insights LinkedIn (${ragProfilesCount} profils analysés) !`
        : '✅ Analyse terminée !'
    )
  } catch (error) {
    setCareerStatusMessage('Erreur : ' + (error instanceof Error ? error.message : String(error)))
  } finally {
    setCareerUploading(false)
  }
}

  const tabs = [
    { id: 'bulletin-paie', label: 'Bulletin de Paie / contrat' },
    { id: 'analyse-salariale', label: 'Analyse Salariale' },
    { id: 'coaching-carriere', label: 'Coaching Carrière' },
  ] as const

  const renderTabContent = () => {
    switch (activeTab) {
      case 'bulletin-paie':
        return (
          <div className="space-y-6">
            <div
              className="relative border-2 border-dashed border-blue-300 rounded-xl p-6 text-center bg-gradient-to-br from-blue-50 to-indigo-50 hover:border-blue-400 transition-all duration-300 group cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                type="file"
                accept=".pdf,.jpg,.png"
                ref={fileInputRef}
                onChange={handleFileChange}
                className="hidden"
              />
              <div className="relative">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center mx-auto mb-3">
                  <svg
                    className="w-6 h-6 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                    />
                  </svg>
                </div>
                <div className="text-blue-600 text-lg font-semibold mb-2">
                  Déposez votre bulletin de paie ou contrat ici
                </div>
                <div className="text-gray-500 text-sm">
                  Formats acceptés : PDF, JPG, PNG • Taille max : 10MB
                </div>
              </div>
            </div>

            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="w-full bg-gradient-to-r from-purple-500 to-cyan-400 text-white py-3 rounded-xl font-semibold hover:shadow-xl hover:scale-105 transition-all duration-300"
            >
              {uploading ? 'Analyse en cours...' : 'Analyser mon bulletin ou contrat'}
            </button>

            {statusMessage && (
              <div className="text-center text-sm text-gray-600">{statusMessage}</div>
            )}
          </div>
        )

      case 'analyse-salariale':
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="block text-gray-700 dark:text-gray-300 font-semibold mb-2 flex items-center space-x-2">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                  <span>Intitulé du poste</span>
                </label>
                <input
                  type="text"
                  placeholder="Ex : Développeur Full-Stack"
                  value={salaryFormData.poste}
                  onChange={(e) => setSalaryFormData({ ...salaryFormData, poste: e.target.value })}
                  className="w-full p-3 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white/70 dark:bg-gray-700/70 backdrop-blur-sm transition-all durée-200 hover:shadow-md text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                />
              </div>
              <div className="space-y-2">
                <label className="block text-gray-700 dark:text-gray-300 font-semibold mb-2 flex items-center space-x-2">
                  <div className="w-2 h-2 bg-cyan-400 rounded-full"></div>
                  <span>Années d'expérience</span>
                </label>
                <select
                  value={salaryFormData.experience}
                  onChange={(e) =>
                    setSalaryFormData({ ...salaryFormData, experience: e.target.value })
                  }
                  className="w-full p-3 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white/70 dark:bg-gray-700/70 backdrop-blur-sm transition-all durée-200 hover:shadow-md text-gray-900 dark:text-white"
                >
                  <option>Sélectionnez</option>
                  <option>0-2 ans</option>
                  <option>2-5 ans</option>
                  <option>5-10 ans</option>
                  <option>10+ ans</option>
                </select>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="block text-gray-700 dark:text-gray-300 font-semibold mb-2 flex items-center space-x-2">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                  <span>Localisation</span>
                </label>
                <input
                  type="text"
                  placeholder="Ex : Casablanca, Rabat, Tanger..."
                  value={salaryFormData.localisation}
                  onChange={(e) =>
                    setSalaryFormData({ ...salaryFormData, localisation: e.target.value })
                  }
                  className="w-full p-3 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white/70 dark:bg-gray-700/70 backdrop-blur-sm transition-all durée-200 hover:shadow-md text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                />
              </div>
              <div className="space-y-2">
                <label className="block text-gray-700 dark:text-gray-300 font-semibold mb-2 flex items-center space-x-2">
                  <div className="w-2 h-2 bg-cyan-400 rounded-full"></div>
                  <span>Salaire actuel (MAD/mois)</span>
                </label>
                <input
                  type="number"
                  placeholder="Ex : 15 000"
                  value={salaryFormData.salaireActuel || ''}
                  onChange={(e) =>
                    setSalaryFormData({
                      ...salaryFormData,
                      salaireActuel: parseInt(e.target.value) || 0,
                    })
                  }
                  className="w-full p-3 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white/70 dark:bg-gray-700/70 backdrop-blur-sm transition-all durée-200 hover:shadow-md text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                />
              </div>
            </div>

            <button
              onClick={handleSalaryAnalysis}
              className="w-full bg-gradient-to-r from-purple-500 to-cyan-400 text-white py-3 rounded-xl font-semibold hover:shadow-xl hover:shadow-purple-500/25 hover:scale-105 transition-all duration-300 transform"
            >
              <span className="flex items-center justify-center space-x-3">
                <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                <span>Analyser mon positionnement</span>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </span>
            </button>
          </div>
        )

      case 'coaching-carriere':
        return (
          <div className="space-y-6">
            <div className="space-y-2">
              <label className="block text-gray-700 dark:text-gray-300 font-semibold mb-2 flex items-center space-x-2">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <span>Objectif professionnel</span>
              </label>
              <textarea
                placeholder="Décrivez votre objectif de carrière..."
                rows={3}
                value={careerFormData.objectif}
                onChange={(e) => setCareerFormData({ ...careerFormData, objectif: e.target.value })}
                className="w-full p-3 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white/70 dark:bg-gray-700/70 backdrop-blur-sm transition-all durée-200 hover:shadow-md resize-none text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
              />
            </div>
            <div className="space-y-2">
              <label className="block text-gray-700 dark:text-gray-300 font-semibold mb-2 flex items-center space-x-2">
                <div className="w-2 h-2 bg-cyan-400 rounded-full"></div>
                <span>Compétences clés actuelles</span>
              </label>
              <input
                type="text"
                placeholder="Ex : JavaScript, Python, React..."
                value={careerFormData.competences}
                onChange={(e) =>
                  setCareerFormData({ ...careerFormData, competences: e.target.value })
                }
                className="w-full p-3 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white/70 dark:bg-gray-700/70 backdrop-blur-sm transition-all durée-200 hover:shadow-md text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
              />
            </div>
            <div className="space-y-2">
              <label className="block text-gray-700 dark:text-gray-300 font-semibold mb-2 flex items-center space-x-2">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <span>Secteur d'activité</span>
              </label>
              <select
                value={careerFormData.secteur}
                onChange={(e) => setCareerFormData({ ...careerFormData, secteur: e.target.value })}
                className="w-full p-3 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white/70 dark:bg-gray-700/70 backdrop-blur-sm transition-all durée-200 hover:shadow-md text-gray-900 dark:text-white"
              >
                <option>Sélectionnez...</option>
                <option>Technologie</option>
                <option>Finance</option>
                <option>Santé</option>
                <option>Éducation</option>
                <option>Commerce</option>
              </select>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button
                onClick={handleCareerCoaching}
                disabled={careerUploading}
                className="bg-gradient-to-r from-purple-500 to-cyan-400 text-white py-3 rounded-xl font-semibold hover:shadow-xl hover:shadow-purple-500/25 hover:scale-105 transition-all duration-300 transform"
              >
                <span className="flex items-center justify-center space-x-2">
                  {careerUploading && (
                    <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                  )}
                  <span>{careerUploading ? 'Analyse en cours...' : 'Générer mon plan de carrière'}</span>
                </span>
              </button>

              <button
                onClick={handleCareerCoaching}
                className="bg-gradient-to-r from-blue-500 to-pink-500 text-white py-3 rounded-xl font-semibold hover:shadow-xl hover:shadow-blue-500/25 hover:scale-105 transition-all duration-300 transform"
              >
                <span className="flex items-center justify-center space-x-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                    />
                  </svg>
                  <span>Script de négociation</span>
                </span>
              </button>
              {careerStatusMessage && (
                <div className="text-center text-sm text-gray-600 mt-2">
                  {careerStatusMessage}
                </div>
              )}
            </div>
          </div>
        )

      default:
        return null
    }
  }

<<<<<<< HEAD
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 pt-6 pb-6 px-6 transition-colors duration-300">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-purple-500 to-cyan-400 rounded-2xl mb-6 shadow-lg">
            <span className="text-white font-bold text-2xl">CF</span>
          </div>
          <h1 className="text-5xl font-bold bg-gradient-to-r from-gray-900 via-purple-900 to-gray-900 dark:from-white dark:via-purple-300 dark:to-white bg-clip-text text-transparent mb-4">
            CareerFinance AI
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto leading-relaxed">
            Votre assistant intelligent pour optimiser votre carrière et comprendre vos finances
          </p>
          <div className="mt-6 flex flex-col items-center space-y-4">
            <div className="flex space-x-2">
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
              <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse delay-75"></div>
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse delay-150"></div>
=======
  if (isLoading) {
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

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-red-500 to-red-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-2xl">🔒</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Accès Refusé</h2>
          <p className="text-gray-600 mb-4">Vous devez être connecté pour accéder à cette page.</p>
          <button
            onClick={() => router.push('/auth/login')}
            className="bg-gradient-to-r from-purple-500 to-cyan-400 text-white px-6 py-3 rounded-lg hover:shadow-lg transition-all"
          >
            Se connecter
          </button>
        </div>
      </div>
    )
  }

  return (
    <AuthGuard>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 pt-6 pb-6 px-6 transition-colors duration-300">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-purple-500 to-cyan-400 rounded-2xl mb-6 shadow-lg">
              <span className="text-white font-bold text-2xl">CF</span>
            </div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-gray-900 via-purple-900 to-gray-900 dark:from-white dark:via-purple-300 dark:to-white bg-clip-text text-transparent mb-4">
              CareerFinance AI
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto leading-relaxed">
              Votre assistant intelligent pour optimiser votre carrière et comprendre vos finances
            </p>
            <div className="mt-6 flex flex-col items-center space-y-4">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse delay-75"></div>
                <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse delay-150"></div>
              </div>
            </div>
          </div>

          <div className="max-w-4xl mx-auto">
            {/* Tabs */}
            <div className="flex space-x-2 mb-6 bg-white/70 dark:bg-gray-800/70 backdrop-blur-sm p-2 rounded-xl shadow-lg border border-white/20 dark:border-gray-700/20">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 py-4 px-6 rounded-xl font-medium transition-all duration-300 transform hover:scale-105 ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-purple-500 to-cyan-400 text-white shadow-xl shadow-purple-500/25'
                      : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-white/50 dark:hover:bg-gray-700/50'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl p-6 shadow-xl border border-white/20 dark:border-gray-700/20">
              {renderTabContent()}
>>>>>>> 5e0de77 (Auth commit)
            </div>
          </div>
        </div>

<<<<<<< HEAD
        <div className="max-w-4xl mx-auto">
          {/* Tabs */}
          <div className="flex space-x-2 mb-6 bg-white/70 dark:bg-gray-800/70 backdrop-blur-sm p-2 rounded-xl shadow-lg border border-white/20 dark:border-gray-700/20">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 py-4 px-6 rounded-xl font-medium transition-all duration-300 transform hover:scale-105 ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-purple-500 to-cyan-400 text-white shadow-xl shadow-purple-500/25'
                    : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-white/50 dark:hover:bg-gray-700/50'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl p-6 shadow-xl border border-white/20 dark:border-gray-700/20">
            {renderTabContent()}
          </div>
        </div>
      </div>

      {/* Modals */}
      {showBulletinResult && bulletinData && (
        <BulletinAnalysisResult
          data={bulletinData}
          onClose={() => setShowBulletinResult(false)}
        />
      )}

      {showSalaryResult && resultData && (
        <SalaryAnalysisResult
          data={resultData}
          onClose={() => setShowSalaryResult(false)}
        />
      )}

      {showCareerResult && careerData && (
        <CareerCoachingResult
          data={careerData}
          onClose={() => setShowCareerResult(false)}
        />
      )}
    </div>
=======
        {/* Modals */}
        {showBulletinResult && bulletinData && (
          <BulletinAnalysisResult
            data={bulletinData}
            onClose={() => setShowBulletinResult(false)}
          />
        )}

        {showSalaryResult && resultData && (
          <SalaryAnalysisResult
            data={resultData}
            onClose={() => setShowSalaryResult(false)}
          />
        )}

        {showCareerResult && careerData && (
          <CareerCoachingResult
            data={careerData}
            onClose={() => setShowCareerResult(false)}
          />
        )}
      </div>
    </AuthGuard>
>>>>>>> 5e0de77 (Auth commit)
  )
}
