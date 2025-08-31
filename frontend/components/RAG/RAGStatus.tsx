'use client'

import React, { useState, useEffect } from 'react'
<<<<<<< HEAD
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
=======
import { Card, CardContent, CardHeader, CardTitle } from '../UI/Card'
import { Button } from '../UI/button'
import { Alert, AlertDescription } from '../UI/alert'
import { Badge } from '../UI/badge'
>>>>>>> 5e0de77 (Auth commit)
import { 
  CheckCircle, 
  XCircle, 
  Loader2, 
  Database, 
  Search, 
  AlertTriangle,
  RefreshCw
} from 'lucide-react'
<<<<<<< HEAD
import { ragService } from '@/lib/api'
=======
// import { ragService } from '@/lib/api'
>>>>>>> 5e0de77 (Auth commit)

interface RAGStatusData {
  isInitialized: boolean
  profilesCount: number
  indexExists: boolean
  message: string
}

export default function RAGStatus() {
  const [status, setStatus] = useState<RAGStatusData | null>(null)
  const [loading, setLoading] = useState(true)
  const [initializing, setInitializing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const checkStatus = async () => {
    try {
      setLoading(true)
      setError(null)
<<<<<<< HEAD
      const data = await ragService.getStatus()
=======
      // const data = await ragService.getStatus()
    const data = { isInitialized: false, profilesCount: 0, indexExists: false, message: 'Système non initialisé' }
>>>>>>> 5e0de77 (Auth commit)
      setStatus(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de la vérification du statut')
    } finally {
      setLoading(false)
    }
  }

  const initializeRAG = async () => {
    try {
      setInitializing(true)
      setError(null)
<<<<<<< HEAD
      await ragService.initialize()
=======
              // await ragService.initialize()
>>>>>>> 5e0de77 (Auth commit)
      
      // Attendre un peu puis vérifier le statut
      setTimeout(() => {
        checkStatus()
        setInitializing(false)
      }, 2000)
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de l\'initialisation')
      setInitializing(false)
    }
  }

  useEffect(() => {
    checkStatus()
  }, [])

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center p-6">
          <Loader2 className="h-6 w-6 animate-spin mr-2" />
          <span>Vérification du statut RAG...</span>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Database className="h-5 w-5" />
          Statut du système RAG LinkedIn
          <Button
            variant="outline"
            size="sm"
            onClick={checkStatus}
            disabled={loading}
          >
            <RefreshCw className="h-4 w-4" />
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {status && (
          <>
            {/* Statut général */}
            <div className="flex items-center gap-2">
              {status.isInitialized ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <XCircle className="h-5 w-5 text-red-600" />
              )}
              <span className="font-medium">
                {status.isInitialized ? 'Système initialisé' : 'Système non initialisé'}
              </span>
              <Badge 
                variant={status.isInitialized ? "default" : "destructive"}
                className={status.isInitialized ? "bg-green-600" : ""}
              >
                {status.isInitialized ? 'Prêt' : 'Non prêt'}
              </Badge>
            </div>

            {/* Détails */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
                <Database className="h-4 w-4 text-blue-600" />
                <div>
                  <div className="text-sm font-medium">Profils LinkedIn</div>
                  <div className="text-lg font-bold text-blue-600">
                    {status.profilesCount.toLocaleString()}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
                <Search className="h-4 w-4 text-purple-600" />
                <div>
                  <div className="text-sm font-medium">Index de recherche</div>
                  <div className="text-lg font-bold text-purple-600">
                    {status.indexExists ? 'Créé' : 'Non créé'}
                  </div>
                </div>
              </div>
            </div>

            {/* Message */}
            <Alert>
              <AlertDescription>{status.message}</AlertDescription>
            </Alert>

            {/* Actions */}
            {!status.isInitialized && (
              <div className="pt-4">
                <Button 
                  onClick={initializeRAG}
                  disabled={initializing}
                  className="w-full"
                >
                  {initializing ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      Initialisation en cours...
                    </>
                  ) : (
                    <>
                      <Database className="h-4 w-4 mr-2" />
                      Initialiser le système RAG
                    </>
                  )}
                </Button>
                
                {status.profilesCount === 0 && (
                  <Alert className="mt-4">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      Assurez-vous que le fichier <code>linkedin_scraped_fixed.json</code> 
                      est placé dans le dossier <code>backend/data/</code>
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            )}

            {/* Informations d'utilisation */}
            {status.isInitialized && (
              <div className="pt-4 border-t">
                <h4 className="font-medium mb-2">Fonctionnalités disponibles :</h4>
                <ul className="text-sm space-y-1 text-gray-600">
                  <li>✅ Coaching de carrière enrichi avec données LinkedIn</li>
                  <li>✅ Recherche de profils similaires</li>
                  <li>✅ Analyse des compétences du marché</li>
                  <li>✅ Insights sectoriels</li>
                </ul>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  )
}
