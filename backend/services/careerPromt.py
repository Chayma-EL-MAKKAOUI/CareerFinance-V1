# services/careerPromt.py
import google.generativeai as genai
import os
from typing import List

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_career_plan(goal: str, skills: List[str], sector: str) -> str:
    prompt = f"""
    En tant qu'expert en coaching de carrière, créez un plan personnalisé en JSON pour:
    Objectif: {goal}
    Compétences actuelles: {', '.join(skills)}
    Secteur: {sector}

    Répondez UNIQUEMENT en JSON avec cette structure:
    {{
        "plan_carriere": {{
            "titre": "...",
            "description": "...",
            "etapes": [
                {{"titre": "...", "description": "...", "duree": "...", "competences": []}}
            ]
        }},
        "formations": [
            {{"titre": "...", "description": "...", "duree": "...", "priorite": "..."}}
        ],
        "negociation": {{
            "points_cles": ["..."],
            "arguments": ["..."],
            "conseils": ["..."]
        }}
    }}
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise Exception(f"Erreur Gemini: {str(e)}")

def generate_career_plan_with_rag(goal: str, skills: List[str], sector: str, rag_context: str) -> str:
    prompt = f"""
    En tant qu'expert en coaching de carrière, utilisez les données LinkedIn suivantes pour créer un plan personnalisé et réaliste.

    PROFILS LINKEDIN PERTINENTS:
    {rag_context}

    DEMANDE DE L'UTILISATEUR:
    Objectif: {goal}
    Compétences actuelles: {', '.join(skills)}
    Secteur: {sector}

    INSTRUCTIONS:
    - Analysez les profils LinkedIn fournis pour identifier des parcours réalistes
    - Basez vos recommandations sur les expériences réelles de ces professionnels
    - Proposez des étapes concrètes inspirées des trajectoires observées
    - Suggérez des formations que ces professionnels ont suivies
    - Donnez des conseils de négociation basés sur leur secteur d'activité

    Répondez UNIQUEMENT en JSON avec cette structure:
    {{
        "plan_carriere": {{
            "titre": "Plan basé sur les profils LinkedIn du secteur {sector}",
            "description": "Description du parcours recommandé",
            "etapes": [
                {{
                    "titre": "Titre de l'étape",
                    "description": "Description détaillée basée sur les profils analysés",
                    "duree": "6-12 mois",
                    "competences": ["compétence1", "compétence2"],
                    "salaire": 50000
                }}
            ]
        }},
        "formations": [
            {{
                "titre": "Formation recommandée",
                "description": "Description basée sur les profils LinkedIn",
                "duree": "2-3 mois",
                "priorite": "élevée"
            }}
        ],
        "negociation": {{
            "points_cles": [
                "Point de négociation basé sur le marché du secteur",
                "Argument tiré des profils LinkedIn analysés"
            ],
            "arguments": [
                "Argument concret basé sur les données LinkedIn",
                "Référence aux standards du secteur"
            ],
            "conseils": [
                "Conseil pratique pour le secteur {sector}",
                "Stratégie observée chez les professionnels similaires"
            ]
        }}
    }}
    """
    try:
        # modèle à latence faible, OK pour RAG
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise Exception(f"Erreur Gemini avec RAG: {str(e)}")
