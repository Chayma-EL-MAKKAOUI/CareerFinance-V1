from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
from services.gemini import call_gemini_api
from services.enhanced_salary_service import enhanced_salary_service
from services.rag_service import linkedin_rag

router = APIRouter()


class Recommendation(BaseModel):
    title: str
    description: str
    priority: str  # 'high', 'medium', 'low'

class Trend(BaseModel):
    title: str
    detail: str

class Step(BaseModel):
    numero: int
    contenu: str

# 📥 Schéma de la requête
class SalaryRequest(BaseModel):
    jobTitle: str
    location: str
    experienceYears: int
    currentSalary: int
    useLinkedInData: Optional[bool] = True  # Par défaut, utiliser les données LinkedIn

# 📤 Schéma de la réponse (facultatif mais bon pour clarté)
class SalaryResponse(BaseModel):
    moyenne: int
    ecart: int
    ecart_pourcent: float
    minimum: int
    maximum: int
    percentile: int
    recommandations: List[Recommendation]
    tendances: List[Trend]
    salaireActuel: int
    jobTitle: str
    location: str
    experienceYears: int
    etapes: List[Step]
    linkedinInsights: Optional[dict] = None
    dataQuality: Optional[dict] = None

@router.post("/analyze", response_model=SalaryResponse)
async def analyze_salary(data: SalaryRequest):
    # 🧠 Prompt à envoyer à Gemini
    prompt = f"""
Tu es un expert RH. Voici les infos d’un salarié :
- Poste : {data.jobTitle}
- Localisation : {data.location}
- Expérience : {data.experienceYears} ans
- Salaire actuel : {data.currentSalary} MAD

Fais une analyse salariale et réponds en JSON avec cette structure :

{{
  "moyenne": 9000,
  "ecart": -2000,
  "ecart_pourcent": -22.2,
  "minimum": 7500,
  "maximum": 12000,
  "percentile": 25,
  "recommandations": [
    {{
      "title": "Négociation salariale",
      "description": "Préparez un dossier de négociation basé sur vos performances et l'analyse du marché",
      "priority": "high"
    }}
  ],
  "tendances": [
    {{
      "title": "Demande du marché",
      "detail": "Forte demande pour les profils Data Security, ce qui pousse les salaires à la hausse."
    }}
  ]
   "etapes": [
    {{
      "numero": 1,
      "contenu": "Préparez votre dossier de négociation avec ces données"
    }},
    {{
      "numero": 2,
      "contenu": "Planifiez un entretien avec votre manager"
    }},
    {{
      "numero": 3,
      "contenu": "Explorez les opportunités du marché"
    }}
  ]
}}

IMPORTANT: N'inclus PAS le champ "salaireActuel" dans ta réponse JSON, il sera ajouté automatiquement.

Réponds uniquement avec un JSON valide sans aucune phrase ni explication autour. Ne mets rien d'autre que le JSON.
"""

    # Appel à Gemini
    try:
        gemini_output = call_gemini_api(prompt)
        print("🧪 Réponse Gemini brute :", gemini_output)

     # Supprime les éventuels ```json et ``` qui encadrent la réponse
        cleaned_output = gemini_output.strip().removeprefix("```json").removesuffix("```").strip()

        response_json = json.loads(cleaned_output)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur analyse Gemini: {str(e)}")

    return {
    **response_json,
    "salaireActuel": data.currentSalary,
    "jobTitle": data.jobTitle,
    "location": data.location,
    "experienceYears": data.experienceYears
}

