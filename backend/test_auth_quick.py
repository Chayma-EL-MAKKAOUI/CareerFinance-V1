#!/usr/bin/env python3
"""
Test rapide de l'authentification JWT
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint_without_auth(endpoint: str, method: str = "GET", data: dict = None):
    """Teste un endpoint sans token d'authentification"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        else:
            return False, f"Méthode {method} non supportée"
        
        return response.status_code == 401, f"{method} {endpoint} -> {response.status_code}"
        
    except requests.exceptions.ConnectionError:
        return False, f"Erreur de connexion (serveur non démarré ?)"
    except Exception as e:
        return False, f"Erreur: {str(e)}"

def main():
    print("🔐 Test rapide de l'authentification JWT")
    print("=" * 50)
    
    # Test des endpoints protégés
    protected_endpoints = [
        ("GET", "/api/rag/status"),
        ("POST", "/api/salary/analyze", {"jobTitle": "Test", "location": "Test", "experienceYears": 2, "currentSalary": 5000}),
        ("POST", "/api/coaching/coaching", {"goal": "Test", "skills": ["Test"], "sector": "Test"}),
    ]
    
    print("Test des endpoints protégés (doivent retourner 401):")
    for endpoint_info in protected_endpoints:
        if len(endpoint_info) == 2:
            method, endpoint = endpoint_info
            data = None
        else:
            method, endpoint, data = endpoint_info
        
        success, message = test_endpoint_without_auth(endpoint, method, data)
        status = "✅" if success else "❌"
        print(f"  {status} {message}")
    
    print("\n" + "=" * 50)
    print("Si tous les endpoints retournent 401, l'authentification fonctionne !")
    print("Si certains retournent 200, l'authentification n'est pas active.")

if __name__ == "__main__":
    main()
