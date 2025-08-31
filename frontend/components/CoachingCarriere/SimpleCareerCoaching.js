'use client';
import React, { useState } from 'react';

const SimpleCareerCoaching = () => {
  const [formData, setFormData] = useState({
    goal: '',
    skills: '',
    sector: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

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
    setResult(null);

    try {
      // Simulation d'une réponse
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setResult({
        message: "Plan de carrière généré avec succès !",
        plan: `Basé sur votre objectif "${formData.goal}" et vos compétences "${formData.skills}", voici votre plan de carrière personnalisé...`,
        recommendations: [
          "Développez vos compétences en leadership",
          "Obtenez des certifications dans votre domaine",
          "Construisez votre réseau professionnel",
          "Identifiez les opportunités de promotion"
        ]
      });
    } catch (error) {
      setResult({
        error: "Erreur lors de la génération du plan"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 p-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🎯 Coaching Carrière
        </h1>
        <p className="text-gray-600">
          Générez votre plan de carrière personnalisé
        </p>
      </div>

      {/* Formulaire */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">Vos informations</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
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
          
          <button 
            type="submit" 
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Génération en cours...' : 'Générer mon plan de carrière'}
          </button>
        </form>
      </div>

      {/* Résultat */}
      {result && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Votre plan de carrière</h2>
          
          {result.error ? (
            <div className="text-red-600 bg-red-50 p-4 rounded-md">
              {result.error}
            </div>
          ) : (
            <div className="space-y-4">
              <div className="text-green-600 bg-green-50 p-4 rounded-md">
                {result.message}
              </div>
              
              <div>
                <h3 className="font-medium mb-2">Plan personnalisé :</h3>
                <div className="bg-gray-50 p-4 rounded-md">
                  {result.plan}
                </div>
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
          )}
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
            </ul>
          </div>
          <div>
            <h4 className="font-medium mb-2">🚀 Avantages</h4>
            <ul className="space-y-1 text-gray-600">
              <li>• Analyse personnalisée</li>
              <li>• Recommandations concrètes</li>
              <li>• Suivi de progression</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimpleCareerCoaching;
