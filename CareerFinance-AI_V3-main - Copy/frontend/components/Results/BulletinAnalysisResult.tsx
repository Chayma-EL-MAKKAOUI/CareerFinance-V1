// BulletinAnalysisResult.tsx
'use client'

import { useState } from 'react'
import { FileText, AlertTriangle, CheckCircle, TrendingUp, Download, Share2, Eye } from 'lucide-react'

type LigneMontant = { libelle: string; montant: number }
type Cotisation = LigneMontant & { type: string }

export interface Anomalie {
  type?: string            // rendu tolérant si backend n’envoie pas ce champ
  title: string
  description: string
  impact: 'Faible' | 'Moyen' | 'Élevé' | 'Positif' | string
}

/** Nouveau bloc renvoyé par le backend */
export interface AnalysisGlobal {
  status: 'ok' | 'warning' | 'alert' | string
  title: string
  deductionRate: number
  summary: string
  highlights?: string[]
}

export interface AnalysisData {
  resume: {
    salaireBrut: number
    salaireNet: number
    cotisations: number
    impots: number
  }
  details: {
    salaireBase: number
    primes: LigneMontant[]
    heuresSupp: LigneMontant[]
    cotisations: Cotisation[]
    impots: LigneMontant[]
    netAPayer: number
  }
  anomalies: Anomalie[]
  recommandations: string[]
}

export interface BulletinResponse {
  fileName: string
  // nouveau schéma
  analysis?: AnalysisData
  analysis_global?: AnalysisGlobal
  // compat: ancien schéma (champs au top-level)
  resume?: AnalysisData['resume']
  details?: AnalysisData['details']
  anomalies?: AnalysisData['anomalies']
  recommandations?: AnalysisData['recommandations']
}

interface BulletinAnalysisResultProps {
  data: BulletinResponse
  onClose: () => void
}

