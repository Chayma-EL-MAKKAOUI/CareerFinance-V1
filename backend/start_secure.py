#!/usr/bin/env python3
"""
Script de démarrage sécurisé pour CareerFinance AI avec authentification
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from config.auth_config import auth_settings

print("SUPABASE_ANON_KEY =", auth_settings.SUPABASE_ANON_KEY)
print("JWT_SECRET_KEY =", auth_settings.JWT_SECRET_KEY)
print("APP_SECRET_KEY =", auth_settings.APP_SECRET_KEY)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
log = logging.getLogger("careerfinance-secure")

def check_environment():
    """Vérifier que toutes les variables d'environnement sont définies"""
    required_vars = [
        "SUPABASE_URL",  # Seule variable vraiment requise
    ]
    
    # Vérifier les variables vraiment requises
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        log.error(f"❌ Variables d'environnement manquantes: {', '.join(missing_vars)}")
        log.error("Veuillez créer un fichier .env avec au minimum SUPABASE_URL")
        return False
    
    # Vérifier les variables optionnelles
    optional_vars = [
        "SUPABASE_ANON_KEY", 
        "SUPABASE_SERVICE_ROLE_KEY",
        "JWT_SECRET_KEY",
        "APP_SECRET_KEY"
    ]
    
    missing_optional = []
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_optional:
        log.warning(f"⚠️  Variables optionnelles manquantes: {', '.join(missing_optional)}")
        log.info("✅ Mode développement détecté - utilisation de valeurs par défaut")
    else:
        log.info("✅ Toutes les variables d'environnement sont définies")
    
    return True

def check_dependencies():
    """Vérifier que toutes les dépendances sont installées"""
    try:
        import fastapi
        import uvicorn
        import supabase
        import jwt
        import bcrypt
        import pydantic
        log.info("✅ Toutes les dépendances sont installées")
        return True
    except ImportError as e:
        log.error(f"❌ Dépendance manquante: {e}")
        log.error("Exécutez: pip install -r requirements_rag.txt")
        return False

def check_config_files():
    """Vérifier que tous les fichiers de configuration existent"""
    required_files = [
        "config/auth_config.py",
        "services/supabase_auth_service.py",
        "models/auth_models.py",
        "dependencies/auth_dependencies.py",
        "routers/auth.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        log.error(f"❌ Fichiers de configuration manquants: {', '.join(missing_files)}")
        return False
    
    log.info("✅ Tous les fichiers de configuration sont présents")
    return True

def test_auth_system():
    """Tester le système d'authentification"""
    try:
        from config.auth_config import auth_settings
        log.info("✅ Configuration d'authentification chargée")
        
        # Vérifier la configuration Supabase (URL requise)
        if not auth_settings.SUPABASE_URL:
            log.error("❌ Configuration Supabase invalide: SUPABASE_URL manquant")
            return False
        
        # En mode dev, les autres variables peuvent avoir des valeurs par défaut
        if os.getenv("ENV", "dev") == "dev":
            log.info("✅ Mode développement - configuration flexible")
            log.info(f"   - Supabase URL: {auth_settings.SUPABASE_URL}")
            log.info(f"   - JWT Algorithm: {auth_settings.JWT_ALGORITHM}")
            log.info(f"   - Token Expire: {auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
        else:
            # En production, vérifier toutes les variables
            if not auth_settings.SUPABASE_ANON_KEY or not auth_settings.SUPABASE_SERVICE_ROLE_KEY:
                log.error("❌ Configuration Supabase invalide en production")
                return False
            log.info("✅ Configuration Supabase valide (production)")
        
        return True
        
    except Exception as e:
        log.error(f"❌ Erreur lors du test du système d'authentification: {e}")
        return False

def main():
    """Fonction principale"""
    log.info("🚀 Démarrage sécurisé de CareerFinance AI")
    log.info("=" * 50)
    
    # Charger les variables d'environnement
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv(env_file)
        log.info("✅ Fichier .env chargé")
    else:
        log.warning("⚠️  Fichier .env non trouvé, utilisation des variables système")
    
    # Vérifications de sécurité
    checks = [
        ("Variables d'environnement", check_environment),
        ("Dépendances", check_dependencies),
        ("Fichiers de configuration", check_config_files),
        ("Système d'authentification", test_auth_system),
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        log.info(f"\n🔍 Vérification: {check_name}")
        if not check_func():
            all_passed = False
            break
    
    if not all_passed:
        log.error("\n❌ Échec des vérifications de sécurité")
        log.error("L'application ne peut pas démarrer en mode sécurisé")
        sys.exit(1)
    
    log.info("\n✅ Toutes les vérifications de sécurité sont passées")
    log.info("🎉 Démarrage de l'application...")
    
    # Démarrer l'application
    try:
        import uvicorn
        from main import app
        
        log.info("✅ Application chargée avec succès")
        log.info("🌐 Serveur accessible sur: http://localhost:8000")
        log.info("📚 Documentation API: http://localhost:8000/docs")
        log.info("🔐 Endpoints d'authentification: /api/auth/*")
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except Exception as e:
        log.error(f"❌ Erreur lors du démarrage de l'application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
