'use client'

import React, { useState } from 'react'
<<<<<<< HEAD
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
=======
import { Card, CardContent, CardHeader, CardTitle } from '../UI/Card'
import { Button } from '../UI/button'
import { Input } from '../UI/input'
import { Badge } from '../UI/badge'
import { Alert, AlertDescription } from '../UI/alert'
>>>>>>> 5e0de77 (Auth commit)
import { 
  Search, 
  User, 
  Building, 
  MapPin, 
  Star, 
  Loader2,
  Users,
  AlertTriangle 
} from 'lucide-react'
<<<<<<< HEAD
import { ragService } from '@/lib/api'
=======
// import { ragService } from '@/lib/api'
>>>>>>> 5e0de77 (Auth commit)

interface Profile {
  name: string
  title: string
  company: string
  location: string
  summary: string
  skills: string[]
  connections: number
}

interface SearchResult {
  rank: number
  score: number
  profile: Profile
}

interface ProfileSearchProps {
  ragStatus?: {
    isInitialized: boolean
    profilesCount: number
  }
}

export default function ProfileSearch({ ragStatus }: ProfileSearchProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasSearched, setHasSearched] = useState(false)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!query.trim()) {
      setError('Veuillez saisir une requête de recherche')
      return
    }

    if (!ragStatus?.isInitialized) {
      setError('Le système RAG n\'est pas initialisé')
      return
    }

    setLoading(true)
    setError(null)
    setHasSearched(true)

    try {
<<<<<<< HEAD
      const response = await ragService.searchProfiles(query.trim(), 10)
=======
      // const response = await ragService.searchProfiles(query.trim(), 10)
      const response = { profiles: [], total: 0 }
>>>>>>> 5e0de77 (Auth commit)
      setResults(response.profiles || [])
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de la recherche')
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-100'
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  const isRAGAvailable = ragStatus?.isInitialized && ragStatus?.profilesCount > 0

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Search className="h-5 w-5 text-blue-600" />
          Recherche de Profils LinkedIn
        </CardTitle>
        <p className="text-sm text-gray-600">
          Trouvez des professionnels similaires à votre profil ou objectif de carrière
        </p>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {!isRAGAvailable && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              Le système RAG n'est pas disponible. Veuillez l'initialiser d'abord.
            </AlertDescription>
          </Alert>
        )}

        {/* Formulaire de recherche */}
        <form onSubmit={handleSearch} className="flex gap-2">
          <Input
            placeholder="Ex: développeur React senior, data scientist Python..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={!isRAGAvailable}
            className="flex-1"
          />
          <Button
            type="submit"
            disabled={loading || !isRAGAvailable || !query.trim()}
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Search className="h-4 w-4" />
            )}
          </Button>
        </form>

        {error && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Statistiques */}
        {isRAGAvailable && (
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <div className="flex items-center gap-1">
              <Users className="h-4 w-4" />
              {ragStatus.profilesCount.toLocaleString()} profils disponibles
            </div>
            {hasSearched && results.length > 0 && (
              <div className="flex items-center gap-1">
                <Star className="h-4 w-4" />
                {results.length} résultats trouvés
              </div>
            )}
          </div>
        )}

        {/* Résultats */}
        {hasSearched && results.length === 0 && !loading && !error && (
          <Alert>
            <AlertDescription>
              Aucun profil trouvé pour cette recherche. Essayez avec des termes différents.
            </AlertDescription>
          </Alert>
        )}

        {results.length > 0 && (
          <div className="space-y-4">
            <h3 className="font-semibold text-gray-900">
              Profils similaires trouvés
            </h3>
            
            <div className="space-y-4">
              {results.map((result, index) => (
                <Card key={index} className="border border-gray-200">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                          {result.profile.name.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <h4 className="font-semibold text-gray-900">
                            {result.profile.name}
                          </h4>
                          <p className="text-sm text-gray-600">
                            {result.profile.title}
                          </p>
                        </div>
                      </div>
                      
                      <Badge 
                        className={`${getScoreColor(result.score)} border-0`}
                      >
                        {Math.round(result.score * 100)}% similaire
                      </Badge>
                    </div>

                    <div className="space-y-2 mb-3">
                      {result.profile.company && (
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <Building className="h-4 w-4" />
                          {result.profile.company}
                        </div>
                      )}
                      
                      {result.profile.location && (
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <MapPin className="h-4 w-4" />
                          {result.profile.location}
                        </div>
                      )}
                    </div>

                    {result.profile.summary && (
                      <p className="text-sm text-gray-700 mb-3 line-clamp-2">
                        {result.profile.summary}
                      </p>
                    )}

                    {result.profile.skills && result.profile.skills.length > 0 && (
                      <div className="space-y-2">
                        <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                          Compétences principales
                        </p>
                        <div className="flex flex-wrap gap-1">
                          {result.profile.skills.slice(0, 6).map((skill, skillIndex) => (
                            <Badge
                              key={skillIndex}
                              variant="outline"
                              className="text-xs"
                            >
                              {skill}
                            </Badge>
                          ))}
                          {result.profile.skills.length > 6 && (
                            <Badge variant="outline" className="text-xs">
                              +{result.profile.skills.length - 6} autres
                            </Badge>
                          )}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
