'use client'

import { useState } from 'react'
import { Target, TrendingUp, BookOpen, Users, Award, Calendar, Download, Share2, CheckCircle } from 'lucide-react'

interface CareerData {
  objectif: string
  competences: string[]
  secteur: string
  linkedInDataUsed?: boolean
  planCarriere: {
    etapes: Array<{
      titre: string
      duree: string
      description: string
      competencesRequises: string[]
      salaireEstime: number
    }>
  }
  scriptNegociation: {
    points: string[]
    arguments: string[]
    conseils: string[]
  }

  formationsRecommandees: Array<{
    titre: string
    duree: string
    priorite: 'high' | 'medium' | 'low'
    description: string
  }>

  planningFormations: Array<{
    mois: string
    formation: string
  }>

  objectifsSMART: Array<{
    horizon: string
    objectif: string
    smart_tags: string[]
  }>

  suiviProgres: Array<{
    titre: string
    progression: string
  }>

  // Nouvelles propriétés pour les insights LinkedIn
  linkedinInsights?: {
    profilesAnalyzed: number
    topSkills: string[]
    targetCompanies: string[]
    commonTitles: string[]
    locations: string[]
  }

  recommendationsBasedOnProfiles?: Array<{
    profileReference: string
    recommendation: string
    similarity: number
  }>
}

interface CareerCoachingResultProps {
  data: CareerData
  onClose: () => void
}

