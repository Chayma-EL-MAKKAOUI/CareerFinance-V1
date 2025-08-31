#!/usr/bin/env python3
"""
Script de démarrage simple pour tester l'authentification JWT
sans charger les services externes problématiques
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import os

# Configuration simple
app = FastAPI(title="CareerFinance AI - Test Auth", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schéma de sécurité pour le token Bearer
security = HTTPBearer()

# Modèles Pydantic simples
class SalaryRequest(BaseModel):
    jobTitle: str
    location: str
    experienceYears: int
    currentSalary: int

class CoachingRequest(BaseModel):
    goal: str
    skills: list
    sector: str

# Dépendance d'authentification simple
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dépendance simple pour récupérer l'utilisateur actuel"""
    token = credentials.credentials
    
    # En mode test, on simule un utilisateur valide
    # En production, ceci devrait valider le token avec Supabase
    if token and len(token) > 10:  # Token valide simulé
        return {
            "id": 1,
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "role": "user",
            "is_active": True
        }
    else:
        raise HTTPException(status_code=401, detail="Token d'authentification invalide")

# Endpoints publics
@app.get("/api/health")
async def health():
    return {"ok": True, "message": "Serveur en ligne"}

@app.get("/api/version")
async def version():
    return {"name": "CareerFinance AI", "version": "1.0.0", "env": "test"}

# Endpoints protégés
@app.post("/api/salary/analyze")
async def analyze_salary(
    data: SalaryRequest,
    current_user: dict = Depends(get_current_user)
):
    """Endpoint protégé pour l'analyse salariale"""
    return {
        "message": "Analyse salariale simulée",
        "user": current_user["email"],
        "data": data.dict(),
        "result": {
            "moyenne": 8000,
            "ecart": -1000,
            "ecart_pourcent": -12.5,
            "recommandations": ["Test recommendation"]
        }
    }

@app.post("/api/coaching/coaching")
async def generate_plan(
    data: CoachingRequest,
    current_user: dict = Depends(get_current_user)
):
    """Endpoint protégé pour le coaching"""
    return {
        "message": "Plan de coaching simulé",
        "user": current_user["email"],
        "data": data.dict(),
        "plan": {
            "objectif": data.goal,
            "etapes": ["Étape 1", "Étape 2", "Étape 3"]
        }
    }

@app.get("/api/rag/status")
async def get_rag_status(current_user: dict = Depends(get_current_user)):
    """Endpoint protégé pour le statut RAG"""
    return {
        "message": "Statut RAG simulé",
        "user": current_user["email"],
        "status": {
            "isInitialized": True,
            "profilesCount": 100,
            "indexExists": True
        }
    }

@app.get("/api/doc-rag/status")
async def get_doc_rag_status(current_user: dict = Depends(get_current_user)):
    """Endpoint protégé pour le statut Doc RAG"""
    return {
        "message": "Statut Doc RAG simulé",
        "user": current_user["email"],
        "status": {
            "index_ready": True,
            "documents_count": 50
        }
    }

if __name__ == "__main__":
    print("🚀 Démarrage du serveur de test d'authentification...")
    print("📝 Ce serveur simule l'authentification JWT pour les tests")
    print("🔗 URL: http://localhost:8000")
    print("📚 Documentation: http://localhost:8000/docs")
    print("🔒 Tous les endpoints métier nécessitent un token Bearer valide")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
