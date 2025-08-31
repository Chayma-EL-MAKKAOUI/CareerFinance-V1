#!/usr/bin/env python3
"""
Script pour tester la connexion au serveur
"""

import requests
import time

def test_server():
    """Tester la connexion au serveur"""
    print("🔍 Test de connexion au serveur...")
    
    # Test du serveur principal
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Serveur principal accessible")
            print(f"   Réponse: {response.json()}")
            return True
        else:
            print(f"❌ Serveur principal - Code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Serveur principal non accessible")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_auth_endpoints():
    """Tester les endpoints d'authentification"""
    print("\n🔍 Test des endpoints d'authentification...")
    
    # Test de l'inscription
    try:
        response = requests.post("http://localhost:8000/api/auth/register", 
                               json={"email": "test@example.com", "password": "test123"},
                               timeout=5)
        if response.status_code == 200:
            print("✅ Endpoint /api/auth/register accessible")
            print(f"   Réponse: {response.json()}")
        else:
            print(f"❌ Endpoint /api/auth/register - Code: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur endpoint register: {e}")
    
    # Test de la connexion
    try:
        response = requests.post("http://localhost:8000/api/auth/login", 
                               json={"email": "test@example.com", "password": "test123"},
                               timeout=5)
        if response.status_code == 200:
            print("✅ Endpoint /api/auth/login accessible")
            print(f"   Réponse: {response.json()}")
        else:
            print(f"❌ Endpoint /api/auth/login - Code: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur endpoint login: {e}")

if __name__ == "__main__":
    print("🧪 Test de connexion au serveur backend")
    print("=" * 50)
    
    # Attendre un peu que le serveur démarre
    print("⏳ Attente du démarrage du serveur...")
    time.sleep(2)
    
    # Tester le serveur
    if test_server():
        test_auth_endpoints()
    else:
        print("\n❌ Le serveur n'est pas accessible")
        print("💡 Vérifiez que le serveur est démarré sur le port 8000")
    
    print("\n" + "=" * 50)
