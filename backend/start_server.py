#!/usr/bin/env python3
"""
Script simple pour démarrer le serveur backend
"""

import uvicorn
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

if __name__ == "__main__":
    print("🚀 Démarrage du serveur backend...")
    print("📍 URL: http://localhost:8000")
    print("📋 API Docs: http://localhost:8000/docs")
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        print("🔧 Vérifiez que toutes les dépendances sont installées")
