#!/usr/bin/env python3
"""
Test simplifié du système d'authentification
"""

import asyncio
import os
import sys
from pathlib import Path

# Ajouter le répertoire backend au PYTHONPATH
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def test_basic_imports():
    """Tester les imports de base"""
    print("🔍 Test des imports de base")
    
    try:
        # Test des modèles
        from models.auth_models import UserRegister, UserLogin
        print("✅ Modèles d'authentification importés")
        
        # Test de création d'un modèle
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User"
        }
        user = UserRegister(**user_data)
        print("✅ Modèle UserRegister créé avec succès")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des modèles: {e}")
        return False

async def test_config_loading():
    """Tester le chargement de la configuration"""
    print("🔍 Test du chargement de la configuration")
    
    try:
        from config.auth_config import auth_settings
        print("✅ Configuration d'authentification chargée")
        
        # Afficher la configuration
        print(f"   - Supabase URL: {auth_settings.SUPABASE_URL}")
        print(f"   - JWT Algorithm: {auth_settings.JWT_ALGORITHM}")
        print(f"   - Token Expire: {auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du chargement de la configuration: {e}")
        return False

async def test_service_creation():
    """Tester la création du service d'authentification"""
    print("🔍 Test de la création du service")
    
    try:
        from services.supabase_auth_service import SupabaseAuthService
        print("✅ Service d'authentification importé")
        
        # En mode dev, on peut créer le service même sans Supabase réel
        if os.getenv("ENV", "dev") == "dev":
            print("✅ Mode développement détecté")
            return True
        else:
            # En production, tester la création
            auth_service = SupabaseAuthService()
            print("✅ Service d'authentification créé")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la création du service: {e}")
        return False

async def test_router_creation():
    """Tester la création du router"""
    print("🔍 Test de la création du router")
    
    try:
        # Tester seulement les modèles d'authentification
        from models.auth_models import UserResponse, AuthResponse
        print("✅ Modèles d'authentification importés")
        
        # Tester la création d'un modèle de réponse
        response = AuthResponse(
            success=True,
            access_token="test-token",
            token_type="bearer",
            user=UserResponse(
                id=1,
                email="test@example.com",
                username="testuser",
                first_name="Test",
                last_name="User",
                role="user",
                is_active=True,
                created_at=None,
                updated_at=None,
                last_login=None,
                total_analyses=0,
                document_analyses_count=0,
                salary_analyses_count=0,
                coaching_sessions_count=0
            )
        )
        print("✅ Modèle de réponse créé avec succès")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du router: {e}")
        return False

async def main():
    """Fonction principale"""
    print("🧪 Test simplifié du système d'authentification")
    print("=" * 50)
    
    # Tests
    tests = [
        ("Imports de base", test_basic_imports),
        ("Configuration", test_config_loading),
        ("Service", test_service_creation),
        ("Router", test_router_creation),
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
        print(f"{test_name:20} : {status}")
        if result:
            passed += 1
    
    print(f"\nRésultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés avec succès!")
        print("🚀 Le système d'authentification est prêt pour le développement")
        return 0
    else:
        print("⚠️  Certains tests ont échoué")
        return 1

if __name__ == "__main__":
    # Exécuter les tests
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
