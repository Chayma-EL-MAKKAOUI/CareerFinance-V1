#!/usr/bin/env python3
"""
Script pour vérifier la configuration des variables d'environnement
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

def check_env_file():
    """Vérifier le fichier .env"""
    env_file = Path(".env")
    
    print("🔍 Vérification du fichier .env...")
    
    if not env_file.exists():
        print("❌ Fichier .env non trouvé")
        return False
    
    print("✅ Fichier .env trouvé")
    
    # Lire le contenu du fichier
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\n📄 Contenu du fichier .env ({len(content)} caractères):")
        print("-" * 50)
        print(content)
        print("-" * 50)
        
        # Vérifier les variables essentielles
        required_vars = [
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY", 
            "SUPABASE_SERVICE_ROLE_KEY",
            "JWT_SECRET_KEY",
            "APP_SECRET_KEY"
        ]
        
        print("\n🔍 Vérification des variables requises:")
        missing_vars = []
        
        for var in required_vars:
            if var in content:
                # Extraire la valeur
                lines = content.split('\n')
                for line in lines:
                    if line.startswith(f"{var}="):
                        value = line.split('=', 1)[1].strip()
                        if value and value != f"your_{var.lower()}_here":
                            print(f"✅ {var}: Configuré")
                        else:
                            print(f"⚠️  {var}: Valeur par défaut détectée")
                            missing_vars.append(var)
                        break
                else:
                    print(f"❌ {var}: Non trouvé")
                    missing_vars.append(var)
            else:
                print(f"❌ {var}: Non trouvé")
                missing_vars.append(var)
        
        if missing_vars:
            print(f"\n⚠️  Variables manquantes ou non configurées: {', '.join(missing_vars)}")
            print("\n📝 Pour corriger, mettez à jour votre fichier .env avec vos vraies clés Supabase:")
            print("""
# Exemple de configuration valide:
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
JWT_SECRET_KEY=your-super-secret-jwt-key-here
APP_SECRET_KEY=your-app-secret-key-here
            """)
            return False
        else:
            print("\n✅ Toutes les variables requises sont configurées!")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier .env: {e}")
        return False

def check_env_variables():
    """Vérifier les variables d'environnement chargées"""
    print("\n🔍 Vérification des variables d'environnement chargées:")
    
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY", 
        "SUPABASE_SERVICE_ROLE_KEY",
        "JWT_SECRET_KEY",
        "APP_SECRET_KEY"
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Masquer partiellement la valeur pour la sécurité
            masked_value = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var}: {masked_value}")
        else:
            print(f"❌ {var}: Non définie")

if __name__ == "__main__":
    print("🔧 Vérification de la configuration d'environnement")
    print("=" * 60)
    
    env_ok = check_env_file()
    check_env_variables()
    
    if env_ok:
        print("\n✅ Configuration OK - Vous pouvez démarrer l'application")
    else:
        print("\n❌ Configuration incomplète - Veuillez corriger le fichier .env")
