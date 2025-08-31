 #services.enhanced_career_services.py
from typing import List, Dict, Any
from services.gemini import call_gemini_api
from services.rag_service import linkedin_rag
import json

class EnhancedCareerService:
    """Service de coaching de carrière enrichi avec les données LinkedIn RAG"""
    
    def __init__(self):
        self.rag_service = linkedin_rag
    
    def generate_enhanced_career_plan(self, goal: str, skills: List[str], sector: str) -> Dict[str, Any]:
        """Génère un plan de carrière enrichi avec les données LinkedIn"""
        
        # 1. Obtenir les insights LinkedIn via RAG
        linkedin_insights = self.rag_service.get_career_insights(goal, skills, sector)
        
        # 2. Construire un prompt enrichi pour Gemini
        enhanced_prompt = self._build_enhanced_prompt(goal, skills, sector, linkedin_insights)
        
        # 3. Appeler Gemini avec le prompt enrichi
        try:
            gemini_response = call_gemini_api(enhanced_prompt)
            cleaned_response = gemini_response.strip().removeprefix("```json").removesuffix("```").strip()
            career_plan = json.loads(cleaned_response)
            
            # 4. Enrichir la réponse avec les données LinkedIn
            enhanced_plan = self._enrich_career_plan(career_plan, linkedin_insights)
            
            return enhanced_plan
            
        except Exception as e:
            raise Exception(f"Erreur lors de la génération du plan de carrière enrichi: {str(e)}")
    
    def _build_enhanced_prompt(self, goal: str, skills: List[str], sector: str, insights: Dict[str, Any]) -> str:
        """Construit un prompt enrichi avec les données LinkedIn"""
        
        # Extraire les informations clés des insights
        similar_profiles = insights.get('profiles_similaires', [])
        popular_skills = insights.get('competences_populaires', [])
        target_companies = insights.get('entreprises_cibles', [])
        career_paths = insights.get('parcours_types', [])
        
        # Construire les sections d'information LinkedIn
        profiles_info = ""
        if similar_profiles:
            profiles_info = "Profils LinkedIn similaires trouvés:\n"
            for i, profile_data in enumerate(similar_profiles[:3], 1):
                profile = profile_data['profile']
                profiles_info += f"{i}. {profile['name']} - {profile['title']} chez {profile['company']}\n"
                profiles_info += f"   Compétences: {', '.join(profile['skills'][:5])}\n"
        
        skills_info = ""
        if popular_skills:
            skills_info = "Compétences les plus demandées dans ce domaine:\n"
            for skill_data in popular_skills[:5]:
                skills_info += f"- {skill_data['skill']} (mentionnée {skill_data['count']} fois)\n"
        
        companies_info = ""
        if target_companies:
            companies_info = "Entreprises populaires dans ce secteur:\n"
            for company_data in target_companies[:5]:
                companies_info += f"- {company_data['company']} ({company_data['count']} profils)\n"
        
        paths_info = ""
        if career_paths:
            paths_info = "Postes typiques dans ce domaine:\n"
            for path in career_paths[:5]:
                paths_info += f"- {path}\n"
        
        prompt = f"""
Tu es un expert en coaching de carrière avec accès à des données LinkedIn réelles. 

INFORMATIONS UTILISATEUR:
- Objectif de carrière: "{goal}"
- Compétences actuelles: {', '.join(skills)}
- Secteur visé: {sector}

DONNÉES LINKEDIN ANALYSÉES:
{profiles_info}

{skills_info}

{companies_info}

{paths_info}

En te basant sur ces données LinkedIn réelles et l'objectif de l'utilisateur, génère un plan de carrière personnalisé et réaliste.

Réponds en JSON avec cette structure exacte:

{{
  "planCarriere": {{
    "etapes": [
      {{
        "titre": "Nom du poste (basé sur les données LinkedIn)",
        "duree": "Durée estimée",
        "description": "Description détaillée avec références aux profils LinkedIn",
        "competencesRequises": ["Compétence basée sur l'analyse LinkedIn", "..."],
        "salaireEstime": 35000,
        "entreprisesCibles": ["Entreprise trouvée sur LinkedIn", "..."],
        "justification": "Pourquoi cette étape, basée sur les profils analysés"
      }}
    ]
  }},
  "scriptNegociation": {{
    "points": ["Point de négociation basé sur les données du marché", "..."],
    "arguments": ["Argument avec référence aux profils LinkedIn", "..."],
    "conseils": ["Conseil pratique basé sur l'analyse", "..."]
  }},
  "formationsRecommandees": [
    {{
      "titre": "Formation identifiée via l'analyse LinkedIn",
      "duree": "Durée",
      "priorite": "high",
      "description": "Pourquoi cette formation, basée sur les compétences populaires",
      "competencesCibles": ["Compétence populaire sur LinkedIn", "..."]
    }}
  ],
  "planningFormations": [
    {{
      "mois": "Janvier 2025",
      "formation": "Formation prioritaire identifiée"
    }}
  ],
  "objectifsSMART": [
    {{
      "horizon": "3 mois",
      "objectif": "Objectif basé sur l'analyse des profils similaires",
      "smart_tags": ["Spécifique", "Mesurable", "Atteignable", "Réaliste", "Temporel"]
    }}
  ],
  "suiviProgres": [
    {{
      "titre": "Indicateur de progression",
      "progression": "Comment mesurer le progrès"
    }}
  ],
  "insightsLinkedIn": {{
    "profilsAnalyses": {len(similar_profiles)},
    "competencesPopulaires": ["{popular_skills[0]['skill'] if popular_skills else 'N/A'}"],
    "entreprisesCibles": ["{target_companies[0]['company'] if target_companies else 'N/A'}"],
    "recommandationsPersonnalisees": [
      "Recommandation basée sur l'analyse des profils similaires",
      "Conseil pour se démarquer dans ce secteur"
    ]
  }}
}}

IMPORTANT:
- Base tes recommandations sur les données LinkedIn fournies
- Utilise les compétences populaires identifiées
- Référence les entreprises trouvées dans l'analyse
- Justifie chaque recommandation avec les insights LinkedIn
- Sois réaliste et précis dans les estimations salariales
- Ne mets aucune balise Markdown, juste le JSON valide
"""
        
        return prompt
    
    def _enrich_career_plan(self, career_plan: Dict[str, Any], insights: Dict[str, Any]) -> Dict[str, Any]:
        """Enrichit le plan de carrière avec des métadonnées LinkedIn"""
        
        # Ajouter les insights LinkedIn au plan
        career_plan['linkedinInsights'] = {
            'profilesAnalyzed': len(insights.get('profiles_similaires', [])),
            'topSkills': [skill['skill'] for skill in insights.get('competences_populaires', [])[:5]],
            'targetCompanies': [company['company'] for company in insights.get('entreprises_cibles', [])[:5]],
            'commonTitles': insights.get('parcours_types', [])[:5],
            'locations': [loc['location'] for loc in insights.get('localisations', [])[:3]]
        }
        
        # Ajouter des recommandations basées sur les profils similaires
        if insights.get('profiles_similaires'):
            career_plan['recommendationsBasedOnProfiles'] = []
            for profile_data in insights['profiles_similaires'][:3]:
                profile = profile_data['profile']
                career_plan['recommendationsBasedOnProfiles'].append({
                    'profileReference': f"{profile['title']} chez {profile['company']}",
                    'recommendation': f"Considérez développer les compétences: {', '.join(profile['skills'][:3])}",
                    'similarity': round(profile_data['score'], 2)
                })
        
        return career_plan
    
    def search_similar_professionals(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Recherche des professionnels similaires"""
        return self.rag_service.search_profiles(query, top_k)
    
    def get_skill_analysis(self, skills: List[str], sector: str) -> Dict[str, Any]:
        """Analyse les compétences par rapport au marché LinkedIn"""
        query = f"{sector} {' '.join(skills)}"
        similar_profiles = self.rag_service.search_profiles(query, top_k=20)
        
        # Analyser les compétences manquantes et populaires
        all_skills = []
        for profile_data in similar_profiles:
            profile = profile_data['profile']
            all_skills.extend(profile.get('skills', []))
        
        # Compter les compétences
        skill_count = {}
        for skill in all_skills:
            skill_count[skill] = skill_count.get(skill, 0) + 1
        
        # Identifier les compétences manquantes
        user_skills_lower = [s.lower() for s in skills]
        missing_skills = []
        for skill, count in skill_count.items():
            if skill.lower() not in user_skills_lower and count >= 3:
                missing_skills.append({'skill': skill, 'frequency': count})
        
        # Trier par fréquence
        missing_skills.sort(key=lambda x: x['frequency'], reverse=True)
        
        return {
            'userSkills': skills,
            'missingSkills': missing_skills[:10],
            'marketDemand': {
                'totalProfilesAnalyzed': len(similar_profiles),
                'averageSkillsPerProfile': len(all_skills) / len(similar_profiles) if similar_profiles else 0
            },
            'recommendations': [
                f"Considérez apprendre {skill['skill']} (trouvé chez {skill['frequency']} professionnels)"
                for skill in missing_skills[:5]
            ]
        }

# Instance globale du service enrichi
enhanced_career_service = EnhancedCareerService()
