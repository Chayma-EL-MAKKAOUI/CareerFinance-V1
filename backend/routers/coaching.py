<<<<<<< HEAD
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from services.careerPromt import generate_career_plan
=======
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from services.careerPromt import generate_career_plan
from dependencies.auth_dependencies import get_current_user
>>>>>>> 5e0de77 (Auth commit)

router = APIRouter()

class CoachingRequest(BaseModel):
    goal: str
    skills: List[str]
    sector: str

@router.post("/coaching")
<<<<<<< HEAD
async def generate_plan(data: CoachingRequest):
=======
async def generate_plan(
    data: CoachingRequest,
    current_user: dict = Depends(get_current_user)
):
>>>>>>> 5e0de77 (Auth commit)
    try:
        response = generate_career_plan(data.goal, data.skills, data.sector)
        print("💬 Réponse Gemini brute :\n", response)
        
        cleaned_output = response.strip().removeprefix("```json").removesuffix("```").strip()
        
        # 🧩 Charger le JSON généré par Gemini
        import json
        plan_data = json.loads(cleaned_output)

        # ✅ Ajouter les champs en haut de l'objet final
        enriched_plan = {
            "objectif": data.goal,
            "competences": data.skills,
            "secteur": data.sector,
            **plan_data  # fusionne avec les autres champs générés : planCarriere, scriptNegociation, etc.
        }

        return enriched_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
