'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Users, Building, MapPin, TrendingUp, Star, Download, Share2, X } from 'lucide-react'
import ActionButtons from '../UI/ActionButtons'

interface LinkedInInsightsProps {
  insights: {
    profilesAnalyzed: number
    topSkills: string[]
    targetCompanies: string[]
    commonTitles: string[]
    locations: string[]
  }
  recommendations?: Array<{
    profileReference: string
    recommendation: string
    similarity: number
  }>
}

export default function LinkedInInsights({ insights, recommendations }: LinkedInInsightsProps) {
  const [showModal, setShowModal] = useState(false);

  const insightsText = `
Insights LinkedIn - Analyse des profils

📊 Statistiques:
- Profils analysés: ${insights.profilesAnalyzed}
- Compétences identifiées: ${insights.topSkills.length}
- Entreprises cibles: ${insights.targetCompanies.length}
- Postes identifiés: ${insights.commonTitles.length}

🚀 Compétences les plus demandées:
${insights.topSkills.map((skill, index) => `${index + 1}. ${skill}`).join('\n')}

🏢 Entreprises populaires:
${insights.targetCompanies.map((company, index) => `${index + 1}. ${company}`).join('\n')}

👥 Postes typiques dans ce domaine:
${insights.commonTitles.map((title, index) => `${index + 1}. ${title}`).join('\n')}

📍 Localisations populaires:
${insights.locations.map((location, index) => `${index + 1}. ${location}`).join('\n')}

${recommendations && recommendations.length > 0 ? `
⭐ Recommandations basées sur des profils similaires:
${recommendations.map((rec, index) => `
${index + 1}. Basé sur: ${rec.profileReference}
   Similarité: ${Math.round(rec.similarity * 100)}%
   Recommandation: ${rec.recommendation}
`).join('\n')}
` : ''}
  `.trim();

  return (
    <>
      <div className="space-y-6">
        {/* En-tête avec statistiques */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5 text-blue-600" />
                Insights LinkedIn
              </CardTitle>
              <Button
                onClick={() => setShowModal(true)}
                variant="outline"
                size="sm"
              >
                📋 Voir en détail
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{insights.profilesAnalyzed}</div>
                <div className="text-sm text-gray-600">Profils analysés</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{insights.topSkills.length}</div>
                <div className="text-sm text-gray-600">Compétences identifiées</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">{insights.targetCompanies.length}</div>
                <div className="text-sm text-gray-600">Entreprises cibles</div>
              </div>
              <div className="text-center p-4 bg-orange-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">{insights.commonTitles.length}</div>
                <div className="text-sm text-gray-600">Postes identifiés</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Compétences populaires */}
        {insights.topSkills.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-green-600" />
                Compétences les plus demandées
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {insights.topSkills.map((skill, index) => (
                  <Badge 
                    key={index} 
                    variant={index < 3 ? "default" : "secondary"}
                    className={index < 3 ? "bg-green-600 hover:bg-green-700" : ""}
                  >
                    {skill}
                    {index < 3 && <Star className="h-3 w-3 ml-1" />}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Entreprises cibles */}
        {insights.targetCompanies.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building className="h-5 w-5 text-blue-600" />
                Entreprises populaires
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {insights.targetCompanies.map((company, index) => (
                  <div 
                    key={index}
                    className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg"
                  >
                    <Building className="h-4 w-4 text-gray-500" />
                    <span className="text-sm">{company}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Postes typiques */}
        {insights.commonTitles.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5 text-purple-600" />
                Postes typiques dans ce domaine
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {insights.commonTitles.map((title, index) => (
                  <div 
                    key={index}
                    className="p-2 bg-purple-50 rounded-lg border-l-4 border-purple-600"
                  >
                    <span className="text-sm font-medium">{title}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Localisations */}
        {insights.locations.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="h-5 w-5 text-red-600" />
                Localisations populaires
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {insights.locations.map((location, index) => (
                  <Badge key={index} variant="outline" className="border-red-200">
                    <MapPin className="h-3 w-3 mr-1" />
                    {location}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Recommandations basées sur les profils */}
        {recommendations && recommendations.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Star className="h-5 w-5 text-yellow-600" />
                Recommandations basées sur des profils similaires
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recommendations.map((rec, index) => (
                  <div 
                    key={index}
                    className="p-4 bg-yellow-50 rounded-lg border border-yellow-200"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="text-sm font-medium text-yellow-800">
                        Basé sur: {rec.profileReference}
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {Math.round(rec.similarity * 100)}% similaire
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-700">{rec.recommendation}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Fenêtre modale */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="border-b p-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold">Insights LinkedIn - Vue détaillée</h2>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowModal(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <X className="h-5 w-5" />
                </Button>
              </div>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
              <div className="space-y-4">
                <div className="bg-gray-50 p-4 rounded-md whitespace-pre-line text-sm">
                  {insightsText}
                </div>

                <ActionButtons
                  content={insightsText}
                  filename="insights-linkedin.txt"
                  title="Insights LinkedIn"
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
