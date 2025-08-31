#!/usr/bin/env python3
"""
Script de test pour le système d'authentification
"""

import asyncio
import os
import sys
from pathlib import Path

# Ajouter le répertoire backend au PYTHONPATH
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def test_auth_service():
    """Tester le service d'authentification"""
    try:
        from services.supabase_auth_service import SupabaseAuthService
        print("✅ Service d'authentification importé avec succès")
        
        # Tester l'initialisation
        auth_service = SupabaseAuthService()
        print("✅ Service d'authentification initialisé avec succès")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test du service d'authentification: {e}")
        return False

async def test_auth_models():
    """Tester les modèles d'authentification"""
    try:
        from models.auth_models import UserRegister, UserLogin, AuthResponse
        print("✅ Modèles d'authentification importés avec succès")
        
        # Tester la création d'un modèle
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        user_register = UserRegister(**user_data)
        print("✅ Modèle UserRegister créé avec succès")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des modèles: {e}")
        return False

async def test_auth_dependencies():
    """Tester les dépendances d'authentification"""
    try:
        from dependencies.auth_dependencies import get_current_user, require_user
        print("✅ Dépendances d'authentification importées avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des dépendances: {e}")
        return False

async def test_auth_router():
    """Tester le router d'authentification"""
    try:
        from routers.auth import router
        print("✅ Router d'authentification importé avec succès")
        
        # Vérifier que le router a des routes
        routes = [route for route in router.routes]
        print(f"✅ Router contient {len(routes)} routes")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test du router: {e}")
        return False

async def test_config():
    """Tester la configuration"""
    try:
        from config.auth_config import auth_settings
        print("✅ Configuration d'authentification importée avec succès")
        
        # Afficher la configuration (sans les secrets)
        print(f"   - Supabase URL: {'✅' if auth_settings.SUPABASE_URL else '❌'}")
        print(f"   - JWT Algorithm: {auth_settings.JWT_ALGORITHM}")
        print(f"   - Token Expire: {auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
        print(f"   - OAuth configuré: {'✅' if auth_settings.is_oauth_configured else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de la configuration: {e}")
        return False

async def main():
    """Fonction principale de test"""
    print("🧪 Test du système d'authentification")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_config),
        ("Modèles", test_auth_models),
        ("Service", test_auth_service),
        ("Dépendances", test_auth_dependencies),
        ("Router", test_auth_router),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Test: {test_name}")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur lors du test {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 Résumé des tests")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:15} : {status}")
        if result:
            passed += 1
    
    print(f"\nRésultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés avec succès!")
        return 0
    else:
        print("⚠️  Certains tests ont échoué")
        return 1

if __name__ == "__main__":
    # Charger les variables d'environnement
    from dotenv import load_dotenv
    load_dotenv()
    
    # Exécuter les tests
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
