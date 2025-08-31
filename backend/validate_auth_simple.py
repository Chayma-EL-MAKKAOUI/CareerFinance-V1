#!/usr/bin/env python3
"""
Script de validation des modifications d'authentification
Ce script verifie que tous les routers ont bien ete modifies pour inclure l'authentification JWT
"""

import os
import re
from typing import List, Dict, Tuple

# Configuration
ROUTERS_DIR = "routers"
AUTH_IMPORT = "from dependencies.auth_dependencies import get_current_user"
AUTH_DEPENDENCY = "current_user: dict = Depends(get_current_user)"

def check_file_for_auth(file_path: str) -> Tuple[bool, List[str]]:
    """Verifie si un fichier contient les modifications d'authentification"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        has_auth_import = AUTH_IMPORT in content
        has_auth_dependency = AUTH_DEPENDENCY in content
        
        if not has_auth_import:
            issues.append("Import d'authentification manquant")
        
        if not has_auth_dependency:
            issues.append("Dependance d'authentification manquante")
        
        # Verifier les endpoints POST et GET
        post_endpoints = re.findall(r'@router\.post\([^)]+\)\s*\n\s*async def ([^(]+)', content)
        get_endpoints = re.findall(r'@router\.get\([^)]+\)\s*\n\s*async def ([^(]+)', content)
        
        protected_endpoints = []
        for endpoint in post_endpoints + get_endpoints:
            endpoint_name = endpoint.strip()
            if endpoint_name and not endpoint_name.startswith('_'):
                # Verifier si cet endpoint a la dependance d'authentification
                endpoint_pattern = rf'async def {re.escape(endpoint_name)}\s*\([^)]*{re.escape(AUTH_DEPENDENCY)}'
                if not re.search(endpoint_pattern, content):
                    protected_endpoints.append(endpoint_name)
        
        if protected_endpoints:
            issues.append(f"Endpoints sans authentification: {', '.join(protected_endpoints)}")
        
        return has_auth_import and has_auth_dependency and not protected_endpoints, issues
        
    except Exception as e:
        return False, [f"Erreur de lecture: {str(e)}"]

def main():
    """Fonction principale de validation"""
    print("Validation des modifications d'authentification JWT")
    print("=" * 60)
    
    # Lister tous les fichiers routers
    router_files = []
    for file in os.listdir(ROUTERS_DIR):
        if file.endswith('.py') and file != '__init__.py':
            router_files.append(os.path.join(ROUTERS_DIR, file))
    
    print(f"Fichiers routers trouves: {len(router_files)}")
    print()
    
    results = {}
    total_issues = 0
    
    for file_path in router_files:
        file_name = os.path.basename(file_path)
        print(f"Verification de {file_name}...")
        
        is_valid, issues = check_file_for_auth(file_path)
        results[file_name] = (is_valid, issues)
        
        if is_valid:
            print(f"  OK {file_name} - Authentification configuree correctement")
        else:
            print(f"  ERREUR {file_name} - Problemes detectes:")
            for issue in issues:
                print(f"    {issue}")
            total_issues += len(issues)
        
        print()
    
    # Resume
    print("=" * 60)
    print("RESUME DE LA VALIDATION")
    print("=" * 60)
    
    valid_files = sum(1 for is_valid, _ in results.values() if is_valid)
    total_files = len(results)
    
    print(f"Fichiers correctement configures: {valid_files}/{total_files}")
    print(f"Problemes detectes: {total_issues}")
    
    if valid_files == total_files:
        print("\nTous les routers sont correctement configures pour l'authentification JWT !")
        print("\nModifications appliquees:")
        print("   • Import de get_current_user ajoute")
        print("   • Dependance d'authentification ajoutee aux endpoints")
        print("   • Tous les endpoints metier sont maintenant proteges")
        return 0
    else:
        print("\nCertains fichiers necessitent des corrections.")
        print("\nActions a effectuer:")
        for file_name, (is_valid, issues) in results.items():
            if not is_valid:
                print(f"   • {file_name}: {', '.join(issues)}")
        return 1

if __name__ == "__main__":
    exit(main())
