from typing import Optional, Dict, Any
import os
from datetime import datetime, timedelta
import jwt
from supabase import create_client, Client
from fastapi import HTTPException, status
import bcrypt
from config.auth_config import auth_settings

class SupabaseAuthService:
    def __init__(self):
        self.supabase_url = auth_settings.SUPABASE_URL
        self.supabase_anon_key = auth_settings.SUPABASE_ANON_KEY
        self.supabase_service_key = auth_settings.SUPABASE_SERVICE_ROLE_KEY
        self.jwt_secret = auth_settings.JWT_SECRET_KEY
        self.jwt_algorithm = auth_settings.JWT_ALGORITHM
        self.access_token_expire_minutes = auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES
        
        # Vérifier si on est en mode développement avec des clés par défaut
        if (self.supabase_anon_key == "dev-anon-key" or 
            self.supabase_service_key == "dev-service-key" or
            self.supabase_url == "https://dev-project.supabase.co"):
            raise ValueError("Configuration Supabase manquante. Veuillez configurer vos vraies clés Supabase dans le fichier .env")
        
        if not all([self.supabase_url, self.supabase_anon_key, self.supabase_service_key]):
            raise ValueError("Configuration Supabase manquante dans les variables d'environnement")
        
        try:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_anon_key)
            self.supabase_admin: Client = create_client(self.supabase_url, self.supabase_service_key)
        except Exception as e:
            raise ValueError(f"Erreur lors de la connexion à Supabase: {str(e)}")
    
    def _create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Créer un JWT token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.jwt_secret, algorithm=self.jwt_algorithm)
        return encoded_jwt
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Vérifier un mot de passe avec bcrypt"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def _hash_password(self, password: str) -> str:
        """Hasher un mot de passe avec bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    async def register_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Inscrire un nouvel utilisateur"""
        try:
            # Vérifier si l'utilisateur existe déjà
            existing_user = self.supabase.table("users").select("id").eq("email", user_data["email"]).execute()
            if existing_user.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email déjà utilisé"
                )
            
            existing_username = self.supabase.table("users").select("id").eq("username", user_data["username"]).execute()
            if existing_username.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Nom d'utilisateur déjà utilisé"
                )
            
            # Créer l'utilisateur dans Supabase Auth
            auth_response = self.supabase.auth.sign_up({
                "email": user_data["email"],
                "password": user_data["password"]
            })
            
            if auth_response.user is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Erreur lors de la création du compte Supabase"
                )
            
            # Insérer dans la table users
            user_record = {
                "email": user_data["email"],
                "username": user_data["username"],
                "password": self._hash_password(user_data["password"]),
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
                "role": user_data.get("role", "user"),
                "auth_id": auth_response.user.id,
                "is_active": True
            }
            
            db_response = self.supabase.table("users").insert(user_record).execute()
            
            if not db_response.data:
                # Supprimer le compte Auth si l'insertion échoue
                self.supabase_admin.auth.admin.delete_user(auth_response.user.id)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Erreur lors de la création de l'utilisateur"
                )
            
            # Créer le token JWT
            access_token = self._create_access_token(
                data={"sub": str(db_response.data[0]["id"]), "email": user_data["email"]}
            )
            
            return {
                "success": True,
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": db_response.data[0]["id"],
                    "email": user_data["email"],
                    "username": user_data["username"],
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                    "role": user_data.get("role", "user")
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur interne: {str(e)}"
            )
    
    async def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Connecter un utilisateur"""
        try:
            # Vérifier les credentials dans la table users
            user_response = self.supabase.table("users").select("*").eq("email", email).eq("is_active", True).execute()
            
            if not user_response.data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email ou mot de passe incorrect"
                )
            
            user = user_response.data[0]
            
            # Vérifier le mot de passe
            if not self._verify_password(password, user["password"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email ou mot de passe incorrect"
                )
            
            # Mettre à jour last_login
            self.supabase.table("users").update({"last_login": datetime.utcnow().isoformat()}).eq("id", user["id"]).execute()
            
            # Créer le token JWT
            access_token = self._create_access_token(
                data={"sub": str(user["id"]), "email": user["email"]}
            )
            
            return {
                "success": True,
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "username": user["username"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "role": user["role"],
                    "is_active": user["is_active"]
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur interne: {str(e)}"
            )
    
    async def get_current_user(self, token: str) -> Dict[str, Any]:
        """Récupérer l'utilisateur actuel à partir du token JWT"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token invalide"
                )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expiré"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide"
            )
        
        # Récupérer l'utilisateur depuis la base
        user_response = self.supabase.table("users").select("*").eq("id", user_id).eq("is_active", True).execute()
        
        if not user_response.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non trouvé ou inactif"
            )
        
        return user_response.data[0]
    
    async def logout_user(self, token: str) -> Dict[str, Any]:
        """Déconnecter un utilisateur"""
        try:
            # Récupérer l'utilisateur pour vérifier le token
            user = await self.get_current_user(token)
            
            # Invalider le token côté client (le JWT reste valide jusqu'à expiration)
            # En production, vous pourriez implémenter une blacklist de tokens
            
            return {
                "success": True,
                "message": "Déconnexion réussie"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur interne: {str(e)}"
            )
    
    async def get_oauth_url(self, provider: str) -> str:
        """Générer l'URL OAuth pour Google ou GitHub"""
        try:
            if provider == "google":
                if not auth_settings.is_google_oauth_configured:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Google OAuth non configuré"
                    )
                return self.supabase.auth.sign_in_with_oauth({
                    "provider": "google",
                    "options": {
                        "redirect_to": f"{auth_settings.FRONTEND_URL}/auth/callback"
                    }
                }).url
            elif provider == "github":
                if not auth_settings.is_github_oauth_configured:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="GitHub OAuth non configuré"
                    )
                return self.supabase.auth.sign_in_with_oauth({
                    "provider": "github",
                    "options": {
                        "redirect_to": f"{auth_settings.FRONTEND_URL}/auth/callback"
                    }
                }).url
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Provider OAuth non supporté"
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la génération de l'URL OAuth: {str(e)}"
            )
    
    async def handle_oauth_callback(self, code: str, provider: str) -> Dict[str, Any]:
        """Gérer le callback OAuth"""
        try:
            # Échanger le code contre un token
            session = self.supabase.auth.exchange_code_for_session(code)
            
            if not session.user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Erreur lors de l'authentification OAuth"
                )
            
            # Vérifier si l'utilisateur existe déjà
            existing_user = self.supabase.table("users").select("*").eq("auth_id", session.user.id).execute()
            
            if existing_user.data:
                # Utilisateur existant, mettre à jour last_login
                user = existing_user.data[0]
                self.supabase.table("users").update({"last_login": datetime.utcnow().isoformat()}).eq("id", user["id"]).execute()
            else:
                # Nouvel utilisateur, créer le profil
                user_data = {
                    "email": session.user.email,
                    "username": session.user.email.split("@")[0],  # Username par défaut
                    "password": "",  # Pas de mot de passe pour OAuth
                    "first_name": session.user.user_metadata.get("full_name", "").split(" ")[0] if session.user.user_metadata.get("full_name") else "",
                    "last_name": " ".join(session.user.user_metadata.get("full_name", "").split(" ")[1:]) if session.user.user_metadata.get("full_name") else "",
                    "role": "user",
                    "auth_id": session.user.id,
                    "is_active": True
                }
                
                db_response = self.supabase.table("users").insert(user_data).execute()
                user = db_response.data[0]
            
            # Créer le token JWT
            access_token = self._create_access_token(
                data={"sub": str(user["id"]), "email": user["email"]}
            )
            
            return {
                "success": True,
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "username": user["username"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "role": user["role"]
                }
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de l'authentification OAuth: {str(e)}"
            )
