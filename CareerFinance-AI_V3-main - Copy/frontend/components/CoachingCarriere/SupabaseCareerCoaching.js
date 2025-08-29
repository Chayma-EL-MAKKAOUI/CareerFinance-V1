'use client';
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../UI/Card';
import Button from '../UI/Button';
import CareerPlan from './CareerPlan';
import NegotiationScript from './NegotiationScript';

const SupabaseCareerCoaching = () => {
  const [formData, setFormData] = useState({
    user_id: 1, // À remplacer par l'ID de l'utilisateur connecté
    goal: '',
    skills: '',
    sector: '',
    useLinkedInData: true
  });
  
  const [loading, setLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);
  const [careerPlan, setCareerPlan] = useState(null);
  const [error, setError] = useState(null);
  const [coachingHistory, setCoachingHistory] = useState([]);
  const [showCareerPlan, setShowCareerPlan] = useState(false);
  const [showNegotiationScript, setShowNegotiationScript] = useState(false);

  const API_BASE = '/api/supabase-career';

  // Vérifier le statut du système au chargement
  useEffect(() => {
    checkSystemStatus();
    loadCoachingHistory();
  }, []);

  const checkSystemStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/status`);
      const data = await response.json();
      setSystemStatus(data);
    } catch (error) {
      console.error('Erreur lors de la vérification du statut:', error);
    }
  };

  const initializeSystem = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/initialize`, {
        method: 'POST'
      });
      const data = await response.json();
      console.log('Système initialisé:', data);
      
      // Attendre un peu puis recharger le statut
      setTimeout(() => {
        checkSystemStatus();
        setLoading(false);
      }, 2000);
    } catch (error) {
      console.error('Erreur lors de l\'initialisation:', error);
      setLoading(false);
    }
  };

  const loadCoachingHistory = async () => {
    try {
      const response = await fetch(`${API_BASE}/history/${formData.user_id}`);
      const data = await response.json();
      setCoachingHistory(data.sessions || []);
    } catch (error) {
      console.error('Erreur lors du chargement de l\'historique:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setCareerPlan(null);

    try {
      // Préparer les données
      const requestData = {
        ...formData,
        skills: formData.skills.split(',').map(skill => skill.trim()).filter(skill => skill)
      };

      const response = await fetch(`${API_BASE}/coaching`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      });

      if (!response.ok) {
        throw new Error(`Erreur ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setCareerPlan(data);
      
      // Recharger l'historique
      loadCoachingHistory();
    } catch (error) {
      console.error('Erreur lors de la génération du plan:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const searchSimilarProfiles = async () => {
    if (!formData.goal && !formData.skills) {
      setError('Veuillez remplir au moins l\'objectif ou les compétences');
      return;
    }

    setLoading(true);
    try {
      const query = `${formData.goal} ${formData.skills}`.trim();
      const response = await fetch(`${API_BASE}/search-profiles`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query,
          topK: 5
        })
      });

      if (!response.ok) {
        throw new Error(`Erreur ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Profils similaires:', data);
      // Ici vous pourriez afficher les profils dans une modal ou une nouvelle section
      alert(`${data.resultsCount} profils similaires trouvés!`);
    } catch (error) {
      console.error('Erreur lors de la recherche:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveCareerPlan = (updatedPlan) => {
    setCareerPlan(prev => ({
      ...prev,
      planCarriere: updatedPlan
    }));
  };

  const handleSaveNegotiationScript = (updatedScript) => {
    setCareerPlan(prev => ({
      ...prev,
      scriptNegociation: updatedScript
    }));
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Statut du système */}
      {systemStatus && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className={`w-3 h-3 rounded-full ${systemStatus.isInitialized ? 'bg-green-500' : 'bg-red-500'}`}></span>
              Statut du système
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="font-medium">Initialisé:</span> {systemStatus.isInitialized ? 'Oui' : 'Non'}
              </div>
              <div>
                <span className="font-medium">Profils:</span> {systemStatus.profilesCount}
              </div>
              <div>
                <span className="font-medium">Chunks:</span> {systemStatus.chunksCount}
              </div>
              <div>
                <span className="font-medium">Index:</span> {systemStatus.indexExists ? 'Prêt' : 'Manquant'}
              </div>
            </div>
            <p className="text-gray-600 mt-2">{systemStatus.message}</p>
            
            {!systemStatus.isInitialized && (
              <Button 
                onClick={initializeSystem} 
                disabled={loading}
                className="mt-3"
              >
                {loading ? 'Initialisation...' : 'Initialiser le système'}
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Formulaire de coaching */}
      <Card>
        <CardHeader>
          <CardTitle>Plan de carrière personnalisé</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Objectif professionnel *
              </label>
              <textarea 
                name="goal"
                value={formData.goal}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows="3"
                placeholder="Ex: Devenir Data Science Manager dans les 2 prochaines années"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Compétences clés (séparées par des virgules)
              </label>
              <input 
                type="text" 
                name="skills"
                value={formData.skills}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ex: Python, Machine Learning, Leadership, SQL"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Secteur d'activité
              </label>
              <input 
                type="text" 
                name="sector"
                value={formData.sector}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ex: Technologie, Intelligence Artificielle, Finance"
              />
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="useLinkedInData"
                name="useLinkedInData"
                checked={formData.useLinkedInData}
                onChange={(e) => setFormData(prev => ({ ...prev, useLinkedInData: e.target.checked }))}
                className="mr-2"
              />
              <label htmlFor="useLinkedInData" className="text-sm text-gray-700">
                Utiliser les données LinkedIn pour enrichir l'analyse
              </label>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Button 
                type="submit" 
                disabled={loading || !systemStatus?.isInitialized}
                className="w-full"
              >
                {loading ? 'Génération...' : 'Générer mon plan de carrière'}
              </Button>
              <Button 
                type="button"
                variant="outline" 
                onClick={searchSimilarProfiles}
                disabled={loading || !systemStatus?.isInitialized}
                className="w-full"
              >
                Rechercher des profils similaires
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Affichage des erreurs */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="text-red-700">
              <strong>Erreur:</strong> {error}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Résultat du plan de carrière */}
      {careerPlan && (
        <Card>
          <CardHeader>
            <CardTitle>Votre plan de carrière</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="font-medium">Objectif:</span> {careerPlan.objectif}
                </div>
                <div>
                  <span className="font-medium">Secteur:</span> {careerPlan.secteur}
                </div>
                <div>
                  <span className="font-medium">LinkedIn utilisé:</span> {careerPlan.linkedInDataUsed ? 'Oui' : 'Non'}
                </div>
              </div>

              {/* Boutons d'ouverture des fenêtres */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {careerPlan.planCarriere && (
                  <Button
                    onClick={() => setShowCareerPlan(true)}
                    className="w-full bg-blue-600 hover:bg-blue-700"
                  >
                    📋 Voir le plan de carrière
                  </Button>
                )}
                
                {careerPlan.scriptNegociation && (
                  <Button
                    onClick={() => setShowNegotiationScript(true)}
                    className="w-full bg-purple-600 hover:bg-purple-700"
                  >
                    💬 Voir le script de négociation
                  </Button>
                )}
              </div>

              {careerPlan.linkedInInsights && (
                <div>
                  <h4 className="font-medium mb-2">Insights LinkedIn:</h4>
                  <div className="bg-blue-50 p-4 rounded-md">
                    <p><strong>Profils analysés:</strong> {careerPlan.linkedInInsights.profiles_analyzed}</p>
                    {careerPlan.linkedInInsights.top_profiles && (
                      <div className="mt-2">
                        <p className="font-medium">Profils de référence:</p>
                        <ul className="list-disc list-inside text-sm">
                          {careerPlan.linkedInInsights.top_profiles.slice(0, 3).map((profile, index) => (
                            <li key={index}>
                              {profile.nom} - {profile.titre} (score: {profile.score.toFixed(3)})
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Historique des sessions */}
      {coachingHistory.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Historique des sessions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {coachingHistory.slice(0, 5).map((session, index) => (
                <div key={session.id} className="border-b border-gray-200 pb-3 last:border-b-0">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-medium">{session.objectif}</h4>
                      <p className="text-sm text-gray-600">
                        Compétences: {session.competences ? JSON.parse(session.competences).join(', ') : 'N/A'}
                      </p>
                      <p className="text-sm text-gray-600">Secteur: {session.secteur}</p>
                    </div>
                    <span className="text-xs text-gray-500">
                      {new Date(session.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Fenêtres modales */}
      {careerPlan?.planCarriere && (
        <CareerPlan
          plan={careerPlan.planCarriere}
          isOpen={showCareerPlan}
          onClose={() => setShowCareerPlan(false)}
          onSave={handleSaveCareerPlan}
        />
      )}

      {careerPlan?.scriptNegociation && (
        <NegotiationScript
          script={careerPlan.scriptNegociation}
          isOpen={showNegotiationScript}
          onClose={() => setShowNegotiationScript(false)}
          onSave={handleSaveNegotiationScript}
        />
      )}
    </div>
  );
};

export default SupabaseCareerCoaching;
