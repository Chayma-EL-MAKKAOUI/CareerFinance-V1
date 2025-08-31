#!/usr/bin/env python3
"""
Test direct de l'authentification JWT
"""

import requests
import time

def test_auth():
    """Test de l'authentification JWT"""
    print("🔐 Test de l'authentification JWT")
    print("=" * 50)
    
    # Test des endpoints publics (doivent fonctionner)
    print("Test des endpoints publics:")
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ GET /api/health -> 200 (public)")
        else:
            print(f"  ❌ GET /api/health -> {response.status_code}")
    except Exception as e:
        print(f"  ❌ GET /api/health -> Erreur: {e}")
    
    # Test des endpoints protégés (doivent retourner 401)
    print("\nTest des endpoints protégés (doivent retourner 401):")
    
    # Test 1: GET /api/rag/status
    try:
        response = requests.get("http://localhost:8000/api/rag/status", timeout=5)
        if response.status_code == 401:
            print("  ✅ GET /api/rag/status -> 401 (protégé)")
        else:
            print(f"  ❌ GET /api/rag/status -> {response.status_code} (devrait être 401)")
    except Exception as e:
        print(f"  ❌ GET /api/rag/status -> Erreur: {e}")
    
    # Test 2: POST /api/salary/analyze
    try:
        data = {"jobTitle": "Test", "location": "Test", "experienceYears": 2, "currentSalary": 5000}
        response = requests.post("http://localhost:8000/api/salary/analyze", json=data, timeout=5)
        if response.status_code == 401:
            print("  ✅ POST /api/salary/analyze -> 401 (protégé)")
        else:
            print(f"  ❌ POST /api/salary/analyze -> {response.status_code} (devrait être 401)")
    except Exception as e:
        print(f"  ❌ POST /api/salary/analyze -> Erreur: {e}")
    
    # Test 3: POST /api/coaching/coaching
    try:
        data = {"goal": "Test", "skills": ["Test"], "sector": "Test"}
        response = requests.post("http://localhost:8000/api/coaching/coaching", json=data, timeout=5)
        if response.status_code == 401:
            print("  ✅ POST /api/coaching/coaching -> 401 (protégé)")
        else:
            print(f"  ❌ POST /api/coaching/coaching -> {response.status_code} (devrait être 401)")
    except Exception as e:
        print(f"  ❌ POST /api/coaching/coaching -> Erreur: {e}")
    
    print("\n" + "=" * 50)
    print("Résultat:")
    print("✅ Si tous les endpoints protégés retournent 401, l'authentification fonctionne !")
    print("❌ Si certains retournent 200, l'authentification n'est pas active.")

if __name__ == "__main__":
    test_auth()
