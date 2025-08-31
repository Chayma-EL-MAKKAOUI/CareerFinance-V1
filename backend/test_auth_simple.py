#!/usr/bin/env python3
"""
Script de test simple pour vérifier que l'authentification JWT fonctionne
sans dépendre des services externes (Supabase, etc.)
"""

import requests
import json
import sys
from typing import List, Tuple

# Configuration
BASE_URL = "http://localhost:8000"

def test_public_endpoints() -> List[Tuple[bool, str]]:
    """Teste les endpoints publics qui doivent être accessibles sans token."""
    print("🔓 Test des endpoints publics:")
    
    public_endpoints = [
        ("GET", "/api/health"),
        ("GET", "/api/version"),
        ("GET", "/docs"),
    ]
    
    results = []
    for method, endpoint in public_endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            if method == "GET":
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, timeout=5)
            
            if response.status_code == 200:
                results.append((True, f"✅ {method} {endpoint} -> 200"))
                print(f"  ✅ {method} {endpoint} -> 200")
            else:
                results.append((False, f"❌ {method} {endpoint} -> {response.status_code}"))
                print(f"  ❌ {method} {endpoint} -> {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            results.append((False, f"❌ {method} {endpoint} -> Erreur de connexion"))
            print(f"  ❌ {method} {endpoint} -> Erreur de connexion (serveur non démarré ?)")
        except Exception as e:
            results.append((False, f"❌ {method} {endpoint} -> {str(e)}"))
            print(f"  ❌ {method} {endpoint} -> {str(e)}")
    
    return results

def test_protected_endpoints() -> List[Tuple[bool, str]]:
    """Teste les endpoints protégés qui doivent retourner 401 sans token."""
    print("\n🔒 Test des endpoints protégés:")
    
    protected_endpoints = [
        ("POST", "/api/salary/analyze"),
        ("POST", "/api/coaching/coaching"),
        ("GET", "/api/rag/status"),
        ("GET", "/api/doc-rag/status"),
    ]
    
    results = []
    for method, endpoint in protected_endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, timeout=5)
            elif method == "POST":
                # Données minimales pour les tests
                data = {}
                if "analyze" in endpoint:
                    data = {
                        "jobTitle": "Test Job",
                        "location": "Test Location", 
                        "experienceYears": 2,
                        "currentSalary": 5000
                    }
                elif "coaching" in endpoint:
                    data = {
                        "goal": "Test Goal",
                        "skills": ["Test Skill"],
                        "sector": "Test Sector"
                    }
                
                response = requests.post(url, json=data, timeout=5)
            
            if response.status_code == 401:
                results.append((True, f"✅ {method} {endpoint} -> 401 (protégé)"))
                print(f"  ✅ {method} {endpoint} -> 401 (protégé)")
            else:
                results.append((False, f"❌ {method} {endpoint} -> {response.status_code} (devrait être 401)"))
                print(f"  ❌ {method} {endpoint} -> {response.status_code} (devrait être 401)")
                
        except requests.exceptions.ConnectionError:
            results.append((False, f"❌ {method} {endpoint} -> Erreur de connexion"))
            print(f"  ❌ {method} {endpoint} -> Erreur de connexion")
        except Exception as e:
            results.append((False, f"❌ {method} {endpoint} -> {str(e)}"))
            print(f"  ❌ {method} {endpoint} -> {str(e)}")
    
    return results

def main():
    """Fonction principale du script de test."""
    print("🔐 Test de protection JWT - CareerFinance AI")
    print("=" * 50)
    
    # Test des endpoints publics
    public_results = test_public_endpoints()
    
    # Test des endpoints protégés
    protected_results = test_protected_endpoints()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    public_success = sum(1 for success, _ in public_results if success)
    protected_success = sum(1 for success, _ in protected_results if success)
    
    print(f"✅ Endpoints publics: {public_success}/{len(public_results)} réussis")
    print(f"✅ Endpoints protégés: {protected_success}/{len(protected_results)} réussis")
    
    total_success = public_success + protected_success
    total_tests = len(public_results) + len(protected_results)
    
    print(f"\n🎯 Score global: {total_success}/{total_tests} ({total_success/total_tests*100:.1f}%)")
    
    if total_success == total_tests:
        print("\n🎉 Tous les tests sont passés ! L'authentification JWT fonctionne correctement.")
        print("\n💡 Pour tester avec un token valide:")
        print("   1. Créez un compte via POST /api/auth/register")
        print("   2. Connectez-vous via POST /api/auth/login")
        print("   3. Utilisez le token retourné dans le header Authorization: Bearer <token>")
        return 0
    else:
        print("\n⚠️  Certains tests ont échoué. Vérifiez que le serveur est démarré et que l'authentification est configurée.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
