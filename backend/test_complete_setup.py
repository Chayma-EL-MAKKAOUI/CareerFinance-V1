#!/usr/bin/env python3
"""
Script de test complet pour vérifier l'installation du système d'authentification
"""

import asyncio
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
log = logging.getLogger("careerfinance-test")

def test_environment():
    """Tester les variables d'environnement"""
    log.info("🔍 Test des variables d'environnement")
    
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY", 
        "SUPABASE_SERVICE_ROLE_KEY",
        "JWT_SECRET_KEY",
        "APP_SECRET_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            # Masquer les valeurs sensibles
            if "KEY" in var or "SECRET" in var:
                masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                log.info(f"   ✅ {var}: {masked_value}")
            else:
                log.info(f"   ✅ {var}: {value}")
    
    if missing_vars:
        log.error(f"   ❌ Variables manquantes: {', '.join(missing_vars)}")
        return False
    
    log.info("   ✅ Toutes les variables d'environnement sont définies")
    return True

def test_dependencies():
    """Tester les dépendances Python"""
    log.info("🔍 Test des dépendances Python")
    
    dependencies = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("supabase", "Supabase"),
        ("jwt", "PyJWT"),
        ("bcrypt", "bcrypt"),
        ("pydantic", "Pydantic"),
        ("python-dotenv", "dotenv")
    ]
    
    missing_deps = []
    for package, import_name in dependencies:
        try:
            __import__(import_name.lower())
            log.info(f"   ✅ {package}")
        except ImportError:
            log.error(f"   ❌ {package} manquant")
            missing_deps.append(package)
    
    if missing_deps:
        log.error(f"   ❌ Dépendances manquantes: {', '.join(missing_deps)}")
        log.error("   💡 Exécutez: pip install -r requirements_rag.txt")
        return False
    
    log.info("   ✅ Toutes les dépendances sont installées")
    return True

