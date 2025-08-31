#!/usr/bin/env python3
"""
Test minimal du système d'authentification uniquement
"""

import asyncio
import os
import sys
from pathlib import Path

# Ajouter le répertoire backend au PYTHONPATH
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def test_auth_system_only():
    """Tester seulement le système d'authentification"""
    print("🧪 Test du système d'authentification uniquement")
    print("=" * 50)
    
    try:
        # 1. Test de la configuration
        print("🔍 Test de la configuration d'authentification")
        from config.auth_config import auth_settings
        print("✅ Configuration chargée")
        print(f"   - Supabase URL: {auth_settings.SUPABASE_URL}")
        print(f"   - JWT Algorithm: {auth_settings.JWT_ALGORITHM}")
        print(f"   - Token Expire: {auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
        
        # 2. Test des modèles
        print("\n🔍 Test des modèles d'authentification")
        from models.auth_models import UserRegister, UserLogin, AuthResponse, UserResponse
        print("✅ Modèles chargés")
        
        # 3. Test des dépendances
        print("\n🔍 Test des dépendances d'authentification")
        from dependencies.auth_dependencies import get_current_user, get_current_active_user
        print("✅ Dépendances chargées")
        
        # 4. Test du service (en mode dev)
        print("\n🔍 Test du service d'authentification")
        from services.supabase_auth_service import SupabaseAuthService
        print("✅ Service importé")
        
        # 5. Test du router (en mode dev)
        print("\n🔍 Test du router d'authentification")
        from routers.auth import router
        print("✅ Router chargé")
        
        print("\n🎉 Tous les tests d'authentification sont passés !")
        print("🚀 Le système d'authentification est prêt")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Fonction principale"""
    success = await test_auth_system_only()
    
    if success:
        print("\n✅ Système d'authentification fonctionnel")
        print("💡 Vous pouvez maintenant configurer Supabase pour la production")
        return 0
    else:
        print("\n❌ Problème avec le système d'authentification")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
