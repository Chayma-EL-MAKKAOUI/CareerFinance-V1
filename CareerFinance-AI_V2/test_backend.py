#!/usr/bin/env python3
"""
Script de test pour vérifier que le backend fonctionne
"""

import requests
import time

def test_backend():
    """Teste le backend"""
    print("🧪 Test du backend...")
    
    # Attendre que le serveur démarre
    time.sleep(2)
    
    try:
        # Test de santé
        response = requests.get('http://localhost:8000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ Backend accessible")
            print(f"   Réponse: {response.json()}")
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
        response = requests.get('http://localhost:8000/api/supabase-career/', timeout=5)
        if response.status_code == 200:
            print("✅ API coaching carrière accessible")
        else:
            print(f"❌ API coaching carrière: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur API coaching: {e}")
    
    return True

if __name__ == "__main__":
    test_backend()
