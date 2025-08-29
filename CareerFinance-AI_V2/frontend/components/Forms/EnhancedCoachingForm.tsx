'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { 
  Loader2, 
  Target, 
  Plus, 
  X, 
  Database, 
  Sparkles,
  AlertTriangle 
} from 'lucide-react'
import { ragService } from '@/lib/api'

interface EnhancedCoachingFormProps {
  onResult: (data: any) => void
  ragStatus?: {
    isInitialized: boolean
    profilesCount: number
  }
}

export default function EnhancedCoachingForm({ onResult, ragStatus }: EnhancedCoachingFormProps) {
  const [formData, setFormData] = useState({
    goal: '',
    skills: [] as string[],
    sector: '',
    useLinkedInData: true
  })
  
  const [newSkill, setNewSkill] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const addSkill = () => {
    if (newSkill.trim() && !formData.skills.includes(newSkill.trim())) {
      setFormData(prev => ({
        ...prev,
        skills: [...prev.skills, newSkill.trim()]
      }))
      setNewSkill('')
    }
  }

  const removeSkill = (skillToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      skills: prev.skills.filter(skill => skill !== skillToRemove)
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.goal.trim() || !formData.sector.trim() || formData.skills.length === 0) {
      setError('Veuillez remplir tous les champs obligatoires')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const result = await ragService.enhancedCoaching(formData)
      onResult(result)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de la génération du plan de carrière')
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      addSkill()
    }
  }

  const isRAGAvailable = ragStatus?.isInitialized && ragStatus?.profilesCount > 0

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Target className="h-5 w-5 text-purple-600" />
          Coaching de Carrière Enrichi
          {isRAGAvailable && (
            <Badge className="bg-green-100 text-green-800 border-green-200">
              <Database className="h-3 w-3 mr-1" />
              LinkedIn disponible
            </Badge>
          )}
        </CardTitle>
        <p className="text-sm text-gray-600">
          Générez un plan de carrière personnalisé 
          {isRAGAvailable && ' enrichi avec des données LinkedIn réelles'}
        </p>
      </CardHeader>
      
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Objectif de carrière */}
          <div className="space-y-2">
            <Label htmlFor="goal">Objectif de carrière *</Label>
            <Textarea
              id="goal"
              placeholder="Ex: Devenir développeur senior, évoluer vers un poste de management..."
              value={formData.goal}
              onChange={(e) => setFormData(prev => ({ ...prev, goal: e.target.value }))}
              className="min-h-[80px]"
            />
          </div>

          {/* Secteur */}
          <div className="space-y-2">
            <Label htmlFor="sector">Secteur d'activité *</Label>
            <Input
              id="sector"
              placeholder="Ex: Développement web, Marketing digital, Finance..."
              value={formData.sector}
              onChange={(e) => setFormData(prev => ({ ...prev, sector: e.target.value }))}
            />
          </div>

          {/* Compétences */}
          <div className="space-y-2">
            <Label>Compétences actuelles *</Label>
            <div className="flex gap-2">
              <Input
                placeholder="Ajouter une compétence..."
                value={newSkill}
                onChange={(e) => setNewSkill(e.target.value)}
                onKeyPress={handleKeyPress}
              />
              <Button
                type="button"
                onClick={addSkill}
                variant="outline"
                size="icon"
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            
            {formData.skills.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {formData.skills.map((skill, index) => (
                  <Badge
                    key={index}
                    variant="secondary"
                    className="flex items-center gap-1"
                  >
                    {skill}
                    <button
                      type="button"
                      onClick={() => removeSkill(skill)}
                      className="ml-1 hover:text-red-600"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}
          </div>

          {/* Option LinkedIn */}
          {isRAGAvailable && (
            <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-center gap-2">
                <Database className="h-5 w-5 text-blue-600" />
                <div>
                  <Label htmlFor="useLinkedIn" className="text-sm font-medium">
                    Utiliser les données LinkedIn
                  </Label>
                  <p className="text-xs text-gray-600">
                    Enrichir les recommandations avec {ragStatus?.profilesCount.toLocaleString()} profils LinkedIn
                  </p>
                </div>
              </div>
              <Switch
                id="useLinkedIn"
                checked={formData.useLinkedInData}
                onCheckedChange={(checked) => 
                  setFormData(prev => ({ ...prev, useLinkedInData: checked }))
                }
              />
            </div>
          )}

          {!isRAGAvailable && (
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                Le système LinkedIn n'est pas disponible. Le coaching utilisera uniquement l'IA générative.
              </AlertDescription>
            </Alert>
          )}

          {/* Bouton de soumission */}
          <Button
            type="submit"
            disabled={loading || !formData.goal.trim() || !formData.sector.trim() || formData.skills.length === 0}
            className="w-full"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Génération en cours...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4 mr-2" />
                Générer mon plan de carrière
                {formData.useLinkedInData && isRAGAvailable && ' (avec LinkedIn)'}
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
