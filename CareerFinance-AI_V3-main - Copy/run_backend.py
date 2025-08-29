#!/usr/bin/env python3
"""
Script simple pour lancer le backend
"""

import subprocess
import sys
import os

def main():
    print("🚀 Lancement du backend CareerFinance AI...")
    print("📖 Documentation: http://localhost:8000/docs")
    print("🎯 Coaching carrière: http://localhost:8000/api/supabase-career/")
    print("⏹️ Appuyez sur Ctrl+C pour arrêter")
    
    try:
        # Changer vers le dossier backend
        os.chdir("backend")
        
        # Lancer uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()
