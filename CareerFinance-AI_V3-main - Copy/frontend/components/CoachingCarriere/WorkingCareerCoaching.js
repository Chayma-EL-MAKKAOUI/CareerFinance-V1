'use client';
import React, { useState } from 'react';
import CareerPlan from './CareerPlan';
import NegotiationScript from './NegotiationScript';

const WorkingCareerCoaching = () => {
  const [formData, setFormData] = useState({
    goal: '',
    skills: '',
    sector: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [showCareerPlan, setShowCareerPlan] = useState(false);
  const [showNegotiationScript, setShowNegotiationScript] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const generateCareerPlan = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setError(null);

    try {
      // Simulation d'une réponse
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setResult({
        message: "Plan de carrière généré avec succès !",
        plan: `Basé sur votre objectif "${formData.goal}" et vos compétences "${formData.skills}", voici votre plan de carrière personnalisé :

**Phase 1 (0-6 mois) :**
• Développez vos compétences en leadership et gestion de projet
• Obtenez des certifications pertinentes dans votre domaine
• Construisez votre réseau professionnel

**Phase 2 (6-12 mois) :**
• Identifiez les opportunités de promotion internes
• Participez à des projets transversaux
• Développez votre visibilité dans l'entreprise

**Phase 3 (12-24 mois) :**
• Postulez à des postes de chef de projet
• Négociez votre promotion avec des arguments solides
• Continuez à développer vos compétences techniques et managériales`,
        recommendations: [
          "Développez vos compétences en leadership",
          "Obtenez des certifications dans votre domaine",
          "Construisez votre réseau professionnel",
          "Identifiez les opportunités de promotion",
          "Participez à des projets transversaux",
          "Développez votre visibilité dans l'entreprise"
        ]
      });
    } catch (error) {
      setError("Erreur lors de la génération du plan");
    } finally {
      setLoading(false);
    }
  };

  const generateNegotiationScript = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setError(null);

    try {
      // Simulation d'une réponse
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      setResult({
        message: "Script de négociation généré avec succès !",
        script: `Voici votre script de négociation personnalisé basé sur votre objectif "${formData.goal}" :

**Ouverture :**
"Bonjour [Nom du manager], j'aimerais discuter de mon évolution professionnelle au sein de l'entreprise."

**Argumentation :**
"Au cours des derniers mois, j'ai développé mes compétences en ${formData.skills} et j'ai contribué à plusieurs projets importants. Je pense être prêt à prendre plus de responsabilités."

**Objectif :**
"Mon objectif est de devenir ${formData.goal} dans les prochains mois. Quelles sont les étapes pour y parvenir ?"

**Questions à poser :**
• Quels sont les critères pour ce poste ?
• Y a-t-il des formations ou certifications recommandées ?
• Quand pourrions-nous revoir cette discussion ?

**Conclusion :**
"Je suis motivé et prêt à m'investir pour atteindre cet objectif. Pouvez-vous me donner votre retour sur ce plan ?"`,
        recommendations: [
          "Préparez des exemples concrets de vos réalisations",
          "Anticipez les objections et préparez vos réponses",
          "Soyez confiant mais humble",
          "Écoutez activement les retours",
          "Proposez un plan d'action concret",
          "Fixez des échéances pour le suivi"
        ]
      });
    } catch (error) {
      setError("Erreur lors de la génération du script");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveCareerPlan = (updatedPlan) => {
    setResult(prev => ({
      ...prev,
      plan: updatedPlan
    }));
  };

  const handleSaveNegotiationScript = (updatedScript) => {
    setResult(prev => ({
      ...prev,
      script: updatedScript
    }));
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 p-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🎯 Coaching Carrière
        </h1>
        <p className="text-gray-600">
          Générez votre plan de carrière personnalisé et vos scripts de négociation
        </p>
      </div>

      {/* Formulaire */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">Vos informations</h2>
        <form className="space-y-4">
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
              placeholder="Ex: Devenir chef de projet"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Compétences clés actuelles (séparées par des virgules)
            </label>
            <input 
              type="text" 
              name="skills"
              value={formData.skills}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Ex: Python, React, Gestion de projet"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Secteur d'activité
            </label>
            <select
              name="sector"
              value={formData.sector}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Sélectionnez un secteur</option>
              <option value="Technologie">Technologie</option>
              <option value="Finance">Finance</option>
              <option value="Santé">Santé</option>
              <option value="Éducation">Éducation</option>
              <option value="Commerce">Commerce</option>
              <option value="Industrie">Industrie</option>
              <option value="Autre">Autre</option>
            </select>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button 
              type="button"
              onClick={generateCareerPlan}
              disabled={loading || !formData.goal}
              className="w-full bg-gradient-to-r from-blue-600 to-green-600 text-white py-2 px-4 rounded-md hover:from-blue-700 hover:to-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Génération...' : 'Générer mon plan de carrière'}
            </button>
            <button 
              type="button"
              onClick={generateNegotiationScript}
              disabled={loading || !formData.goal}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-2 px-4 rounded-md hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Génération...' : 'Script de négociation'}
            </button>
          </div>
        </form>
      </div>

      {/* Affichage des erreurs */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="text-red-700">
            <strong>Erreur :</strong> {error}
          </div>
        </div>
      )}

      {/* Résultat */}
      {result && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Votre résultat</h2>
          
          <div className="space-y-4">
            <div className="text-green-600 bg-green-50 p-4 rounded-md">
              {result.message}
            </div>
            
            {/* Boutons d'ouverture des fenêtres */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {result.plan && (
                <button
                  onClick={() => setShowCareerPlan(true)}
                  className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 transition-colors"
                >
                  📋 Voir le plan de carrière
                </button>
              )}
              
              {result.script && (
                <button
                  onClick={() => setShowNegotiationScript(true)}
                  className="w-full bg-purple-600 text-white py-3 px-4 rounded-md hover:bg-purple-700 transition-colors"
                >
                  💬 Voir le script de négociation
                </button>
              )}
            </div>
            
            <div>
              <h3 className="font-medium mb-2">Recommandations :</h3>
              <ul className="list-disc list-inside space-y-1">
                {result.recommendations.map((rec, index) => (
                  <li key={index} className="text-gray-700">{rec}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Informations supplémentaires */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-3">💡 À propos du coaching carrière</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <h4 className="font-medium mb-2">🎯 Objectifs</h4>
            <ul className="space-y-1 text-gray-600">
              <li>• Définir un plan de carrière clair</li>
              <li>• Identifier les compétences à développer</li>
              <li>• Trouver des opportunités de progression</li>
              <li>• Préparer ses négociations</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium mb-2">🚀 Avantages</h4>
            <ul className="space-y-1 text-gray-600">
              <li>• Analyse personnalisée</li>
              <li>• Recommandations concrètes</li>
              <li>• Scripts de négociation</li>
              <li>• Suivi de progression</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Fenêtres modales */}
      {result?.plan && (
        <CareerPlan
          plan={result.plan}
          isOpen={showCareerPlan}
          onClose={() => setShowCareerPlan(false)}
          onSave={handleSaveCareerPlan}
        />
      )}

      {result?.script && (
        <NegotiationScript
          script={result.script}
          isOpen={showNegotiationScript}
          onClose={() => setShowNegotiationScript(false)}
          onSave={handleSaveNegotiationScript}
        />
      )}
    </div>
  );
};

export default WorkingCareerCoaching;
