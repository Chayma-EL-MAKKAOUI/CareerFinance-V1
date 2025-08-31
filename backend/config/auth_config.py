import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

class AuthSettings(BaseSettings):
    """Configuration pour l'authentification"""
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    
    # App
    APP_SECRET_KEY: str
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Sécurité
    PASSWORD_MIN_LENGTH: int = 8
    USERNAME_MIN_LENGTH: int = 3
    USERNAME_MAX_LENGTH: int = 50
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignorer les variables extra du fichier .env
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_config()
    
    def _validate_config(self):
        """Valider la configuration requise"""
        required_fields = [
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY", 
            "SUPABASE_SERVICE_ROLE_KEY",
            "JWT_SECRET_KEY",
            "APP_SECRET_KEY"
        ]
        
        missing_fields = [field for field in required_fields if not getattr(self, field)]
        if missing_fields:
            # En mode développement, utiliser des valeurs par défaut
            if os.getenv("ENV", "dev") == "dev":
                print(f"⚠️  Configuration manquante en mode dev: {', '.join(missing_fields)}")
                print("⚠️  Utilisation de valeurs par défaut pour le développement")
                return
            else:
                raise ValueError(f"Configuration manquante: {', '.join(missing_fields)}")
    
    @property
    def is_oauth_configured(self) -> bool:
        """Vérifier si OAuth est configuré"""
        return bool(
            self.GOOGLE_CLIENT_ID and self.GOOGLE_CLIENT_SECRET or
            self.GITHUB_CLIENT_ID and self.GITHUB_CLIENT_SECRET
        )
    
    @property
    def is_google_oauth_configured(self) -> bool:
        """Vérifier si Google OAuth est configuré"""
        return bool(self.GOOGLE_CLIENT_ID and self.GOOGLE_CLIENT_SECRET)
    
    @property
    def is_github_oauth_configured(self) -> bool:
        """Vérifier si GitHub OAuth est configuré"""
        return bool(self.GITHUB_CLIENT_ID and self.GITHUB_CLIENT_SECRET)

# Instance globale de configuration
auth_settings = AuthSettings()
