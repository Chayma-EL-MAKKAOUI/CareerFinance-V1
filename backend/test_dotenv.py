#!/usr/bin/env python3
"""
Test du chargement des variables d'environnement
"""

import os
from dotenv import load_dotenv

print("🔧 Test du chargement des variables d'environnement")
print("=" * 60)

# Avant le chargement
print("\n📋 Variables avant load_dotenv():")
supabase_url_before = os.getenv("SUPABASE_URL")
print(f"SUPABASE_URL: {supabase_url_before}")

# Charger le fichier .env
print("\n🔄 Chargement du fichier .env...")
load_dotenv()

# Après le chargement
print("\n📋 Variables après load_dotenv():")
supabase_url_after = os.getenv("SUPABASE_URL")
print(f"SUPABASE_URL: {supabase_url_after}")

# Vérifier toutes les variables importantes
print("\n🔍 Vérification de toutes les variables:")
important_vars = [
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "JWT_SECRET_KEY",
    "APP_SECRET_KEY"
]

for var in important_vars:
    value = os.getenv(var)
    if value:
        # Masquer partiellement la valeur
        masked_value = value[:20] + "..." if len(value) > 20 else value
        print(f"✅ {var}: {masked_value}")
    else:
        print(f"❌ {var}: Non définie")

print("\n" + "=" * 60)
