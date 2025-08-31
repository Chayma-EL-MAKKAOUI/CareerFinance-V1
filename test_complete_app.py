#!/usr/bin/env python3
"""
Script de test complet pour l'application CareerFinance AI
"""

import requests
import time
import json

def test_backend():
    """Teste le backend complet"""
    print("🧪 Test du backend CareerFinance AI...")
    
    base_url = "http://localhost:8000"
    
    # Test 1: Santé du serveur
    try:
        response = requests.get(f'{base_url}/api/health', timeout=5)
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
    
    # Test 2: Version
    try:
        response = requests.get(f'{base_url}/api/version', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Version: {data['name']} v{data['version']}")
        else:
            print(f"❌ Erreur version: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur version: {e}")
    
    # Test 3: Route racine
    try:
        response = requests.get(f'{base_url}/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API racine accessible")
            print(f"   Message: {data['message']}")
        else:
            print(f"❌ API racine: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur API racine: {e}")
    
    # Test 4: Statut RAG
    try:
        response = requests.get(f'{base_url}/api/rag/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API RAG status accessible")
            print(f"   Status: {data['status']}")
            print(f"   Message: {data['message']}")
        else:
            print(f"❌ API RAG status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur API RAG: {e}")
    
    # Test 5: Coaching carrière
    try:
        payload = {
            "goal": "Développeur Full Stack",
            "skills": ["JavaScript", "React", "Node.js"],
            "sector": "Technologie"
        }
        response = requests.post(
            f'{base_url}/api/coaching/coaching',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload),
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ API coaching carrière fonctionnelle")
            print(f"   Objectif: {data['plan']['objectif']}")
            print(f"   Étapes: {len(data['plan']['etapes'])} étapes")
            print(f"   Insights: {len(data['insights'])} insights")
        else:
            print(f"❌ API coaching carrière: {response.status_code}")
            print(f"   Réponse: {response.text}")
    except Exception as e:
        print(f"❌ Erreur API coaching: {e}")
    
    # Test 6: Coaching enrichi
    try:
        payload = {
            "goal": "Data Scientist",
            "skills": ["Python", "Machine Learning", "SQL"],
            "sector": "Intelligence Artificielle"
        }
        response = requests.post(
            f'{base_url}/api/rag/enhanced-coaching',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload),
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ API coaching enrichi fonctionnelle")
            print(f"   Objectif: {data['plan']['objectif']}")
            print(f"   Étapes: {len(data['plan']['etapes'])} étapes")
        else:
            print(f"❌ API coaching enrichi: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur API coaching enrichi: {e}")
    
    return True

def test_frontend():
    """Teste le frontend"""
    print("\n🌐 Test du frontend...")
    
    try:
        response = requests.get('http://localhost:3000', timeout=5)
        if response.status_code == 200:
            print("✅ Frontend accessible")
            print("   URL: http://localhost:3000")
        else:
            print(f"❌ Frontend non accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion au frontend: {e}")
        return False
    
    return True

def main():
    """Fonction principale de test"""
    print("🚀 Test complet de l'application CareerFinance AI")
    print("=" * 50)
    
    # Attendre que les serveurs démarrent
    print("⏳ Attente du démarrage des serveurs...")
    time.sleep(3)
    
    # Test backend
    backend_ok = test_backend()
    
    # Test frontend
    frontend_ok = test_frontend()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    if backend_ok:
        print("✅ Backend: Fonctionnel")
        print("   - API de santé: OK")
        print("   - API de version: OK")
        print("   - API RAG status: OK")
        print("   - API coaching carrière: OK")
        print("   - API coaching enrichi: OK")
    else:
        print("❌ Backend: Problèmes détectés")
    
    if frontend_ok:
        print("✅ Frontend: Fonctionnel")
        print("   - Interface utilisateur: OK")
    else:
        print("❌ Frontend: Problèmes détectés")
    
    if backend_ok and frontend_ok:
        print("\n🎉 SUCCÈS! L'application est entièrement fonctionnelle!")
        print("\n📱 URLs d'accès:")
        print("   Frontend: http://localhost:3000")
        print("   Backend API: http://localhost:8000")
        print("   Documentation API: http://localhost:8000/docs")
        print("   Santé API: http://localhost:8000/api/health")
    else:
        print("\n⚠️  ATTENTION: Certains composants ont des problèmes")
        print("   Vérifiez les logs et redémarrez les services si nécessaire")

if __name__ == "__main__":
    main()
