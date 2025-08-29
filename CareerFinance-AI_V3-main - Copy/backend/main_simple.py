# backend/main_simple.py
from __future__ import annotations

import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

# ── Logging ──────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("careerfinance")

# ── Config ───────────────────────────────────────────────────────────────
class Settings(BaseSettings):
    APP_NAME: str = "CareerFinance AI"
    APP_VERSION: str = "v2"
    ENV: str = "dev"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "*"]
    CORS_CREDENTIALS: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

# ── Models ───────────────────────────────────────────────────────────────
# Modèles simplifiés pour éviter les problèmes de parsing
# class CareerCoachingRequest(BaseModel):
#     goal: str = "Évoluer vers un poste de management"
#     skills: list[str] = ["JavaScript", "React", "Node.js"]
#     sector: str = "Technologie"
#     useLinkedInData: bool = False

# class CareerCoachingResponse(BaseModel):
#     plan: dict
#     insights: list[str]
#     recommendations: list[str]
#     next_steps: list[str]

# ── Lifespan ─────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    log.info("🚀 Démarrage CareerFinance AI (version simplifiée)...")
    log.info("✅ Application démarrée")
    yield
    log.info("🛑 Arrêt de l'application...")

# ── App ──────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health/version
@app.get("/api/health")
async def health():
    return {"ok": True, "message": "CareerFinance AI Backend is running"}

@app.get("/api/version")
async def version():
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION, "env": settings.ENV}

# ── Routes de base ───────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "message": "CareerFinance AI Backend",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/coaching-carriere")
async def coaching_carriere_info():
    return {
        "message": "API Coaching Carrière",
        "status": "ready",
        "features": [
            "Génération de plans de carrière",
            "Analyse des compétences",
            "Recherche de profils LinkedIn",
            "Insights sectoriels"
        ],
        "note": "Cette version simplifiée est prête pour l'intégration Supabase"
    }

# ── Routes RAG (simulées) ───────────────────────────────────────────────
@app.get("/api/rag/status")
async def rag_status():
    """Statut du système RAG LinkedIn"""
    return {
        "isInitialized": False,
        "profilesCount": 0,
        "status": "not_available",
        "message": "Système RAG LinkedIn non initialisé dans cette version simplifiée"
    }

# ── Routes Documents (simulées) ──────────────────────────────────────────
@app.post("/api/documents/upload")
async def upload_documents(request: Request):
    """API d'upload de documents (simulée)"""
    try:
        # Simulation d'un upload réussi
        return {
            "success": True,
            "message": "Document uploadé avec succès",
            "filename": "document.pdf",
            "size": "1.2 MB"
        }
    except Exception as e:
        log.error(f"Erreur dans l'upload de documents: {e}")
        return {
            "success": False,
            "message": "Erreur lors de l'upload",
            "error": str(e)
        }

