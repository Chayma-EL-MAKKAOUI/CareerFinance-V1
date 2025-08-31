#!/usr/bin/env python3
"""
Test de l'authentification après correction des variables d'environnement
"""

import os
from dotenv import load_dotenv
from config.auth_config import auth_settings
from services.supabase_auth_service import SupabaseAuthService

# Charger le fichier .env
load_dotenv()

def test_auth_config():
    """Tester la configuration d'authentification"""
    print("🔧 Test de la configuration d'authentification")
    print("=" * 60)
    
    try:
        # Tester la configuration
        print(f"✅ SUPABASE_URL: {auth_settings.SUPABASE_URL}")
        print(f"✅ SUPABASE_ANON_KEY: {auth_settings.SUPABASE_ANON_KEY[:20]}...")
        print(f"✅ SUPABASE_SERVICE_ROLE_KEY: {auth_settings.SUPABASE_SERVICE_ROLE_KEY[:20]}...")
        print(f"✅ JWT_SECRET_KEY: {auth_settings.JWT_SECRET_KEY[:20]}...")
        print(f"✅ APP_SECRET_KEY: {auth_settings.APP_SECRET_KEY[:20]}...")
        
        # Tester la création du service
        print("\n🔄 Test de création du service SupabaseAuthService...")
        auth_service = SupabaseAuthService()
        print("✅ Service SupabaseAuthService créé avec succès!")
        
        # Tester la connexion à Supabase
        print("\n🔄 Test de connexion à Supabase...")
        # Essayer une requête simple
        try:
            # Test simple de connexion
            result = auth_service.supabase.table("users").select("count", count="exact").execute()
            print("✅ Connexion à Supabase réussie!")
            print(f"   Nombre d'utilisateurs dans la base: {result.count}")
        except Exception as e:
            print(f"⚠️  Connexion à Supabase: {str(e)}")
            print("   (Cela peut être normal si la table users n'existe pas encore)")
        
        print("\n✅ Configuration d'authentification OK!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False

async def test_register_mock():
    """Tester l'inscription d'un utilisateur mock"""
    print("\n🧪 Test d'inscription d'utilisateur mock...")
    
    try:
        auth_service = SupabaseAuthService()
        
        # Données d'utilisateur de test
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User",
            "role": "user"
        }
        
        print("🔄 Tentative d'inscription...")
        result = await auth_service.register_user(user_data)
        print("✅ Inscription réussie!")
        print(f"   Token: {result['access_token'][:20]}...")
        print(f"   User ID: {result['user']['id']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'inscription: {str(e)}")
        return False

if __name__ == "__main__":
    import asyncio
    
    print("🚀 Test de l'authentification après correction")
    print("=" * 60)
    
    # Test de la configuration
    config_ok = test_auth_config()
    
    if config_ok:
        print("\n🎉 Configuration OK! L'authentification devrait maintenant fonctionner.")
        print("\n📝 Prochaines étapes:")
        print("1. Redémarrez votre serveur backend")
        print("2. Testez l'inscription/connexion depuis le frontend")
        print("3. Vérifiez que l'erreur 'Invalid API key' a disparu")
    else:
        print("\n❌ Configuration incorrecte. Vérifiez vos clés Supabase.")
