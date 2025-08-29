#!/usr/bin/env python3
"""
Script pour lancer la version simplifiée du backend CareerFinance AI
"""

import subprocess
import sys
import os

def main():
    print("🚀 Lancement du backend CareerFinance AI (version simplifiée)...")
    print("📖 Documentation: http://localhost:8000/docs")
    print("🎯 API Coaching: http://localhost:8000/api/coaching-carriere")
    print("⏹️ Appuyez sur Ctrl+C pour arrêter")
    
    try:
        # Changer vers le dossier backend
        os.chdir("backend")
        
        # Lancer uvicorn avec la version simplifiée
        subprocess.run([
            sys.executable, "-m", "uvicorn", "main_simple:app",
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()
