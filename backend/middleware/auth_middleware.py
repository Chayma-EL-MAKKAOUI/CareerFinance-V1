from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Callable
import logging
from dependencies.auth_dependencies import get_optional_current_user

log = logging.getLogger("careerfinance-auth")

class AuthMiddleware:
    """Middleware global pour l'authentification"""
    
    def __init__(self, app):
        self.app = app
        # Routes publiques qui ne nécessitent pas d'authentification
        self.public_routes = {
            "/api/health",
            "/api/version",
            "/api/auth/register",
            "/api/auth/login",
            "/api/auth/oauth/google/url",
            "/api/auth/oauth/github/url",
            "/api/auth/oauth/google/callback",
            "/api/auth/oauth/github/callback",
            "/docs",
            "/redoc",
            "/openapi.json"
        }
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Vérifier si c'est une route publique
            if self._is_public_route(request.url.path):
                # Route publique, pas d'authentification requise
                return await self.app(scope, receive, send)
            
            # Route protégée, vérifier l'authentification
            try:
                # Vérifier si un token est présent
                auth_header = request.headers.get("Authorization")
                if not auth_header or not auth_header.startswith("Bearer "):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token d'authentification requis"
                    )
                
                # Le token sera vérifié par les dépendances des routes
                # Ce middleware vérifie juste sa présence
                
            except HTTPException as e:
                # Retourner une erreur d'authentification
                response = JSONResponse(
                    status_code=e.status_code,
                    content={"detail": e.detail}
                )
                await response(scope, receive, send)
                return
            
            except Exception as e:
                log.error(f"Erreur dans le middleware d'authentification: {e}")
                response = JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"detail": "Erreur interne du serveur"}
                )
                await response(scope, receive, send)
                return
        
        # Pour les autres types de scope (WebSocket, etc.), passer directement
        return await self.app(scope, receive, send)
    
    def _is_public_route(self, path: str) -> bool:
        """Vérifier si une route est publique"""
        # Vérifier les routes exactes
        if path in self.public_routes:
            return True
        
        # Vérifier les routes d'authentification
        if path.startswith("/api/auth/"):
            return True
        
        # Vérifier les routes de documentation
        if path.startswith("/docs") or path.startswith("/redoc"):
            return True
        
        # Vérifier les routes OpenAPI
        if path.startswith("/openapi"):
            return True
        
        # Vérifier les routes de santé
        if path.startswith("/api/health") or path.startswith("/api/version"):
            return True
        
        # Toutes les autres routes sont protégées
        return False

def add_auth_middleware(app):
    """Ajouter le middleware d'authentification à l'application"""
    app.add_middleware(AuthMiddleware)
    log.info("✅ Middleware d'authentification ajouté")
    return app
