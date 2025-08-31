#!/usr/bin/env python3
"""
Script de démarrage pour le système de coaching carrière avec Supabase
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """Vérifie que toutes les dépendances sont installées"""
    print("🔍 Vérification des dépendances...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'supabase',
        'sentence-transformers',
        'faiss-cpu',
        'numpy',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - MANQUANT")
    
    if missing_packages:
        print(f"\n⚠️ Packages manquants: {', '.join(missing_packages)}")
        print("Installez-les avec: pip install " + " ".join(missing_packages))
        return False
    
    return True

def check_env_file():
    """Vérifie que le fichier .env existe et contient les bonnes variables"""
    print("\n🔍 Vérification du fichier .env...")
    
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ Fichier .env non trouvé")
        print("Créez un fichier .env avec les variables suivantes:")
        print("SUPABASE_URL=votre_url_supabase")
        print("SUPABASE_KEY=votre_clé_supabase")
        return False
    
    # Charger les variables d'environnement
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            print(f"❌ {var} - MANQUANT")
        else:
            print(f"✅ {var}")
    
    if missing_vars:
        print(f"\n⚠️ Variables manquantes: {', '.join(missing_vars)}")
        return False
    
    return True

def run_migration():
    """Exécute la migration des données"""
    print("\n🔄 Migration des données...")
    
    try:
        result = subprocess.run([sys.executable, 'migrate_career_data.py'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("✅ Migration réussie")
            return True
        else:
            print(f"❌ Erreur lors de la migration: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False

def test_api():
    """Teste l'API pour vérifier qu'elle fonctionne"""
    print("\n🧪 Test de l'API...")
    
    try:
        import requests
        
        # Attendre que le serveur démarre
        time.sleep(3)
        
        response = requests.get('http://localhost:8000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ API accessible")
            return True
        else:
            print(f"❌ API non accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du test de l'API: {e}")
        return False

def start_server():
    """Démarre le serveur FastAPI"""
    print("\n🚀 Démarrage du serveur...")
    
    try:
        # Démarrer le serveur en arrière-plan
        process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 'main:app', 
            '--host', '0.0.0.0', '--port', '8000', '--reload'
        ], cwd=os.getcwd())
        
        print("✅ Serveur démarré sur http://localhost:8000")
        print("📖 Documentation: http://localhost:8000/docs")
        print("🎯 Coaching carrière: http://localhost:3000/coaching-carriere")
        
        return process
    except Exception as e:
        print(f"❌ Erreur lors du démarrage du serveur: {e}")
        return None

def main():
    """Fonction principale"""
    print("🎯 Démarrage du système de coaching carrière avec Supabase")
    print("=" * 60)
    
    # 1. Vérifier les dépendances
    if not check_dependencies():
        print("\n❌ Dépendances manquantes. Installez-les d'abord.")
        return
    
    # 2. Vérifier le fichier .env
    if not check_env_file():
        print("\n❌ Configuration manquante. Configurez votre fichier .env.")
        return
    
    # 3. Demander si l'utilisateur veut migrer les données
    print("\n🤔 Voulez-vous migrer les données de test? (y/n): ", end="")
    migrate_choice = input().lower().strip()
    
    if migrate_choice in ['y', 'yes', 'o', 'oui']:
        if not run_migration():
            print("\n❌ Échec de la migration. Vérifiez votre configuration Supabase.")
            return
    else:
        print("⏭️ Migration ignorée")
    
    # 4. Démarrer le serveur
    server_process = start_server()
    if not server_process:
        return
    
    try:
        # 5. Tester l'API
        if test_api():
            print("\n🎉 Système prêt!")
            print("\n📋 Prochaines étapes:")
            print("1. Ouvrez http://localhost:3000/coaching-carriere")
            print("2. Initialisez le système si nécessaire")
            print("3. Générez votre premier plan de carrière!")
            
            print("\n⏹️ Appuyez sur Ctrl+C pour arrêter le serveur...")
            
            # Attendre que l'utilisateur arrête le serveur
            server_process.wait()
        else:
            print("\n❌ L'API n'est pas accessible. Vérifiez les logs.")
            server_process.terminate()
    
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt du serveur...")
        server_process.terminate()
        print("✅ Serveur arrêté")

if __name__ == "__main__":
    main()