export default function BulletinAnalysisResult({ data, onClose }: BulletinAnalysisResultProps) {
  const [activeTab, setActiveTab] = useState<'resume' | 'details' | 'anomalies' | 'conseils'>('resume')

  // ── Normalisation pour supporter ancien + nouveau schéma ────────────────
  const analysis: AnalysisData = data.analysis
    ? data.analysis
    : {
        resume: data.resume || { salaireBrut: 0, salaireNet: 0, cotisations: 0, impots: 0 },
        details:
          data.details || {
            salaireBase: 0,
            primes: [],
            heuresSupp: [],
            cotisations: [],
            impots: [],
            netAPayer: 0,
          },
        anomalies: data.anomalies || [],
        recommandations: data.recommandations || [],
      }

  const g: AnalysisGlobal | undefined = data.analysis_global

  // ── Helpers ─────────────────────────────────────────────────────────────
  const sommeMontant = (arr: LigneMontant[] | Cotisation[] | undefined): number => {
    if (!Array.isArray(arr)) return 0
    return arr.reduce((acc, item) => acc + (Number(item?.montant) || 0), 0)
  }

  const tabs = [
    { id: 'resume', label: 'Résumé', icon: Eye },
    { id: 'details', label: 'Détails', icon: FileText },
    { id: 'anomalies', label: 'Anomalies', icon: AlertTriangle },
    { id: 'conseils', label: 'Conseils', icon: TrendingUp },
  ] as const

  const renderGlobalBadge = () => {
    const status = g?.status || 'ok'
    const color =
      status === 'ok'
        ? 'text-green-600 dark:text-green-400'
        : status === 'warning'
        ? 'text-amber-600 dark:text-amber-400'
        : 'text-red-600 dark:text-red-400'
    const iconColor =
      status === 'ok' ? 'text-green-500' : status === 'warning' ? 'text-amber-500' : 'text-red-500'
    return (
      <div className="flex items-center space-x-3 mb-4">
        <CheckCircle className={`h-6 w-6 ${iconColor}`} />
        <span className={`${color} font-medium`}>{g?.title || 'Analyse'}</span>
      </div>
    )
  }

  // ── Rendus des onglets ──────────────────────────────────────────────────
  const renderTabContent = () => {
    switch (activeTab) {
      case 'resume':
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-xl p-4 text-white">
                <h3 className="text-sm font-medium opacity-90">Salaire Brut</h3>
                <p className="text-2xl font-bold">
                  {analysis.resume.salaireBrut.toLocaleString()} MAD
                </p>
              </div>
              <div className="bg-gradient-to-r from-teal-500 to-teal-600 rounded-xl p-4 text-white">
                <h3 className="text-sm font-medium opacity-90">Salaire Net</h3>
                <p className="text-2xl font-bold">
                  {analysis.resume.salaireNet.toLocaleString()} MAD
                </p>
              </div>
              <div className="bg-gradient-to-r from-amber-500 to-amber-600 rounded-xl p-4 text-white">
                <h3 className="text-sm font-medium opacity-90">Cotisations</h3>
                <p className="text-2xl font-bold">
                  {analysis.resume.cotisations.toLocaleString()} MAD
                </p>
              </div>
              <div className="bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-xl p-4 text-white">
                <h3 className="text-sm font-medium opacity-90">Impôts</h3>
                <p className="text-2xl font-bold">
                  {analysis.resume.impots.toLocaleString()} MAD
                </p>
              </div>
            </div>

            {/* Analyse globale dynamique */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Analyse Globale
              </h3>

              {renderGlobalBadge()}

              <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                {g?.summary || (
                  <>
                    Votre bulletin de paie présente une structure analysée automatiquement.
                  </>
                )}{' '}
                {typeof g?.deductionRate === 'number' && (
                  <>
                    Taux de prélèvement&nbsp;
                    <span className="font-semibold">{g.deductionRate.toFixed(1)}%</span>.
                  </>
                )}
              </p>

              {Array.isArray(g?.highlights) && g!.highlights!.length > 0 && (
                <ul className="mt-4 list-disc pl-5 text-gray-600 dark:text-gray-300 space-y-1">
                  {g!.highlights!.map((h, i) => (
                    <li key={i}>{h}</li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        )

      case 'details':
        return (
          <div className="space-y-4">
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Décomposition Détaillée
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700">
                  <span className="text-gray-600 dark:text-gray-300">Salaire de base</span>
                  <span className="font-semibold text-gray-900 dark:text-white">
                    {analysis.details.salaireBase.toLocaleString()} MAD
                  </span>
                </div>

                <div className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700">
                  <span className="text-gray-600 dark:text-gray-300">Primes</span>
                  <span className="font-semibold text-green-600">
                    +{sommeMontant(analysis.details.primes).toLocaleString()} MAD
                  </span>
                </div>

                <div className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700">
                  <span className="text-gray-600 dark:text-gray-300">Heures supplémentaires</span>
                  <span className="font-semibold text-green-600">
                    +{sommeMontant(analysis.details.heuresSupp).toLocaleString()} MAD
                  </span>
                </div>

                <div className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700">
                  <span className="text-gray-600 dark:text-gray-300">Cotisations sociales</span>
                  <span className="font-semibold text-red-600">
                    -{sommeMontant(analysis.details.cotisations).toLocaleString()} MAD
                  </span>
                </div>

                <div className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700">
                  <span className="text-gray-600 dark:text-gray-300">Impôt sur le revenu</span>
                  <span className="font-semibold text-red-600">
                    -{sommeMontant(analysis.details.impots).toLocaleString()} MAD
                  </span>
                </div>

                <div className="flex justify-between items-center py-3 bg-gray-50 dark:bg-gray-700 rounded-lg px-4 mt-4">
                  <span className="font-semibold text-gray-900 dark:text-white">Net à payer</span>
                  <span className="font-bold text-xl text-green-600">
                    {(analysis.details.netAPayer || analysis.resume.salaireNet).toLocaleString()} MAD
                  </span>
                </div>
              </div>
            </div>
          </div>
        )

      case 'anomalies':
        return (
          <div className="space-y-4">
            {(analysis.anomalies || []).map((anomalie, index) => {
              const isWarn = (anomalie.type || '').toLowerCase() === 'warning' || anomalie.impact === 'Moyen'
              return (
                <div
                  key={index}
                  className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700"
                >
                  <div className="flex items-start space-x-3">
                    {isWarn ? (
                      <AlertTriangle className="h-6 w-6 text-orange-500 mt-1" />
                    ) : (
                      <CheckCircle className="h-6 w-6 text-blue-500 mt-1" />
                    )}
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 dark:text-white">
                        {anomalie.title}
                      </h3>
                      <p className="text-gray-600 dark:text-gray-300 mt-1">
                        {anomalie.description}
                      </p>
                      <span
                        className={`inline-block mt-2 px-2 py-1 rounded-full text-xs font-medium ${
                          anomalie.impact === 'Moyen'
                            ? 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400'
                            : anomalie.impact === 'Positif'
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                            : anomalie.impact === 'Élevé'
                            ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                            : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                        }`}
                      >
                        Impact: {anomalie.impact}
                      </span>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )

      case 'conseils':
        return (
          <div className="space-y-4">
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Recommandations Personnalisées
              </h3>
              <div className="space-y-3">
                {(analysis.recommandations || []).map((conseil, index) => (
                  <div
                    key={index}
                    className="flex items-start space-x-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg"
                  >
                    <TrendingUp className="h-5 w-5" />
                    <p className="text-gray-700 dark:text-gray-300">{conseil}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-slate-800 to-slate-900 p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">Analyse du Bulletin de Paie</h2>
              <p className="opacity-90">{data.fileName}</p>
            </div>
            <div className="flex items-center space-x-2">
              <button className="p-2 hover:bg-white/20 rounded-lg transition-colors">
                <Download className="h-5 w-5" />
              </button>
              <button className="p-2 hover:bg-white/20 rounded-lg transition-colors">
                <Share2 className="h-5 w-5" />
              </button>
              <button onClick={onClose} className="p-2 hover:bg-white/20 rounded-lg transition-colors">
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
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 flex items-center justify-center space-x-2 py-4 px-6 font-medium transition-all duration-200 ${
                    isActive
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
        <div className="p-6 overflow-y-auto max-h-[60vh]">{renderTabContent()}</div>
      </div>
    </div>
  )
}