export default function CareerCoachingResult({ data, onClose }: CareerCoachingResultProps) {
  const [activeTab, setActiveTab] = useState('plan')
   if (!data || !data.planCarriere || !data.planCarriere.etapes) {
    return (
      <div className="text-center p-6 text-red-500">
        Erreur : données de carrière non disponibles.
      </div>
    )
  }
  const tabs = [
    { id: 'plan', label: 'Plan de Carrière', icon: TrendingUp },
    { id: 'formations', label: 'Formations', icon: BookOpen },
    { id: 'negociation', label: 'Négociation', icon: Users },
    { id: 'objectifs', label: 'Objectifs', icon: Target }
  ]

  const renderTabContent = () => {
    switch (activeTab) {
      case 'plan':
        return (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-purple-50 to-cyan-50 dark:from-purple-900/20 dark:to-cyan-900/20 rounded-xl p-6 border border-purple-200 dark:border-purple-800">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Votre Parcours Professionnel</h3>
              <p className="text-gray-600 dark:text-gray-300">
                Basé sur votre objectif : <span className="font-semibold text-purple-600 dark:text-purple-400">"{data.objectif}"</span>
              </p>
            </div>

            <div className="space-y-6">
              {data?.planCarriere?.etapes?.map((etape, index) => (

                <div key={index} className="relative">
                  {/* Timeline line */}
                  {index < data.planCarriere.etapes.length - 1 && (
                    <div className="absolute left-6 top-16 w-0.5 h-16 bg-gradient-to-b from-purple-500 to-cyan-400" />
                  )}
                  
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-r from-purple-500 to-cyan-400 rounded-full flex items-center justify-center text-white font-bold">
                      {index + 1}
                    </div>
                    
                    <div className="flex-1 bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm">
                      <div className="flex items-start justify-between mb-3">
                        <h4 className="text-lg font-semibold text-gray-900 dark:text-white">{etape.titre}</h4>
                        <div className="flex items-center space-x-4">
                          <span className="text-sm text-purple-600 dark:text-purple-400 font-medium">{etape.duree}</span>
                          <span className="text-sm font-semibold text-green-600">
                            {etape.salaireEstime.toLocaleString()} MAD
                          </span>
                        </div>
                      </div>
                      
                      <p className="text-gray-600 dark:text-gray-300 mb-4">{etape.description}</p>
                      
                      <div>
                        <h5 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">Compétences requises :</h5>
                        <div className="flex flex-wrap gap-2">
                          {etape.competencesRequises.map((competence, compIndex) => (
                            <span 
                              key={compIndex}
                              className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400 rounded-full text-sm font-medium"
                            >
                              {competence}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )

      case 'formations':
  return (
    <div className="space-y-6">
      {/* 📘 Formations recommandées */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Formations Recommandées
        </h3>
        <p className="text-gray-600 dark:text-gray-300 mb-6">
          Ces formations vous aideront à atteindre vos objectifs de carrière plus rapidement.
        </p>

        <div className="space-y-4">
          {data.formationsRecommandees.map((formation, index) => (
            <div
              key={index}
              className="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
            >
              <div className="flex items-start justify-between mb-3">
                <h4 className="font-semibold text-gray-900 dark:text-white">
                  {formation.titre}
                </h4>
                <div className="flex items-center space-x-2">
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${
                      formation.priorite === 'high'
                        ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                        : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
                    }`}
                  >
                    {formation.priorite === 'high'
                      ? 'Priorité élevée'
                      : 'Priorité moyenne'}
                  </span>
                  <span className="text-sm text-purple-600 dark:text-purple-400 font-medium">
                    {formation.duree}
                  </span>
                </div>
              </div>
              <p className="text-gray-600 dark:text-gray-300">
                {formation.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* 📆 Calendrier de formation dynamique */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Planning de Formation
        </h3>
        <div className="space-y-3">
          {data.planningFormations.map((item, index) => (
            <div
              key={index}
              className="flex items-center space-x-3 p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg"
            >
              <Calendar className="h-5 w-5 text-purple-500" />
              <div>
                <p className="font-medium text-gray-900 dark:text-white">
                  {item.mois}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {item.formation}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );


      case 'negociation':
  return (
    <div className="space-y-6">
      {/* 🗣️ Script de négociation */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Script de Négociation
        </h3>
        <p className="text-gray-600 dark:text-gray-300 mb-6">
          Utilisez ces points clés pour négocier efficacement votre évolution de carrière.
        </p>

        <div className="space-y-6">
          {/* ✅ Points de discussion */}
          <div>
            <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center space-x-2">
              <Users className="h-5 w-5 text-purple-500" />
              <span>Points de Discussion</span>
            </h4>
            <div className="space-y-3">
              {data.scriptNegociation.points.map((point, index) => (
                <div
                  key={index}
                  className="flex items-start space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                >
                  <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                  <p className="text-gray-700 dark:text-gray-300">{point}</p>
                </div>
              ))}
            </div>
          </div>

          {/* 💡 Arguments clés */}
          <div>
            <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center space-x-2">
              <Award className="h-5 w-5 text-blue-500" />
              <span>Arguments Clés</span>
            </h4>
            <div className="space-y-3">
              {data.scriptNegociation.arguments.map((argument, index) => (
                <div
                  key={index}
                  className="flex items-start space-x-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg"
                >
                  <TrendingUp className="h-5 w-5 text-blue-500 mt-0.5" />
                  <p className="text-gray-700 dark:text-gray-300">{argument}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 🧠 Conseils personnalisés */}
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl p-6 border border-green-200 dark:border-green-800">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Conseils pour Réussir
        </h3>
        <div className="space-y-3">
          {data.scriptNegociation.conseils.map((conseil, index) => (
            <div key={index} className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                {index + 1}
              </div>
              <p className="text-gray-700 dark:text-gray-300">{conseil}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

    case 'objectifs':
  return (
    <div className="space-y-6">
      {/* 🎯 Objectifs SMART */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Objectifs SMART</h3>
        <p className="text-gray-600 dark:text-gray-300 mb-6">
          Voici vos objectifs structurés selon la méthode SMART (Spécifique, Mesurable, Atteignable, Réaliste, Temporel).
        </p>

        <div className="space-y-4">
          {data.objectifsSMART.map((objectif, index) => (
            <div key={index} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2">{objectif.horizon}</h4>
              <p className="text-gray-600 dark:text-gray-300 mb-3">{objectif.objectif}</p>
              <div className="flex flex-wrap gap-2">
                {objectif.smart_tags.map((tag, i) => {
                  const colorMap = {
                    'Spécifique': 'purple',
                    'Mesurable': 'blue',
                    'Temporel': 'green',
                    'Atteignable': 'yellow',
                    'Réaliste': 'red',
                  } as const;

                  const color = colorMap[tag as keyof typeof colorMap] || 'gray';
                  return (
                    <span
                      key={i}
                      className={`px-2 py-1 bg-${color}-100 dark:bg-${color}-900/30 text-${color}-800 dark:text-${color}-400 rounded text-sm`}
                    >
                      {tag} ✓
                    </span>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 📈 Suivi des Progrès */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Suivi des Progrès</h3>
        <div className="space-y-4">
          {data.suiviProgres.map((item, index) => {
            const colorMap = {
              'Certification en cours': 'purple',
              'Développement leadership': 'blue',
              'Réseau professionnel': 'green',
            } as const;

            const color = colorMap[item.titre as keyof typeof colorMap] || 'gray';

            return (
              <div key={index}>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{item.titre}</span>
                  <span className={`text-sm text-${color}-600 dark:text-${color}-400`}>
                    {item.progression}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className={`bg-${color}-500 h-2 rounded-full`}
                    style={{ width: `${item.progression}%` }}
                  ></div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );

      default:
        return null
    }
  }
 if (!data || !data.planCarriere || !data.planCarriere.etapes) {
  return (
    <div className="text-center p-6 text-red-500">
      Erreur : données de carrière non disponibles.
    </div>
  )
}

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-500 to-cyan-400 p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">Plan de Carrière Personnalisé</h2>
              <p className="opacity-90">Secteur: {data.secteur}</p>
            </div>
            <div className="flex items-center space-x-2">
              <button className="p-2 hover:bg-white/20 rounded-lg transition-colors">
                <Download className="h-5 w-5" />
              </button>
              <button className="p-2 hover:bg-white/20 rounded-lg transition-colors">
                <Share2 className="h-5 w-5" />
              </button>
              <button 
                onClick={onClose}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              >
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
