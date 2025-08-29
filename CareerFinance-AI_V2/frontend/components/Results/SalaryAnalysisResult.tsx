'use client'

import { useState } from 'react'
import { TrendingUp, TrendingDown, BarChart3, MapPin, Users, Briefcase, Download, Share2 } from 'lucide-react'

export interface Recommendation {
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
}

export interface Trend {
  title: string;
  detail: string;
}

export interface Etape {
  numero: number;
  contenu: string;
}

export interface SalaryData {
  jobTitle: string;
  experienceYears: number;
  location: string;
  salaireActuel: number;
  moyenne: number;
  minimum: number;
  maximum: number;
  percentile: number;
  recommandations?: Recommendation[];   // ← optional-safe
  tendances?: Trend[];                  // ← optional-safe
  etapes?: Etape[];                     // ← optional-safe
  marketUsed?: string;

  linkedinInsights?: {
    profilesAnalyzed?: number;
    confidenceLevel?: number;
    experienceLevel?: string;
    topSkills?: string[];
    targetCompanies?: string[];
    similarTitles?: string[];
    alternativeLocations?: string[];
    relatedSectors?: string[];
  };

  dataQuality?: {
    marketScope?: 'ville+pays' | 'pays' | 'global' | 'none' | 'unknown';
    samples?: number;
    marketLocation?: string;
    userRowStatus?: 'valide' | 'non_valide';
  };
}

interface SalaryAnalysisResultProps {
  data: SalaryData
  onClose: () => void
}

// ---------- helpers ----------
const toNumber = (v: any, d = 0) => {
  const n = Number(v)
  return Number.isFinite(n) ? n : d
}
const clamp = (n: number, min: number, max: number) => Math.min(Math.max(n, min), max)
const fmtMAD = (n: number) => Math.round(n).toLocaleString() + ' MAD'

