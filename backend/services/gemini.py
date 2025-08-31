# gemini.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Charger les variables d’environnement
load_dotenv()

# Configurer la clé API Gemini (à mettre dans ton .env)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise Exception("❌ GEMINI_API_KEY is not set in the environment.")

# Initialiser le modèle Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-exp")

# Fonction utilitaire principale
def call_gemini_api(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise Exception(f"Erreur lors de l'appel à Gemini : {str(e)}")