# ── Routes Coaching (simulées) ──────────────────────────────────────────
@app.post("/api/coaching/coaching")
async def coaching_carriere(request: Request):
    """API de coaching carrière simplifiée"""
    try:
        body = await request.json()
        goal = body.get('goal', "Évoluer vers un poste de management")
        skills = body.get('skills', ["JavaScript", "React", "Node.js"])
        sector = body.get('sector', "Technologie")

        # Structure attendue par le frontend (CareerCoachingResult)
        response_payload = {
            "objectif": goal,
            "competences": skills,
            "secteur": sector,
            "planCarriere": {
                "etapes": [
                    {
                        "titre": "Bilan des compétences",
                        "duree": "2 semaines",
                        "description": "Cartographier vos compétences actuelles et celles à développer en priorité.",
                        "competencesRequises": skills[:2] + ["Communication"],
                        "salaireEstime": 0,
                    },
                    {
                        "titre": "Formation ciblée",
                        "duree": "1-2 mois",
                        "description": "Suivre 2 formations certifiantes alignées avec l'objectif.",
                        "competencesRequises": skills + ["Gestion de projet"],
                        "salaireEstime": 0,
                    },
                    {
                        "titre": "Projet portfolio",
                        "duree": "1 mois",
                        "description": "Réaliser un projet concret démontrant l'objectif: %s." % goal,
                        "competencesRequises": skills,
                        "salaireEstime": 0,
                    },
                    {
                        "titre": "Networking & candidatures",
                        "duree": "3-4 semaines",
                        "description": "Optimiser CV/LinkedIn, activer le réseau et postuler.",
                        "competencesRequises": ["Personal Branding", "Networking"],
                        "salaireEstime": 0,
                    },
                ]
            },
            "scriptNegociation": {
                "points": [
                    "Mise en avant de l'impact mesurable des projets",
                    "Alignement des compétences avec les besoins du poste",
                    "Mobilité et progression"
                ],
                "arguments": [
                    "Expérience sur %s" % (", ".join(skills[:2]) or "les technologies clés"),
                    "Résultats tangibles obtenus",
                    "Veille continue et certifications"
                ],
                "conseils": [
                    "Préparer 3 exemples STAR",
                    "Ancrer une fourchette salariale réaliste",
                    "Proposer un plan d'onboarding de 30 jours"
                ]
            },
            "formationsRecommandees": [
                {"titre": "Certification %s" % (skills[0] if skills else "Core"), "duree": "2-4 semaines", "priorite": "high", "description": "Certification reconnue pour renforcer la crédibilité."},
                {"titre": "Soft skills leadership", "duree": "2 semaines", "priorite": "medium", "description": "Communication, influence, feedback."}
            ],
            "planningFormations": [
                {"mois": "Mois 1", "formation": "Certification technique"},
                {"mois": "Mois 2", "formation": "Projet portfolio"},
                {"mois": "Mois 3", "formation": "Préparation entretiens"}
            ],
            "objectifsSMART": [
                {"horizon": "30 jours", "objectif": "Finaliser 1 certification", "smart_tags": ["Spécifique", "Mesurable", "Temporel"]},
                {"horizon": "60 jours", "objectif": "Livrer un projet portfolio", "smart_tags": ["Spécifique", "Atteignable", "Réaliste"]},
            ],
            "suiviProgres": [
                {"titre": "Certification en cours", "progression": 40},
                {"titre": "Développement leadership", "progression": 20},
                {"titre": "Réseau professionnel", "progression": 10},
            ],
        }

        return response_payload

    except Exception as e:
        log.error(f"Erreur dans le coaching carrière: {e}")
        return {
            "error": "Erreur interne du serveur",
            "message": str(e),
        }

@app.post("/api/rag/enhanced-coaching")
async def enhanced_coaching(request: Request):
    """API de coaching enrichi avec RAG (simulée)"""
    try:
        body = await request.json()
        goal = body.get('goal', "Évoluer vers un poste de management")
        skills = body.get('skills', ["JavaScript", "React", "Node.js"])
        sector = body.get('sector', "Technologie")

        payload = await coaching_carriere(request)  # base structure
        # Ajouter des drapeaux/insights LinkedIn simulés
        if isinstance(payload, dict):
            payload.update({
                "linkedInDataUsed": True,
                "linkedinInsights": {
                    "profilesAnalyzed": 128,
                    "topSkills": skills[:3],
                    "targetCompanies": ["Company A", "Company B"],
                    "commonTitles": [goal, "Senior " + goal if isinstance(goal, str) else "Senior"],
                    "locations": ["Casablanca", "Rabat"],
                },
                "secteur": sector,
            })
        return payload

    except Exception as e:
        log.error(f"Erreur dans le coaching enrichi: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

# (optionnel) exécution directe: uvicorn backend.main_simple:app --reload
if __name__ == "__main__": # pragma: no cover
    import uvicorn
    uvicorn.run("main_simple:app", host="0.0.0.0", port=8000, reload=True)
