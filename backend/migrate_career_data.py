# migrate_career_data.py
"""
Script de migration pour peupler les tables Supabase avec des données de test
pour le coaching carrière (profileslinkedin, profile_chunks, coaching_sessions)
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ SUPABASE_URL et SUPABASE_KEY doivent être définis dans .env")

# Initialiser le client Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_sample_profiles() -> List[Dict]:
    """Crée des profils LinkedIn de test"""
    profiles = [
        {
            "nom": "Marie Dubois",
            "titre": "Data Scientist Senior",
            "formation": "Master en Intelligence Artificielle - École Centrale Paris",
            "url": "https://linkedin.com/in/marie-dubois"
        },
        {
            "nom": "Thomas Martin",
            "titre": "Lead Developer Full Stack",
            "formation": "Ingénieur Informatique - INSA Lyon",
            "url": "https://linkedin.com/in/thomas-martin"
        },
        {
            "nom": "Sophie Bernard",
            "titre": "Product Manager",
            "formation": "MBA - HEC Paris",
            "url": "https://linkedin.com/in/sophie-bernard"
        },
        {
            "nom": "Pierre Moreau",
            "titre": "DevOps Engineer",
            "formation": "Master en Systèmes d'Information - Télécom Paris",
            "url": "https://linkedin.com/in/pierre-moreau"
        },
        {
            "nom": "Julie Leroy",
            "titre": "UX/UI Designer Senior",
            "formation": "École des Arts Décoratifs de Paris",
            "url": "https://linkedin.com/in/julie-leroy"
        },
        {
            "nom": "Alexandre Petit",
            "titre": "Business Analyst",
            "formation": "Master en Finance - ESSEC",
            "url": "https://linkedin.com/in/alexandre-petit"
        },
        {
            "nom": "Camille Rousseau",
            "titre": "Marketing Digital Manager",
            "formation": "Master en Marketing - Sciences Po Paris",
            "url": "https://linkedin.com/in/camille-rousseau"
        },
        {
            "nom": "Lucas Durand",
            "titre": "Cybersecurity Specialist",
            "formation": "Master en Sécurité Informatique - ENSTA Paris",
            "url": "https://linkedin.com/in/lucas-durand"
        },
        {
            "nom": "Emma Girard",
            "titre": "Data Engineer",
            "formation": "Ingénieur Statistique - ENSAE Paris",
            "url": "https://linkedin.com/in/emma-girard"
        },
        {
            "nom": "Nicolas Blanc",
            "titre": "Sales Director",
            "formation": "Master en Commerce International - ESCP Europe",
            "url": "https://linkedin.com/in/nicolas-blanc"
        }
    ]
    return profiles

def create_sample_chunks(profile_id: int, profile_data: Dict) -> List[Dict]:
    """Crée des chunks de contenu pour un profil"""
    nom = profile_data["nom"]
    titre = profile_data["titre"]
    formation = profile_data["formation"]
    
    chunks = [
        {
            "profile_id": profile_id,
            "chunk_idx": 0,
            "section": "profil",
            "content": f"{nom} est {titre} avec une formation en {formation}. Spécialisé dans les technologies modernes et l'innovation.",
            "token_count": 25
        },
        {
            "profile_id": profile_id,
            "chunk_idx": 1,
            "section": "competences",
            "content": f"Compétences principales de {nom}: Python, Machine Learning, Data Analysis, SQL, Cloud Computing, Agile Methodologies.",
            "token_count": 20
        },
        {
            "profile_id": profile_id,
            "chunk_idx": 2,
            "section": "experience",
            "content": f"{nom} a plus de 5 ans d'expérience dans le secteur technologique. A travaillé sur des projets innovants et des équipes internationales.",
            "token_count": 30
        },
        {
            "profile_id": profile_id,
            "chunk_idx": 3,
            "section": "objectifs",
            "content": f"{nom} cherche à évoluer vers des postes de leadership et à contribuer à des projets d'impact dans le domaine de l'IA et de la data.",
            "token_count": 35
        }
    ]
    return chunks

def create_sample_coaching_sessions() -> List[Dict]:
    """Crée des sessions de coaching de test"""
    sessions = [
        {
            "user_id": 1,
            "objectif": "Évoluer vers un poste de Data Science Manager",
            "competences": json.dumps(["Python", "Machine Learning", "Leadership", "Gestion d'équipe"]),
            "secteur": "Technologie",
            "created_at": (datetime.now() - timedelta(days=5)).isoformat()
        },
        {
            "user_id": 1,
            "objectif": "Améliorer mes compétences en Deep Learning",
            "competences": json.dumps(["Python", "TensorFlow", "PyTorch", "Computer Vision"]),
            "secteur": "Intelligence Artificielle",
            "created_at": (datetime.now() - timedelta(days=10)).isoformat()
        },
        {
            "user_id": 2,
            "object_id": "Devenir Lead Developer",
            "competences": json.dumps(["JavaScript", "React", "Node.js", "Architecture"]),
            "secteur": "Développement Web",
            "created_at": (datetime.now() - timedelta(days=3)).isoformat()
        },
        {
            "user_id": 3,
            "objectif": "Transition vers le Product Management",
            "competences": json.dumps(["Stratégie produit", "User Research", "Agile", "Analytics"]),
            "secteur": "Product Management",
            "created_at": (datetime.now() - timedelta(days=7)).isoformat()
        }
    ]
    return sessions

def migrate_profiles():
    """Migre les profils LinkedIn"""
    print("🔄 Migration des profils LinkedIn...")
    
    try:
        # Vérifier si des profils existent déjà
        existing = supabase.table("profileslinkedin").select("id").execute()
        if existing.data:
            print(f"⚠️ {len(existing.data)} profils existent déjà. Suppression...")
            supabase.table("profileslinkedin").delete().neq("id", 0).execute()
        
        # Créer les profils de test
        profiles = create_sample_profiles()
        
        # Insérer les profils
        response = supabase.table("profileslinkedin").insert(profiles).execute()
        print(f"✅ {len(response.data)} profils LinkedIn créés")
        
        return response.data
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration des profils: {e}")
        return []

def migrate_chunks(profiles_data: List[Dict]):
    """Migre les chunks de profils"""
    print("🔄 Migration des chunks de profils...")
    
    try:
        # Vérifier si des chunks existent déjà
        existing = supabase.table("profile_chunks").select("id").execute()
        if existing.data:
            print(f"⚠️ {len(existing.data)} chunks existent déjà. Suppression...")
            supabase.table("profile_chunks").delete().neq("id", 0).execute()
        
        # Créer les chunks pour chaque profil
        all_chunks = []
        for profile in profiles_data:
            chunks = create_sample_chunks(profile["id"], profile)
            all_chunks.extend(chunks)
        
        # Insérer les chunks
        response = supabase.table("profile_chunks").insert(all_chunks).execute()
        print(f"✅ {len(response.data)} chunks de profils créés")
        
        return response.data
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration des chunks: {e}")
        return []

def migrate_coaching_sessions():
    """Migre les sessions de coaching"""
    print("🔄 Migration des sessions de coaching...")
    
    try:
        # Vérifier si des sessions existent déjà
        existing = supabase.table("coaching_sessions").select("id").execute()
        if existing.data:
            print(f"⚠️ {len(existing.data)} sessions existent déjà. Suppression...")
            supabase.table("coaching_sessions").delete().neq("id", 0).execute()
        
        # Créer les sessions de test
        sessions = create_sample_coaching_sessions()
        
        # Insérer les sessions
        response = supabase.table("coaching_sessions").insert(sessions).execute()
        print(f"✅ {len(response.data)} sessions de coaching créées")
        
        return response.data
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration des sessions: {e}")
        return []

def verify_migration():
    """Vérifie que la migration s'est bien passée"""
    print("\n🔍 Vérification de la migration...")
    
    try:
        # Compter les profils
        profiles = supabase.table("profileslinkedin").select("id").execute()
        print(f"📊 Profils LinkedIn: {len(profiles.data)}")
        
        # Compter les chunks
        chunks = supabase.table("profile_chunks").select("id").execute()
        print(f"📊 Chunks de profils: {len(chunks.data)}")
        
        # Compter les sessions
        sessions = supabase.table("coaching_sessions").select("id").execute()
        print(f"📊 Sessions de coaching: {len(sessions.data)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

def main():
    """Fonction principale de migration"""
    print("🚀 Début de la migration des données de coaching carrière...")
    
    # 1. Migrer les profils
    profiles_data = migrate_profiles()
    if not profiles_data:
        print("❌ Échec de la migration des profils")
        return
    
    # 2. Migrer les chunks
    chunks_data = migrate_chunks(profiles_data)
    if not chunks_data:
        print("❌ Échec de la migration des chunks")
        return
    
    # 3. Migrer les sessions
    sessions_data = migrate_coaching_sessions()
    if not sessions_data:
        print("❌ Échec de la migration des sessions")
        return
    
    # 4. Vérifier la migration
    if verify_migration():
        print("\n✅ Migration terminée avec succès!")
        print("\n📋 Résumé:")
        print(f"   - {len(profiles_data)} profils LinkedIn")
        print(f"   - {len(chunks_data)} chunks de profils")
        print(f"   - {len(sessions_data)} sessions de coaching")
        print("\n🎯 Vous pouvez maintenant utiliser le système de coaching carrière avec Supabase!")
    else:
        print("\n❌ Erreur lors de la vérification de la migration")

if __name__ == "__main__":
    main()
