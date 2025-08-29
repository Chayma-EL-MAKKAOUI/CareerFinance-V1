# test_supabase_career_coaching.py
"""
Script de test pour vérifier le fonctionnement du système de coaching carrière avec Supabase
"""

import os
import json
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration
API_BASE_URL = "http://localhost:8000"
SUPABASE_CAREER_BASE = f"{API_BASE_URL}/api/supabase-career"

def test_status():
    """Test du statut du système"""
    print("🔍 Test du statut du système...")
    
    try:
        response = requests.get(f"{SUPABASE_CAREER_BASE}/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Statut: {data['message']}")
            print(f"   - Initialisé: {data['isInitialized']}")
            print(f"   - Profils: {data['profilesCount']}")
            print(f"   - Chunks: {data['chunksCount']}")
            print(f"   - Index: {data['indexExists']}")
            return data
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def test_initialize():
    """Test de l'initialisation du système"""
    print("\n🔄 Test de l'initialisation...")
    
    try:
        response = requests.post(f"{SUPABASE_CAREER_BASE}/initialize")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Initialisation: {data['message']}")
            print(f"   - Profils chargés: {data['profilesLoaded']}")
            print(f"   - Chunks chargés: {data['chunksLoaded']}")
            print(f"   - Statut: {data['status']}")
            return True
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_coaching():
    """Test de génération de plan de carrière"""
    print("\n🎯 Test de génération de plan de carrière...")
    
    coaching_data = {
        "user_id": 1,
        "goal": "Devenir Data Science Manager",
        "skills": ["Python", "Machine Learning", "Leadership", "SQL"],
        "sector": "Technologie",
        "useLinkedInData": True
    }
    
    try:
        response = requests.post(f"{SUPABASE_CAREER_BASE}/coaching", json=coaching_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ Plan de carrière généré avec succès!")
            print(f"   - Objectif: {data['objectif']}")
            print(f"   - Compétences: {data['competences']}")
            print(f"   - Secteur: {data['secteur']}")
            print(f"   - LinkedIn utilisé: {data['linkedInDataUsed']}")
            print(f"   - Session ID: {data.get('session_id', 'N/A')}")
            
            if 'linkedInInsights' in data:
                insights = data['linkedInInsights']
                print(f"   - Profils analysés: {insights.get('profiles_analyzed', 0)}")
                print(f"   - Chunks pertinents: {len(insights.get('relevant_chunks', []))}")
            
            return data
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def test_search_profiles():
    """Test de recherche de profils"""
    print("\n🔍 Test de recherche de profils...")
    
    search_data = {
        "query": "Data Scientist Python Machine Learning",
        "topK": 5
    }
    
    try:
        response = requests.post(f"{SUPABASE_CAREER_BASE}/search-profiles", json=search_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Recherche réussie: {data['resultsCount']} profils trouvés")
            
            for i, profile in enumerate(data['profiles'][:3], 1):
                print(f"   {i}. {profile['nom']} - {profile['titre']} (score: {profile['score']:.3f})")
            
            return data
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def test_analyze_skills():
    """Test d'analyse des compétences"""
    print("\n📊 Test d'analyse des compétences...")
    
    analysis_data = {
        "skills": ["Python", "Machine Learning", "Deep Learning"],
        "sector": "Intelligence Artificielle"
    }
    
    try:
        response = requests.post(f"{SUPABASE_CAREER_BASE}/analyze-skills", json=analysis_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ Analyse des compétences réussie!")
            print(f"   - Compétences: {data['skills']}")
            print(f"   - Secteur: {data['sector']}")
            print(f"   - Profils analysés: {data['profiles_analyzed']}")
            
            market_demand = data.get('market_demand', {})
            print(f"   - Demande: {market_demand.get('demand_level', 'N/A')}")
            print(f"   - Score moyen: {market_demand.get('avg_score', 0):.3f}")
            
            return data
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def test_sector_insights():
    """Test d'insights sectoriels"""
    print("\n💡 Test d'insights sectoriels...")
    
    try:
        response = requests.get(f"{SUPABASE_CAREER_BASE}/insights/Technologie?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Insights pour le secteur 'Technologie':")
            print(f"   - Profils analysés: {data['profilesAnalyzed']}")
            print(f"   - Top profils: {len(data.get('topProfiles', []))}")
            print(f"   - Contenu pertinent: {len(data.get('relevantContent', []))}")
            
            return data
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def test_coaching_history():
    """Test de récupération de l'historique"""
    print("\n📚 Test de récupération de l'historique...")
    
    try:
        response = requests.get(f"{SUPABASE_CAREER_BASE}/history/1")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Historique récupéré pour l'utilisateur 1:")
            print(f"   - Sessions: {data['sessions_count']}")
            
            for session in data['sessions'][:2]:
                print(f"   - {session['objectif']} ({session['created_at'][:10]})")
            
            return data
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def test_documentation():
    """Test de la documentation"""
    print("\n📖 Test de la documentation...")
    
    try:
        response = requests.get(f"{SUPABASE_CAREER_BASE}/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Documentation accessible!")
            print(f"   - Titre: {data['title']}")
            print(f"   - Version: {data['version']}")
            print(f"   - Endpoints: {len(data['endpoints'])}")
            return data
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def main():
    """Fonction principale de test"""
    print("🧪 Tests du système de coaching carrière avec Supabase")
    print("=" * 60)
    
    # Vérifier que le serveur est accessible
    try:
        health_response = requests.get(f"{API_BASE_URL}/api/health")
        if health_response.status_code != 200:
            print(f"❌ Serveur non accessible: {health_response.status_code}")
            return
        print("✅ Serveur accessible")
    except Exception as e:
        print(f"❌ Impossible de se connecter au serveur: {e}")
        print("   Assurez-vous que le serveur FastAPI est démarré sur http://localhost:8000")
        return
    
    # Tests
    tests = [
        ("Documentation", test_documentation),
        ("Statut", test_status),
        ("Initialisation", test_initialize),
        ("Coaching", test_coaching),
        ("Recherche de profils", test_search_profiles),
        ("Analyse des compétences", test_analyze_skills),
        ("Insights sectoriels", test_sector_insights),
        ("Historique", test_coaching_history),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = "✅ Succès" if result is not None else "❌ Échec"
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            results[test_name] = "❌ Erreur"
    
    # Résumé
    print(f"\n{'='*60}")
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    for test_name, result in results.items():
        print(f"{test_name:25} {result}")
    
    success_count = sum(1 for result in results.values() if "✅" in result)
    total_count = len(results)
    
    print(f"\n🎯 Résultat: {success_count}/{total_count} tests réussis")
    
    if success_count == total_count:
        print("🎉 Tous les tests sont passés! Le système fonctionne correctement.")
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez la configuration et les données.")

if __name__ == "__main__":
    main()
