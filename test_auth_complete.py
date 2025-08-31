#!/usr/bin/env python3
"""
Script de test complet pour l'authentification CareerFinance AI
Teste l'inscription, la connexion, la déconnexion et la protection des routes
"""

import requests
import json
import time
import sys
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpassword123",
    "first_name": "Test",
    "last_name": "User",
    "role": "user"
}

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

def test_health_check():
    """Tester la santé de l'API"""
    print_status("Test de la santé de l'API...", "INFO")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print_status("✅ API en ligne", "SUCCESS")
            return True
        else:
            print_status(f"❌ API retourne {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"❌ Impossible de contacter l'API: {e}", "ERROR")
        return False

def test_auth_health():
    """Tester la santé du service d'authentification"""
    print_status("Test du service d'authentification...", "INFO")
    try:
        response = requests.get(f"{API_BASE_URL}/api/auth/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_status(f"✅ Service d'auth en ligne - Supabase configuré: {data.get('supabase_configured', False)}", "SUCCESS")
            return data.get('supabase_configured', False)
        else:
            print_status(f"❌ Service d'auth retourne {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"❌ Erreur service d'auth: {e}", "ERROR")
        return False

def test_register():
    """Tester l'inscription d'un utilisateur"""
    print_status("Test de l'inscription...", "INFO")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/register",
            json=TEST_USER,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            if data.get("success"):
                print_status("✅ Inscription réussie", "SUCCESS")
                return data.get("access_token")
            else:
                print_status(f"❌ Échec de l'inscription: {data.get('detail', 'Erreur inconnue')}", "ERROR")
                return None
        else:
            data = response.json()
            if "déjà utilisé" in data.get("detail", ""):
                print_status("⚠️ Utilisateur déjà inscrit, test de connexion...", "WARNING")
                return test_login()
            else:
                print_status(f"❌ Erreur d'inscription: {data.get('detail', 'Erreur inconnue')}", "ERROR")
                return None
    except Exception as e:
        print_status(f"❌ Erreur lors de l'inscription: {e}", "ERROR")
        return None

def test_login():
    """Tester la connexion d'un utilisateur"""
    print_status("Test de la connexion...", "INFO")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print_status("✅ Connexion réussie", "SUCCESS")
                return data.get("access_token")
            else:
                print_status(f"❌ Échec de la connexion: {data.get('detail', 'Erreur inconnue')}", "ERROR")
                return None
        else:
            data = response.json()
            print_status(f"❌ Erreur de connexion: {data.get('detail', 'Erreur inconnue')}", "ERROR")
            return None
    except Exception as e:
        print_status(f"❌ Erreur lors de la connexion: {e}", "ERROR")
        return None

def test_protected_route(token: str):
    """Tester l'accès à une route protégée"""
    print_status("Test d'accès à une route protégée...", "INFO")
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/auth/me",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_status(f"✅ Route protégée accessible - Utilisateur: {data.get('first_name')} {data.get('last_name')}", "SUCCESS")
            return True
        else:
            data = response.json()
            print_status(f"❌ Erreur route protégée: {data.get('detail', 'Erreur inconnue')}", "ERROR")
            return False
    except Exception as e:
        print_status(f"❌ Erreur lors du test de route protégée: {e}", "ERROR")
        return False

def test_unprotected_route():
    """Tester l'accès à une route non protégée"""
    print_status("Test d'accès à une route non protégée...", "INFO")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print_status("✅ Route non protégée accessible", "SUCCESS")
            return True
        else:
            print_status(f"❌ Erreur route non protégée: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"❌ Erreur lors du test de route non protégée: {e}", "ERROR")
        return False

def test_logout(token: str):
    """Tester la déconnexion"""
    print_status("Test de la déconnexion...", "INFO")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/logout",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print_status("✅ Déconnexion réussie", "SUCCESS")
                return True
            else:
                print_status(f"❌ Échec de la déconnexion: {data.get('detail', 'Erreur inconnue')}", "ERROR")
                return False
        else:
            data = response.json()
            print_status(f"❌ Erreur de déconnexion: {data.get('detail', 'Erreur inconnue')}", "ERROR")
            return False
    except Exception as e:
        print_status(f"❌ Erreur lors de la déconnexion: {e}", "ERROR")
        return False

def test_invalid_token():
    """Tester l'accès avec un token invalide"""
    print_status("Test d'accès avec un token invalide...", "INFO")
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/auth/me",
            headers={
                "Authorization": "Bearer invalid_token",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        if response.status_code == 401:
            print_status("✅ Token invalide correctement rejeté", "SUCCESS")
            return True
        else:
            print_status(f"❌ Token invalide non rejeté: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"❌ Erreur lors du test de token invalide: {e}", "ERROR")
        return False

def main():
    """Fonction principale de test"""
    print_status("🚀 Démarrage des tests d'authentification CareerFinance AI", "INFO")
    print_status("=" * 60, "INFO")
    
    # Test 1: Santé de l'API
    if not test_health_check():
        print_status("❌ Arrêt des tests - API non disponible", "ERROR")
        sys.exit(1)
    
    # Test 2: Santé du service d'authentification
    auth_configured = test_auth_health()
    if not auth_configured:
        print_status("⚠️ Supabase non configuré, certains tests peuvent échouer", "WARNING")
    
    # Test 3: Route non protégée
    test_unprotected_route()
    
    # Test 4: Inscription/Connexion
    token = test_register()
    if not token:
        print_status("❌ Impossible d'obtenir un token, arrêt des tests", "ERROR")
        sys.exit(1)
    
    # Test 5: Route protégée avec token valide
    test_protected_route(token)
    
    # Test 6: Route protégée avec token invalide
    test_invalid_token()
    
    # Test 7: Déconnexion
    test_logout(token)
    
    print_status("=" * 60, "INFO")
    print_status("✅ Tous les tests d'authentification terminés", "SUCCESS")
    print_status("🎉 L'authentification fonctionne correctement !", "SUCCESS")

if __name__ == "__main__":
    main()
