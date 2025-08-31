from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# Modèles pour l'inscription
class UserRegister(BaseModel):
    email: EmailStr = Field(..., description="Email de l'utilisateur")
    username: str = Field(..., min_length=3, max_length=50, description="Nom d'utilisateur")
    password: str = Field(..., min_length=8, description="Mot de passe (minimum 8 caractères)")
    first_name: str = Field(..., min_length=1, max_length=100, description="Prénom")
    last_name: str = Field(..., min_length=1, max_length=100, description="Nom")
    role: Optional[str] = Field(default="user", description="Rôle de l'utilisateur")

# Modèles pour la connexion
class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Email de l'utilisateur")
    password: str = Field(..., description="Mot de passe")

# Modèles pour la réponse d'authentification
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    total_analyses: Optional[int] = None
    document_analyses_count: Optional[int] = None
    salary_analyses_count: Optional[int] = None
    coaching_sessions_count: Optional[int] = None

class AuthResponse(BaseModel):
    success: bool
    access_token: str
    token_type: str
    user: UserResponse

class LogoutResponse(BaseModel):
    success: bool
    message: str

# Modèles pour OAuth
class OAuthProvider(BaseModel):
    provider: str = Field(..., description="Provider OAuth (google, github)")

class OAuthCallback(BaseModel):
    code: str = Field(..., description="Code d'autorisation OAuth")
    provider: str = Field(..., description="Provider OAuth")

# Modèles pour les erreurs
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None

# Modèle pour le profil utilisateur
class UserProfile(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    total_analyses: int
    document_analyses_count: int
    salary_analyses_count: int
    coaching_sessions_count: int