export default function SalaryAnalysisResult({ data, onClose }: SalaryAnalysisResultProps) {
  const [activeTab, setActiveTab] = useState('comparaison')

  // Safe primitives
  const salaireActuel = toNumber(data.salaireActuel)
  const moyenne       = toNumber(data.moyenne)
  const minimum       = toNumber(data.minimum)
  const maximum       = toNumber(data.maximum)
  const percentile    = clamp(toNumber(data.percentile), 0, 100)

  // Safe collections
  const recommandations = Array.isArray(data.recommandations) ? data.recommandations : []
  const tendances       = Array.isArray(data.tendances) ? data.tendances : []
  const etapes          = Array.isArray(data.etapes) ? data.etapes : []

  // LinkedIn safe arrays
  const topSkills            = data.linkedinInsights?.topSkills ?? []
  const targetCompanies      = data.linkedinInsights?.targetCompanies ?? []
  const similarTitles        = data.linkedinInsights?.similarTitles ?? []
  const alternativeLocations = data.linkedinInsights?.alternativeLocations ?? []
  const relatedSectors       = data.linkedinInsights?.relatedSectors ?? []

  // Derived
  const safeMean = Math.max(moyenne, 1)
  const ecartSalaire = salaireActuel - moyenne
  const ecartPourcentage = (ecartSalaire / safeMean) * 100
  const denom = Math.max(maximum, moyenne, salaireActuel, 1)
  const top25 = Math.max(0, maximum * 0.8)

  const benchmarkData = [
    { entreprise: 'Entreprises similaires', salaire: moyenne, type: 'moyenne' as const },
    { entreprise: 'Top 25%',                 salaire: top25,  type: 'top' as const },
    { entreprise: 'Votre salaire',           salaire: salaireActuel, type: 'current' as const }
  ]

  const tabs = [
    { id: 'comparaison', label: 'Comparaison', icon: BarChart3 },
    { id: 'marche',      label: 'Marché',      icon: TrendingUp },
    { id: 'conseils',    label: 'Conseils',    icon: Briefcase },
    ...(data.linkedinInsights ? [{ id: 'linkedin', label: 'LinkedIn', icon: Users }] : []),
  ]

  const renderTabContent = () => {
    switch (activeTab) {
      case 'comparaison':
        return (
          <div className="space-y-6">
            {/* Résumé principal */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-6 border border-blue-200 dark:border-blue-800">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Votre Position Salariale</h3>
                <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm font-medium ${
                  ecartPourcentage >= 0
                    ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                    : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                }`}>
                  {ecartPourcentage >= 0 ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
                  <span>{ecartPourcentage >= 0 ? '+' : ''}{ecartPourcentage.toFixed(1)}%</span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400">Votre salaire</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{fmtMAD(salaireActuel)}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400">Moyenne du marché</p>
                  <p className="text-2xl font-bold text-blue-600">{fmtMAD(moyenne)}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400">Écart</p>
                  <p className={`text-2xl font-bold ${ecartSalaire >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {ecartSalaire >= 0 ? '+' : ''}{fmtMAD(Math.abs(ecartSalaire))}
                  </p>
                </div>
              </div>
            </div>

            {/* Graphique de comparaison */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Comparaison avec le Marché</h3>
              <div className="space-y-4">
                {benchmarkData.map((item, index) => (
                  <div key={index} className="flex items-center space-x-4">
                    <div className="w-32 text-sm text-gray-600 dark:text-gray-400">{item.entreprise}</div>
                    <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-3 relative">
                      <div
                        className={`h-3 rounded-full ${
                          item.type === 'current' ? 'bg-purple-500' :
                          item.type === 'moyenne' ? 'bg-blue-500' : 'bg-green-500'
                        }`}
                        style={{ width: `${clamp((item.salaire / denom) * 100, 0, 100)}%` }}
                      />
                    </div>
                    <div className="w-28 text-sm font-medium text-gray-900 dark:text-white text-right">
                      {fmtMAD(item.salaire)}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Percentile */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Votre Percentile</h3>
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <p className="text-gray-600 dark:text-gray-400 mb-2">
                    Vous gagnez plus que <span className="font-semibold text-purple-600">{percentile}%</span> des professionnels dans votre domaine
                  </p>
                  <div className="bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                    <div
                      className="bg-gradient-to-r from-purple-500 to-cyan-400 h-3 rounded-full"
                      style={{ width: `${percentile}%` }}
                    />
                  </div>
                </div>
                <div className="text-3xl font-bold text-purple-600">{percentile}%</div>
              </div>
            </div>
          </div>
        )

      case 'marche':
        return (
          <div className="space-y-6">
            {/* Détails */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Détails du jobTitle Analysé</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center space-x-3">
                  <Briefcase className="h-5 w-5 text-purple-500" />
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">jobTitle</p>
                    <p className="font-medium text-gray-900 dark:text-white">{data.jobTitle || '—'}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <Users className="h-5 w-5 text-blue-500" />
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Expérience</p>
                    <p className="font-medium text-gray-900 dark:text-white">{toNumber(data.experienceYears)} ans</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <MapPin className="h-5 w-5 text-green-500" />
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Localisation</p>
                    <p className="font-medium text-gray-900 dark:text-white">{data.location || '—'}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Marché utilisé */}
            <div className="bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-900/20 dark:to-teal-900/20 rounded-xl p-4 border border-emerald-200 dark:border-emerald-800">
              <div className="flex flex-wrap items-center gap-4">
                <span className="text-sm text-gray-600 dark:text-gray-400">Marché utilisé :</span>
                <span className="px-3 py-1 rounded-full text-sm font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300">
                  {data.marketUsed || data.dataQuality?.marketLocation || 'Indéterminé'}
                </span>
                <span className="text-sm text-gray-600 dark:text-gray-400">Portée :</span>
                <span className="px-3 py-1 rounded-full text-sm font-medium bg-teal-100 text-teal-800 dark:bg-teal-900/40 dark:text-teal-300">
                  {data.dataQuality?.marketScope || 'unknown'}
                </span>
                <span className="text-sm text-gray-600 dark:text-gray-400">Échantillons :</span>
                <span className="px-3 py-1 rounded-full text-sm font-medium bg-cyan-100 text-cyan-800 dark:bg-cyan-900/40 dark:text-cyan-300">
                  {toNumber(data.dataQuality?.samples)}
                </span>
                <span className="text-sm text-gray-600 dark:text-gray-400">Votre entrée :</span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  data.dataQuality?.userRowStatus === 'valide'
                    ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                    : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                }`}>
                  {data.dataQuality?.userRowStatus || '—'}
                </span>
              </div>
            </div>

            {/* Fourchette salariale */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Fourchette Salariale du Marché</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                  <p className="text-sm text-red-600 dark:text-red-400 font-medium">Minimum</p>
                  <p className="text-xl font-bold text-red-700 dark:text-red-300">{fmtMAD(minimum)}</p>
                </div>
                <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <p className="text-sm text-blue-600 dark:text-blue-400 font-medium">Moyenne</p>
                  <p className="text-xl font-bold text-blue-700 dark:text-blue-300">{fmtMAD(moyenne)}</p>
                </div>
                <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                  <p className="text-sm text-green-600 dark:text-green-400 font-medium">Maximum</p>
                  <p className="text-xl font-bold text-green-700 dark:text-green-300">{fmtMAD(maximum)}</p>
                </div>
              </div>
            </div>

            {/* Tendances du marché */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Tendances du Marché
              </h3>
              <div className="space-y-4">
                {tendances.map((trend, index) => {
                  const t = trend?.title?.toLowerCase?.() ?? ''
                  const isCroissance = t.includes('croissance')
                  const isDemande = t.includes('demande')
                  const iconColor = isCroissance ? 'text-green-500' : isDemande ? 'text-blue-500' : 'text-gray-500'
                  const bgColor = isCroissance ? 'bg-green-50 dark:bg-green-900/10' : isDemande ? 'bg-blue-50 dark:bg-blue-900/10' : 'bg-gray-100 dark:bg-gray-700'
                  const borderColor = isCroissance ? 'border-green-300' : isDemande ? 'border-blue-300' : 'border-gray-300'

                  return (
                    <div key={index} className={`flex items-start space-x-3 p-4 border rounded-lg ${borderColor} ${bgColor}`}>
                      <BarChart3 className={`h-5 w-5 mt-1 ${iconColor}`} />
                      <div>
                        <p className="font-semibold text-gray-900 dark:text-white">{trend.title}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{trend.detail}</p>
                      </div>
                    </div>
                  )
                })}
                {tendances.length === 0 && (
                  <p className="text-sm text-gray-500 dark:text-gray-400">Aucune tendance disponible.</p>
                )}
              </div>
            </div>
          </div>
        )

      case 'conseils':
        return (
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Plan d'Action Personnalisé</h3>
              <div className="space-y-4">
                {recommandations.map((rec, index) => {
                  const couleurPastille = rec.priority === 'high' ? 'bg-red-500'
                    : rec.priority === 'medium' ? 'bg-yellow-500' : 'bg-green-500'

                  const badgeStyle = rec.priority === 'high'
                    ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                    : rec.priority === 'medium'
                    ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
                    : 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'

                  const label = rec.priority === 'high' ? 'Priorité élevée'
                    : rec.priority === 'medium' ? 'Priorité moyenne' : 'Priorité faible'

                  return (
                    <div key={index} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                      <div className="flex items-start space-x-3">
                        <div className={`w-2 h-2 rounded-full mt-2 ${couleurPastille}`} />
                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-900 dark:text-white">{rec.title}</h4>
                          <p className="text-gray-600 dark:text-gray-400 mt-1">{rec.description}</p>
                          <span className={`inline-block mt-2 px-2 py-1 rounded-full text-xs font-medium ${badgeStyle}`}>
                            {label}
                          </span>
                        </div>
                      </div>
                    </div>
                  )
                })}
                {recommandations.length === 0 && (
                  <p className="text-sm text-gray-500 dark:text-gray-400">Aucune recommandation disponible.</p>
                )}
              </div>
            </div>

            {etapes.length > 0 && (
              <div className="bg-gradient-to-r from-purple-50 to-cyan-50 dark:from-purple-900/20 dark:to-cyan-900/20 rounded-xl p-6 border border-purple-200 dark:border-purple-800">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Prochaines Étapes</h3>
                <div className="space-y-3">
                  {etapes.map((etape, index) => (
                    <div key={index} className="flex items-center space-x-3">
                      <div className="w-6 h-6 bg-purple-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                        {etape.numero}
                      </div>
                      <p className="text-gray-700 dark:text-gray-300">{etape.contenu}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )

      case 'linkedin':
        return data.linkedinInsights ? (
          <div className="space-y-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-6 border border-blue-200 dark:border-blue-800">
              <div className="flex items-center space-x-3 mb-4">
                <svg className="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                </svg>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Analyse basée sur LinkedIn</h3>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">{toNumber(data.linkedinInsights?.profilesAnalyzed)}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Profils analysés</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">{Math.round((toNumber(data.linkedinInsights?.confidenceLevel) * 100))}%</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Niveau de confiance</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-purple-600 capitalize">{data.linkedinInsights?.experienceLevel ?? '-'}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Niveau détecté</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-orange-600">{data.dataQuality?.marketScope || '—'}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Portée marché</p>
                </div>
              </div>
            </div>

            {topSkills.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Compétences les plus demandées</h3>
                <div className="flex flex-wrap gap-2">
                  {topSkills.map((skill, index) => (
                    <span key={index} className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded-full text-sm font-medium">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {targetCompanies.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Entreprises qui recrutent</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {targetCompanies.map((company, index) => (
                    <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-cyan-400 rounded-full flex items-center justify-center text-white font-bold text-sm">
                        {company.charAt(0).toUpperCase()}
                      </div>
                      <span className="text-gray-900 dark:text-white font-medium">{company}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {similarTitles.length > 0 && (
                <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Postes similaires</h3>
                  <ul className="space-y-2">
                    {similarTitles.slice(0, 5).map((title, index) => (
                      <li key={index} className="text-gray-700 dark:text-gray-300 flex items-center space-x-2">
                        <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                        <span>{title}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {relatedSectors.length > 0 && (
                <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Secteurs connexes</h3>
                  <ul className="space-y-2">
                    {relatedSectors.slice(0, 5).map((sector, index) => (
                      <li key={index} className="text-gray-700 dark:text-gray-300 flex items-center space-x-2">
                        <span className="w-2 h-2 bg-cyan-500 rounded-full"></span>
                        <span>{sector}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ) : null

      default:
        return null
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-500 to-cyan-400 p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">Analyse Salariale</h2>
              <p className="opacity-90">{data.jobTitle || '—'} • {data.location || '—'} • {toNumber(data.experienceYears)} ans</p>
            </div>
            <div className="flex items-center space-x-2">
              <button className="p-2 hover:bg-white/20 rounded-lg transition-colors" title="Télécharger">
                <Download className="h-5 w-5" />
              </button>
              <button className="p-2 hover:bg-white/20 rounded-lg transition-colors" title="Partager">
                <Share2 className="h-5 w-5" />
              </button>
              <button onClick={onClose} className="p-2 hover:bg-white/20 rounded-lg transition-colors" title="Fermer">
                ✕
              </button>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 dark:border-gray-700">
          <div className="flex space-x-0">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 flex items-center justify-center space-x-2 py-4 px-6 font-medium transition-all duration-200 ${
                    activeTab === tab.id
                      ? 'text-purple-600 dark:text-purple-400 border-b-2 border-purple-600 dark:border-purple-400 bg-purple-50 dark:bg-purple-900/20'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-800'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {renderTabContent()}
        </div>
      </div>
    </div>
  )
}
