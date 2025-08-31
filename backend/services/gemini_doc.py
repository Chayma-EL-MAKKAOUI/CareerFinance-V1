# services/gemini_doc.py
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Charger .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY non trouvé dans le fichier .env")

# Configurer Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-exp")


def analyze_with_gemini_with_context(user_text: str, contexts: list) -> dict:
    """
    Retourne un dict normalisé (resume, details, anomalies, recommandations, meta.summary optionnel)
    en utilisant le contexte RAG + le texte OCR.
    """
    ctx_joined = "\n\n--- CONTEXTE ---\n\n".join(contexts[:6])

    prompt = f"""
Tu es un assistant d'analyse de documents de paie et contrats pour le Maroc.
Tu t'appuies d'abord sur le CONTEXTE (règles CNSS, IR, SMIG, congés, heures supp…) et ensuite sur le TEXTE UTILISATEUR.

=== CONTEXTE RÉFÉRENCE (extraits fiables) ===
{ctx_joined}

=== TEXTE UTILISATEUR (OCR) ===
{user_text}

Analyse et retourne un JSON strictement valide:
{{
  "resume": {{
    "salaireBrut": 0,
    "salaireNet": 0,
    "cotisations": 0,
    "impots": 0
  }},
  "details": {{
    "salaireBase": 0,
    "primes": [{{"libelle":"...", "montant": 0}}],
    "heuresSupp": [{{"libelle":"...", "montant": 0}}],
    "cotisations": [{{"libelle":"...", "montant": 0, "type": "patronale|salariale"}}],
    "impots": [{{"libelle":"IR", "montant": 0}}],
    "netAPayer": 0
  }},
  "anomalies": [
    {{"titre":"...", "description":"...", "impact":"Faible|Moyen|Élevé|Positif"}}
  ],
  "recommandations": ["...","..."],
  "meta": {{
    "summary": "2 à 3 phrases de synthèse en français"
  }}
}}
Règles:
- Valeurs numériques en MAD (nombres, pas de chaînes).
- Aucune balise Markdown.
- Le JSON doit être parsable avec json.loads.
- Si une valeur n'est pas trouvable, mets 0 ou [] selon le cas.

Retourne uniquement l'objet JSON.
"""
    try:
        response = model.generate_content(prompt)
        cleaned = response.text.strip()

        # Nettoyage basique des blocs markdown éventuels
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        # Retirer retours ligne/contrôles (sans casser les espaces)
        cleaned = cleaned.replace("\r", "").replace("\n", "")

        # Extraire objet JSON
        start_idx = cleaned.find("{")
        end_idx = cleaned.rfind("}")

        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = cleaned[start_idx:end_idx + 1]
            # Debug volontaire (à commenter si besoin)
            print(f"🔍 JSON extrait (début): {json_str[:200]}...")
            return json.loads(json_str)
        else:
            print(f"❌ Pas de JSON valide trouvé (début): {cleaned[:200]}...")
            return _fallback_response()

    except json.JSONDecodeError as e:
        print(f"❌ Erreur JSON parsing: {e}")
        return _fallback_response()
    except Exception as e:
        print("❌ Erreur Gemini (context):", e)
        return _fallback_response()


def _fallback_response() -> dict:
    """Réponse de secours en cas d'échec du LLM."""
    return {
        "resume": {
            "salaireBrut": 0,
            "salaireNet": 0,
            "cotisations": 0,
            "impots": 0
        },
        "details": {
            "salaireBase": 0,
            "primes": [],
            "heuresSupp": [],
            "cotisations": [],
            "impots": [],
            "netAPayer": 0
        },
        "anomalies": [
            {"titre": "Erreur d'analyse", "description": "Impossible d'analyser le document", "impact": "Moyen"}
        ],
        "recommandations": ["Vérifiez la qualité du document uploadé"],
        "meta": {"summary": "Analyse indisponible pour ce document."}
    }
