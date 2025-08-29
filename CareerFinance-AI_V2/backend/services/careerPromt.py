

from services.gemini import call_gemini_api
from services.career_parser import parse_gemini_response
def generate_career_plan(goal, skills, sector):
   prompt = f"""
Je suis un utilisateur avec l'objectif de carrière suivant : "{goal}".
Voici mes compétences actuelles : {', '.join(skills)}.
Le secteur que je vise est : {sector}.

Génère-moi une réponse JSON bien structurée avec les sections suivantes :

1. "planCarriere": {{
   "etapes": [
     {{
       "titre": "Nom du poste ou rôle (ex: Senior Developer)",
       "duree": "Durée estimée pour atteindre ce poste (ex: 6-12 mois)",
       "description": "Description de l'étape et des responsabilités",
       "competencesRequises": ["Compétence A", "Compétence B", "Compétence C"],
       "salaireEstime": Estimation du salaire en MAD (ex: 28000)
     }},
     ...
   ]
}}

2. "scriptNegociation": {{
   "points": [
     "Phrase clé à utiliser dans la négociation (ex: Mes réalisations et contributions à l'équipe)",
     ...
   ],
   "arguments": [
     "Argument fort (ex: J’ai mené avec succès 3 projets majeurs cette année)",
     ...
   ]
   "conseils": [
    "Préparez des exemples concrets de vos réalisations",
    "Choisissez le bon moment pour la discussion",
    "Restez professionnel et positif",
    "Soyez ouvert aux alternatives (formation, responsabilités, etc.)"
  ]
}}

3. "formationsRecommandees": [
  {{
    "titre": "Nom de la formation (ex: Certification Project Management)",
    "duree": "Durée estimée (ex: 3 mois)",
    "priorite": "high | medium | low",
    "description": "Ce que la formation apporte concrètement"
  }},
  ...
]

4. "planningFormations": [
  {{
    "mois": "Mois 1-3",
    "formation": "Nom de la formation"
  }},
  ...
]

5. "objectifsSMART": [
  {{
    "horizon": "6 mois | 1 an | 3 ans",
    "objectif": "Ex: Obtenir une certification en gestion de projet",
    "smart_tags": ["Spécifique", "Mesurable", "Temporel"]  // tags cochés
  }},
  ...
]

6. "suiviProgres": [
  {{
    "titre": "Nom du domaine (ex: Certification en cours)",
    "progression": "Pourcentage (ex: 25%)"
  }},
  ...
]

❗ Important :
- Respecte **scrupuleusement** la structure JSON ci-dessus.
- Les champs doivent être **cohérents, utiles et adaptés** à mon objectif.
- La réponse ne doit contenir **aucun texte explicatif en dehors du JSON**.
"""
    # Appel à Gemini
    #
  


   return call_gemini_api(prompt)
