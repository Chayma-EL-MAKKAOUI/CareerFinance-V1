#!/usr/bin/env python3
"""
Script de test pour la version simplifiée du backend
"""

import requests
import time

def test_simple_backend():
    """Teste le backend simplifié"""
    print("🧪 Test du backend simplifié...")
    
    # Attendre que le serveur démarre
    time.sleep(3)
    
    try:
        # Test de santé
        response = requests.get('http://localhost:8000/api/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend accessible")
            print(f"   Message: {data['message']}")
        else:
            print(f"❌ Backend non accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion au backend: {e}")
        return False
    
    try:
        # Test de la version
        response = requests.get('http://localhost:8000/api/version', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Version: {data['name']} v{data['version']}")
        else:
            print(f"❌ Erreur version: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur version: {e}")
    
    try:
        # Test du coaching carrière
        response = requests.get('http://localhost:8000/api/coaching-carriere', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API coaching carrière accessible")
            print(f"   Status: {data['status']}")
            print(f"   Features: {', '.join(data['features'][:2])}...")
        else:
            print(f"❌ API coaching carrière: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur API coaching: {e}")
    
    try:
        # Test de la racine
        response = requests.get('http://localhost:8000/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API racine accessible")
            print(f"   Message: {data['message']}")
        else:
            print(f"❌ API racine: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur API racine: {e}")
    
    print("\n🎉 Tests terminés!")
    print("📖 Documentation: http://localhost:8000/docs")
    print("🎯 API Coaching: http://localhost:8000/api/coaching-carriere")
    
    return True

if __name__ == "__main__":
    test_simple_backend()
