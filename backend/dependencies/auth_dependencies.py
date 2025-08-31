from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import os
from services.supabase_auth_service import SupabaseAuthService

# Schéma de sécurité pour le token Bearer
security = HTTPBearer()

# Instance du service d'authentification (créée à la demande)
def get_auth_service():
    try:
        return SupabaseAuthService()
    except Exception as e:
        # En mode dev, retourner un service mock
        if os.getenv("ENV", "dev") == "dev":
            print(f"⚠️  Erreur lors de la création du service Supabase: {e}")
            print("⚠️  Utilisation d'un service mock pour le développement")
            return None
        raise e

# Instance globale (créée à la demande)
auth_service = None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dépendance pour récupérer l'utilisateur actuel à partir du token JWT.
    Cette fonction doit être utilisée sur toutes les routes protégées.
    """
    try:
        token = credentials.credentials
        
        # Récupérer le service d'authentification
        auth_service = get_auth_service()
        if auth_service is None:
            # En mode dev, simuler un utilisateur
            if os.getenv("ENV", "dev") == "dev":
                return {
                    "id": 1,
                    "email": "dev@example.com",
                    "username": "devuser",
                    "first_name": "Dev",
                    "last_name": "User",
                    "role": "user",
                    "is_active": True
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Service d'authentification non disponible"
                )
        
        user = await auth_service.get_current_user(token)
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token d'authentification invalide"
        )

async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dépendance pour vérifier que l'utilisateur actuel est actif.
    """
    if not current_user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilisateur inactif"
        )
    return current_user

async def get_current_user_with_role(required_role: str, current_user: dict = Depends(get_current_active_user)) -> dict:
    """
    Dépendance pour vérifier que l'utilisateur a un rôle spécifique.
    """
    if current_user.get("role") != required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Rôle {required_role} requis pour accéder à cette ressource"
        )
    return current_user

# Dépendances prêtes à l'emploi pour différents rôles
async def require_admin(current_user: dict = Depends(lambda: get_current_user_with_role("admin"))) -> dict:
    """Dépendance pour les routes nécessitant un rôle admin."""
    return current_user



async def require_user(current_user: dict = Depends(get_current_active_user)) -> dict:
    """Dépendance pour les routes nécessitant un utilisateur connecté."""
    return current_user

# Dépendance optionnelle pour récupérer l'utilisateur s'il est connecté
async def get_optional_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """
    Dépendance optionnelle pour récupérer l'utilisateur s'il est connecté.
    Retourne None si aucun token n'est fourni.
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user = await auth_service.get_current_user(token)
        return user
    except Exception:
        return None
