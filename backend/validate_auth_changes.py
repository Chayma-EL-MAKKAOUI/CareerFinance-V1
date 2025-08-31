#!/usr/bin/env python3
"""
Script de validation des modifications d'authentification
Ce script vérifie que tous les routers ont bien été modifiés pour inclure l'authentification JWT
"""

import os
import re
from typing import List, Dict, Tuple

# Configuration
ROUTERS_DIR = "routers"
AUTH_IMPORT = "from dependencies.auth_dependencies import get_current_user"
AUTH_DEPENDENCY = "current_user: dict = Depends(get_current_user)"

def check_file_for_auth(file_path: str) -> Tuple[bool, List[str]]:
    """Vérifie si un fichier contient les modifications d'authentification"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        has_auth_import = AUTH_IMPORT in content
        has_auth_dependency = AUTH_DEPENDENCY in content
        
        if not has_auth_import:
            issues.append("❌ Import d'authentification manquant")
        
        if not has_auth_dependency:
            issues.append("❌ Dépendance d'authentification manquante")
        
        # Vérifier les endpoints POST et GET
        post_endpoints = re.findall(r'@router\.post\([^)]+\)\s*\n\s*async def ([^(]+)', content)
        get_endpoints = re.findall(r'@router\.get\([^)]+\)\s*\n\s*async def ([^(]+)', content)
        
        protected_endpoints = []
        for endpoint in post_endpoints + get_endpoints:
            endpoint_name = endpoint.strip()
            if endpoint_name and not endpoint_name.startswith('_'):
                # Vérifier si cet endpoint a la dépendance d'authentification
                endpoint_pattern = rf'async def {re.escape(endpoint_name)}\s*\([^)]*{re.escape(AUTH_DEPENDENCY)}'
                if not re.search(endpoint_pattern, content):
                    protected_endpoints.append(endpoint_name)
        
        if protected_endpoints:
            issues.append(f"⚠️  Endpoints sans authentification: {', '.join(protected_endpoints)}")
        
        return has_auth_import and has_auth_dependency and not protected_endpoints, issues
        
    except Exception as e:
        return False, [f"❌ Erreur de lecture: {str(e)}"]

def main():
    """Fonction principale de validation"""
    print("🔐 Validation des modifications d'authentification JWT")
    print("=" * 60)
    
    # Lister tous les fichiers routers
    router_files = []
    for file in os.listdir(ROUTERS_DIR):
        if file.endswith('.py') and file != '__init__.py':
            router_files.append(os.path.join(ROUTERS_DIR, file))
    
    print(f"📁 Fichiers routers trouvés: {len(router_files)}")
    print()
    
    results = {}
    total_issues = 0
    
    for file_path in router_files:
        file_name = os.path.basename(file_path)
        print(f"🔍 Vérification de {file_name}...")
        
        is_valid, issues = check_file_for_auth(file_path)
        results[file_name] = (is_valid, issues)
        
        if is_valid:
            print(f"  ✅ {file_name} - Authentification configurée correctement")
        else:
            print(f"  ❌ {file_name} - Problèmes détectés:")
            for issue in issues:
                print(f"    {issue}")
            total_issues += len(issues)
        
        print()
    
    # Résumé
    print("=" * 60)
    print("📊 RÉSUMÉ DE LA VALIDATION")
    print("=" * 60)
    
    valid_files = sum(1 for is_valid, _ in results.values() if is_valid)
    total_files = len(results)
    
    print(f"✅ Fichiers correctement configurés: {valid_files}/{total_files}")
    print(f"❌ Problèmes détectés: {total_issues}")
    
    if valid_files == total_files:
        print("\n🎉 Tous les routers sont correctement configurés pour l'authentification JWT !")
        print("\n📋 Modifications appliquées:")
        print("   • Import de get_current_user ajouté")
        print("   • Dépendance d'authentification ajoutée aux endpoints")
        print("   • Tous les endpoints métier sont maintenant protégés")
        return 0
    else:
        print("\n⚠️  Certains fichiers nécessitent des corrections.")
        print("\n📝 Actions à effectuer:")
        for file_name, (is_valid, issues) in results.items():
            if not is_valid:
                print(f"   • {file_name}: {', '.join(issues)}")
        return 1

if __name__ == "__main__":
    exit(main())
