#!/usr/bin/env python3
"""
Serveur backend simplifié pour l'authentification
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Créer l'application FastAPI
app = FastAPI(
    title="CareerFinance AI - Auth Server",
    description="Serveur d'authentification simplifié",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Route racine"""
    return {
        "message": "CareerFinance AI - Serveur d'authentification",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Vérification de l'état du serveur"""
    return {
        "status": "healthy",
        "service": "authentication",
        "supabase_configured": bool(
            os.getenv("SUPABASE_URL") and 
            os.getenv("SUPABASE_ANON_KEY") and 
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
    }

@app.get("/api/auth/health")
async def auth_health():
    """Vérification de l'état de l'authentification"""
    return {
        "status": "healthy",
        "service": "authentication",
        "supabase_configured": bool(
            os.getenv("SUPABASE_URL") and 
            os.getenv("SUPABASE_ANON_KEY") and 
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
    }

@app.post("/api/auth/register")
async def register():
    """Route d'inscription (mock pour test)"""
    return {
        "success": True,
        "message": "Inscription réussie (mode test)",
        "access_token": "test-token-123",
        "user": {
            "id": 1,
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User"
        }
    }

@app.post("/api/auth/login")
async def login():
    """Route de connexion (mock pour test)"""
    return {
        "success": True,
        "message": "Connexion réussie (mode test)",
        "access_token": "test-token-123",
        "user": {
            "id": 1,
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User"
        }
    }

@app.get("/api/auth/me")
async def get_current_user():
    """Route pour récupérer l'utilisateur actuel (mock pour test)"""
    return {
        "id": 1,
        "email": "test@example.com",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "role": "user"
    }

@app.post("/api/auth/logout")
async def logout():
    """Route de déconnexion"""
    return {
        "success": True,
        "message": "Déconnexion réussie"
    }

if __name__ == "__main__":
    print("🚀 Démarrage du serveur d'authentification simplifié...")
    print("📍 URL: http://localhost:8002")
    print("📋 API Docs: http://localhost:8002/docs")
    print("🔧 Mode: Test (authentification mock)")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )
