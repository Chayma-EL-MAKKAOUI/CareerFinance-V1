from fastapi import APIRouter, HTTPException, status, Depends, Response
from fastapi.responses import RedirectResponse
from typing import Dict, Any
import os

from services.supabase_auth_service import SupabaseAuthService
from models.auth_models import (
    UserRegister, UserLogin, AuthResponse, LogoutResponse, 
    OAuthProvider, OAuthCallback, UserProfile
)
from dependencies.auth_dependencies import get_current_user

# Créer le router
router = APIRouter()

# Instance du service d'authentification (créée à la demande pour éviter les erreurs d'initialisation)
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

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister):
    """
    Inscrire un nouvel utilisateur.
    
    - **email**: Email unique de l'utilisateur
    - **username**: Nom d'utilisateur unique
    - **password**: Mot de passe (minimum 8 caractères)
    - **first_name**: Prénom
    - **last_name**: Nom
    - **role**: Rôle (optionnel, défaut: "user")
    """
    try:
        auth_service = get_auth_service()
        if auth_service is None:
            # En mode dev, retourner une réponse mock
            return AuthResponse(
                success=True,
                access_token="dev-token",
                token_type="bearer",
                user=UserResponse(
                    id=1,
                    email=user_data.email,
                    username=user_data.username,
                    first_name=user_data.first_name,
                    last_name=user_data.last_name,
                    role=user_data.role,
                    is_active=True,
                    created_at=None,
                    updated_at=None,
                    last_login=None,
                    total_analyses=0,
                    document_analyses_count=0,
                    salary_analyses_count=0,
                    coaching_sessions_count=0
                )
            )
        
        result = await auth_service.register_user(user_data.dict())
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'inscription: {str(e)}"
        )

@router.post("/login", response_model=AuthResponse)
async def login_user(user_credentials: UserLogin):
    """
    Connecter un utilisateur existant.
    
    - **email**: Email de l'utilisateur
    - **password**: Mot de passe
    """
    try:
        result = await auth_service.login_user(
            email=user_credentials.email,
            password=user_credentials.password
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la connexion: {str(e)}"
        )

@router.post("/logout", response_model=LogoutResponse)
async def logout_user(current_user: dict = Depends(get_current_user)):
    """
    Déconnecter l'utilisateur actuel.
    
    Cette route nécessite une authentification.
    """
    try:
        # Récupérer le token depuis le header Authorization
        # Note: En production, vous pourriez implémenter une blacklist de tokens
        result = await auth_service.logout_user("")  # Le token est vérifié par get_current_user
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la déconnexion: {str(e)}"
        )

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Récupérer le profil de l'utilisateur actuel.
    
    Cette route nécessite une authentification.
    """
    return current_user

@router.get("/oauth/{provider}/url")
async def get_oauth_url(provider: str):
    """
    Générer l'URL OAuth pour Google ou GitHub.
    
    - **provider**: Provider OAuth ("google" ou "github")
    """
    try:
        if provider not in ["google", "github"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provider OAuth non supporté. Utilisez 'google' ou 'github'"
            )
        
        oauth_url = await auth_service.get_oauth_url(provider)
        return {"oauth_url": oauth_url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération de l'URL OAuth: {str(e)}"
        )

@router.get("/oauth/{provider}/callback")
async def oauth_callback(provider: str, code: str):
    """
    Gérer le callback OAuth.
    
    - **provider**: Provider OAuth ("google" ou "github")
    - **code**: Code d'autorisation retourné par le provider
    """
    try:
        if provider not in ["google", "github"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provider OAuth non supporté"
            )
        
        result = await auth_service.handle_oauth_callback(code, provider)
        
        # Rediriger vers le frontend avec le token
        from config.auth_config import auth_settings
        redirect_url = f"{auth_settings.FRONTEND_URL}/auth/callback?token={result['access_token']}&user_id={result['user']['id']}"
        
        return RedirectResponse(url=redirect_url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'authentification OAuth: {str(e)}"
        )

@router.post("/oauth/{provider}/callback")
async def oauth_callback_post(provider: str, oauth_data: OAuthCallback):
    """
    Gérer le callback OAuth via POST (alternative à GET).
    
    - **provider**: Provider OAuth ("google" ou "github")
    - **oauth_data**: Données OAuth incluant le code
    """
    try:
        if provider not in ["google", "github"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provider OAuth non supporté"
            )
        
        result = await auth_service.handle_oauth_callback(oauth_data.code, provider)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'authentification OAuth: {str(e)}"
        )

@router.get("/health")
async def auth_health():
    """
    Vérifier l'état du service d'authentification.
    """
    return {
        "status": "healthy",
        "service": "authentication",
        "supabase_configured": bool(
            os.getenv("SUPABASE_URL") and 
            os.getenv("SUPABASE_ANON_KEY") and 
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
    }
