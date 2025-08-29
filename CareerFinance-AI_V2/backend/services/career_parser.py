import json
from fastapi import HTTPException

def parse_gemini_response(response_text: str):
    """
    Cette fonction tente de parser la réponse de Gemini (string) en JSON.
    Elle vérifie que la structure est valide.
    """
    try:
        # Essaye de parser la réponse en JSON
        parsed = json.loads(response_text)

        # Vérifie que les sections essentielles sont présentes
        if not all(k in parsed for k in ["planCarriere", "scriptNegociation", "formationsRecommandees", "objectifsSMART", "suiviProgres"]):
            raise ValueError("La réponse ne contient pas toutes les sections attendues")

        return parsed

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Réponse de Gemini invalide : JSON non valide")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur dans le parsing Gemini: {str(e)}")
