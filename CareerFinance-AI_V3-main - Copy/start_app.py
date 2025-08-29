#!/usr/bin/env python3
"""
Script de démarrage pour l'application CareerFinance AI
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_frontend_dependencies():
    """Vérifie les dépendances frontend"""
    print("🔍 Vérification des dépendances frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Dossier frontend non trouvé")
        return False
    
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("⚠️ node_modules manquant, installation...")
        try:
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
            print("✅ Dépendances frontend installées")
        except subprocess.CalledProcessError:
            print("❌ Erreur lors de l'installation des dépendances frontend")
            return False
    else:
        print("✅ Dépendances frontend présentes")
    
    return True

def create_env_file():
    """Crée le fichier .env s'il n'existe pas"""
    env_file = Path("backend/.env")
    if not env_file.exists():
        print("\n📝 Création du fichier .env...")
        env_content = """# Configuration Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Modèle d'embedding pour le coaching carrière
CAREER_EMBED_MODEL=sentence-transformers/paraphrase-multilingual-mpnet-base-v2

# Configuration CORS
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000", "*"]
CORS_CREDENTIALS=true

# Configuration de l'application
APP_NAME="CareerFinance AI"
APP_VERSION="v2"
ENV="dev"
"""
        env_file.write_text(env_content)
        print("✅ Fichier .env créé")
        print("⚠️ IMPORTANT: Configurez vos credentials Supabase dans backend/.env")
        return False
    else:
        print("✅ Fichier .env présent")
        return True

def start_backend():
    """Démarre le serveur backend"""
    print("\n🚀 Démarrage du serveur backend...")
    
    try:
        process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 'main:app', 
            '--host', '0.0.0.0', '--port', '8000', '--reload'
        ], cwd="backend")
        
        print("✅ Serveur backend démarré sur http://localhost:8000")
        print("📖 Documentation: http://localhost:8000/docs")
        
        return process
    except Exception as e:
        print(f"❌ Erreur lors du démarrage du backend: {e}")
        return None

def start_frontend():
    """Démarre le serveur frontend"""
    print("\n🚀 Démarrage du serveur frontend...")
    
    try:
        process = subprocess.Popen([
            "npm", "run", "dev"
        ], cwd="frontend")
        
        print("✅ Serveur frontend démarré sur http://localhost:3000")
        
        return process
    except Exception as e:
        print(f"❌ Erreur lors du démarrage du frontend: {e}")
        return None

def main():
    """Fonction principale"""
    print("🎯 Démarrage de CareerFinance AI")
    print("=" * 50)
    
    # 1. Vérifier les dépendances frontend
    if not check_frontend_dependencies():
        print("\n❌ Dépendances frontend manquantes.")
        return
    
    # 2. Vérifier/créer le fichier .env
    env_configured = create_env_file()
    if not env_configured:
        print("\n⚠️ Configurez vos credentials Supabase dans backend/.env avant de continuer")
        print("Puis relancez ce script.")
        return
    
    # 3. Démarrer le backend
    backend_process = start_backend()
    if not backend_process:
        return
    
    # Attendre un peu que le backend démarre
    time.sleep(3)
    
    # 4. Démarrer le frontend
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        return
    
    print("\n🎉 Application démarrée avec succès!")
    print("\n📋 URLs importantes:")
    print("   - Frontend: http://localhost:3000")
    print("   - Backend API: http://localhost:8000")
    print("   - Documentation API: http://localhost:8000/docs")
    print("   - Coaching carrière: http://localhost:3000/coaching-carriere")
    
    print("\n⏹️ Appuyez sur Ctrl+C pour arrêter les serveurs...")
    
    try:
        # Attendre que l'utilisateur arrête
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt des serveurs...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Serveurs arrêtés")

if __name__ == "__main__":
    main()
