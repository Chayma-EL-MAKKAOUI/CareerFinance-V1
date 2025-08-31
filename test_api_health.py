#!/usr/bin/env python3
"""
Script de diagnostic rapide pour vérifier l'état de l'API CareerFinance AI
"""

import requests
import sys
import time

def print_status(message: str, status: str = "INFO"):
    """Afficher un message avec un statut coloré"""
    colors = {
        "INFO": "\033[94m",    # Bleu
        "SUCCESS": "\033[92m", # Vert
        "ERROR": "\033[91m",   # Rouge
        "WARNING": "\033[93m", # Jaune
        "RESET": "\033[0m"     # Reset
    }
    print(f"{colors.get(status, colors['INFO'])}[{status}] {message}{colors['RESET']}")

def test_api_health():
    """Test rapide de la santé de l'API"""
    print_status("🔍 Test rapide de l'API CareerFinance AI", "INFO")
    print_status("=" * 50, "INFO")
    
    # Test 1: Santé générale
    try:
        start_time = time.time()
        response = requests.get("http://localhost:8000/api/health", timeout=3)
        end_time = time.time()
        
        if response.status_code == 200:
            print_status(f"✅ API en ligne (réponse en {end_time - start_time:.2f}s)", "SUCCESS")
        else:
            print_status(f"❌ API retourne {response.status_code}", "ERROR")
            return False
    except requests.exceptions.Timeout:
        print_status("❌ Timeout - API ne répond pas", "ERROR")
        return False
    except requests.exceptions.ConnectionError:
        print_status("❌ Impossible de se connecter à l'API", "ERROR")
        print_status("💡 Vérifiez que le backend est démarré: python main.py", "WARNING")
        return False
    except Exception as e:
        print_status(f"❌ Erreur inattendue: {e}", "ERROR")
        return False
    
    # Test 2: Service d'authentification
    try:
        start_time = time.time()
        response = requests.get("http://localhost:8000/api/auth/health", timeout=3)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            supabase_configured = data.get('supabase_configured', False)
            print_status(f"✅ Service d'auth en ligne (réponse en {end_time - start_time:.2f}s)", "SUCCESS")
            if supabase_configured:
                print_status("✅ Supabase configuré", "SUCCESS")
            else:
                print_status("⚠️ Supabase non configuré", "WARNING")
        else:
            print_status(f"❌ Service d'auth retourne {response.status_code}", "ERROR")
    except Exception as e:
        print_status(f"❌ Erreur service d'auth: {e}", "ERROR")
    
    # Test 3: Test de connexion simple
    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:8000/api/auth/login",
            json={"email": "test@test.com", "password": "test"},
            headers={"Content-Type": "application/json"},
            timeout=3
        )
        end_time = time.time()
        
        if response.status_code in [200, 401]:  # 401 est normal pour des credentials invalides
            print_status(f"✅ Endpoint de connexion accessible (réponse en {end_time - start_time:.2f}s)", "SUCCESS")
        else:
            print_status(f"❌ Endpoint de connexion retourne {response.status_code}", "ERROR")
    except Exception as e:
        print_status(f"❌ Erreur endpoint de connexion: {e}", "ERROR")
    
    print_status("=" * 50, "INFO")
    print_status("🎯 Diagnostic terminé", "SUCCESS")
    return True

if __name__ == "__main__":
    test_api_health()