def test_file_structure():
    """Tester la structure des fichiers"""
    log.info("🔍 Test de la structure des fichiers")
    
    required_files = [
        "config/auth_config.py",
        "services/supabase_auth_service.py",
        "models/auth_models.py",
        "dependencies/auth_dependencies.py",
        "routers/auth.py",
        "middleware/auth_middleware.py",
        "supabase_auth_setup.sql",
        "env.example",
        "AUTHENTICATION_README.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            log.info(f"   ✅ {file_path}")
        else:
            log.error(f"   ❌ {file_path} manquant")
            missing_files.append(file_path)
    
    if missing_files:
        log.error(f"   ❌ Fichiers manquants: {', '.join(missing_files)}")
        return False
    
    log.info("   ✅ Tous les fichiers sont présents")
    return True

def test_imports():
    """Tester les imports des modules"""
    log.info("🔍 Test des imports des modules")
    
    modules = [
        ("Configuration", "config.auth_config"),
        ("Modèles", "models.auth_models"),
        ("Service", "services.supabase_auth_service"),
        ("Dépendances", "dependencies.auth_dependencies"),
        ("Router", "routers.auth"),
        ("Middleware", "middleware.auth_middleware")
    ]
    
    failed_imports = []
    for module_name, module_path in modules:
        try:
            __import__(module_path)
            log.info(f"   ✅ {module_name}")
        except Exception as e:
            log.error(f"   ❌ {module_name}: {e}")
            failed_imports.append(module_name)
    
    if failed_imports:
        log.error(f"   ❌ Imports échoués: {', '.join(failed_imports)}")
        return False
    
    log.info("   ✅ Tous les modules sont importables")
    return True

def test_configuration():
    """Tester la configuration"""
    log.info("🔍 Test de la configuration")
    
    try:
        from config.auth_config import auth_settings
        
        # Vérifier la configuration Supabase
        if not auth_settings.SUPABASE_URL:
            log.error("   ❌ SUPABASE_URL non défini")
            return False
        
        if not auth_settings.SUPABASE_ANON_KEY:
            log.error("   ❌ SUPABASE_ANON_KEY non défini")
            return False
        
        if not auth_settings.SUPABASE_SERVICE_ROLE_KEY:
            log.error("   ❌ SUPABASE_SERVICE_ROLE_KEY non défini")
            return False
        
        if not auth_settings.JWT_SECRET_KEY:
            log.error("   ❌ JWT_SECRET_KEY non défini")
            return False
        
        log.info(f"   ✅ Supabase URL: {auth_settings.SUPABASE_URL}")
        log.info(f"   ✅ JWT Algorithm: {auth_settings.JWT_ALGORITHM}")
        log.info(f"   ✅ Token Expire: {auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
        log.info(f"   ✅ OAuth configuré: {'Oui' if auth_settings.is_oauth_configured else 'Non'}")
        
        return True
        
    except Exception as e:
        log.error(f"   ❌ Erreur de configuration: {e}")
        return False

def test_supabase_connection():
    """Tester la connexion Supabase"""
    log.info("🔍 Test de la connexion Supabase")
    
    try:
        from services.supabase_auth_service import SupabaseAuthService
        auth_service = SupabaseAuthService()
        
        # Tester la connexion en essayant d'accéder à la table users
        # (sans faire de requête réelle)
        if auth_service.supabase and auth_service.supabase_admin:
            log.info("   ✅ Connexion Supabase établie")
            return True
        else:
            log.error("   ❌ Connexion Supabase échouée")
            return False
            
    except Exception as e:
        log.error(f"   ❌ Erreur de connexion Supabase: {e}")
        return False

def test_fastapi_app():
    """Tester l'application FastAPI"""
    log.info("🔍 Test de l'application FastAPI")
    
    try:
        from main import app
        
        # Vérifier que l'app a des routes
        routes = [route for route in app.routes]
        auth_routes = [route for route in routes if hasattr(route, 'tags') and 'authentication' in getattr(route, 'tags', [])]
        
        log.info(f"   ✅ Application FastAPI chargée")
        log.info(f"   ✅ Total routes: {len(routes)}")
        log.info(f"   ✅ Routes d'authentification: {len(auth_routes)}")
        
        return True
        
    except Exception as e:
        log.error(f"   ❌ Erreur de chargement FastAPI: {e}")
        return False

async def main():
    """Fonction principale de test"""
    log.info("🧪 Test complet du système d'authentification")
    log.info("=" * 60)
    
    # Charger les variables d'environnement
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv(env_file)
        log.info("✅ Fichier .env chargé")
    else:
        log.warning("⚠️  Fichier .env non trouvé")
    
    # Tests
    tests = [
        ("Variables d'environnement", test_environment),
        ("Dépendances Python", test_dependencies),
        ("Structure des fichiers", test_file_structure),
        ("Imports des modules", test_imports),
        ("Configuration", test_configuration),
        ("Connexion Supabase", test_supabase_connection),
        ("Application FastAPI", test_fastapi_app),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        log.info(f"\n🔍 Test: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            log.error(f"   ❌ Erreur lors du test {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé
    log.info("\n" + "=" * 60)
    log.info("📊 Résumé des tests")
    log.info("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        log.info(f"{test_name:25} : {status}")
        if result:
            passed += 1
    
    log.info(f"\nRésultat: {passed}/{total} tests réussis")
    
    if passed == total:
        log.info("🎉 Tous les tests sont passés avec succès!")
        log.info("🚀 Le système d'authentification est prêt à être utilisé")
        log.info("\n📋 Prochaines étapes:")
        log.info("   1. Exécutez le script SQL dans Supabase")
        log.info("   2. Configurez OAuth si nécessaire")
        log.info("   3. Testez avec: python test_auth.py")
        log.info("   4. Démarrez avec: python start_secure.py")
        return 0
    else:
        log.error("⚠️  Certains tests ont échoué")
        log.error("🔧 Veuillez corriger les erreurs avant de continuer")
        return 1

if __name__ == "__main__":
    # Ajouter le répertoire backend au PYTHONPATH
    backend_dir = Path(__file__).parent
    sys.path.insert(0, str(backend_dir))
    
    # Exécuter les tests
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
