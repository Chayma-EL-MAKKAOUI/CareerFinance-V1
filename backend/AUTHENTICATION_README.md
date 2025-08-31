# Système d'Authentification CareerFinance AI

Ce document décrit le système d'authentification complet implémenté avec Supabase et FastAPI.

## 🏗️ Architecture

Le système d'authentification comprend :

- **Supabase** : Base de données et gestion des utilisateurs
- **FastAPI** : API backend avec JWT
- **Row Level Security (RLS)** : Sécurité au niveau des données
- **OAuth** : Authentification sociale (Google, GitHub)

## 📋 Prérequis

1. **Compte Supabase** avec un projet créé
2. **Variables d'environnement** configurées
3. **Dépendances Python** installées

## ⚙️ Configuration

### 1. Variables d'environnement

Créez un fichier `.env` dans le dossier `backend/` :

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# JWT Configuration
JWT_SECRET_KEY=your_super_secret_jwt_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OAuth Configuration (optionnel)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

# App Configuration
APP_SECRET_KEY=your_app_secret_key_here
FRONTEND_URL=http://localhost:3000
```

### 2. Configuration Supabase

Exécutez le script SQL `supabase_auth_setup.sql` dans l'éditeur SQL de Supabase :

```bash
# Copiez le contenu de backend/supabase_auth_setup.sql
# et exécutez-le dans l'éditeur SQL de votre projet Supabase
```

### 3. Installation des dépendances

```bash
cd backend
pip install -r requirements_rag.txt
```

## 🚀 Utilisation

### Endpoints d'authentification

#### Inscription
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user"
}
```

#### Connexion
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

#### Profil utilisateur
```http
GET /api/auth/me
Authorization: Bearer <your_jwt_token>
```

#### Déconnexion
```http
POST /api/auth/logout
Authorization: Bearer <your_jwt_token>
```

#### OAuth Google
```http
GET /api/auth/oauth/google/url
```

#### OAuth GitHub
```http
GET /api/auth/oauth/github/url
```

### Protection des routes

Pour protéger une route, utilisez la dépendance `get_current_user` :

```python
from dependencies.auth_dependencies import get_current_user

@app.get("/protected-route")
async def protected_endpoint(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello {current_user['username']}!"}
```

### Rôles et permissions

```python
from dependencies.auth_dependencies import require_admin, require_user

@app.get("/admin-only")
async def admin_endpoint(current_user: dict = Depends(require_admin)):
    return {"message": "Admin access granted"}

@app.get("/user-only")
async def user_endpoint(current_user: dict = Depends(require_user)):
    return {"message": "User access granted"}
```

## 🔒 Sécurité

### Row Level Security (RLS)

Toutes les tables sont protégées par RLS :

- **users** : Chaque utilisateur ne voit que son propre profil
- **documents** : Accès uniquement aux documents de l'utilisateur
- **coaching_sessions** : Sessions de coaching privées
- **chat_sessions** : Historique de chat privé
- **rag_queries** : Requêtes RAG privées

### JWT Tokens

- **Expiration** : 30 minutes par défaut (configurable)
- **Algorithme** : HS256
- **Stockage** : Côté client (localStorage, cookies, etc.)

### OAuth

- **Google** : Authentification via Google OAuth 2.0
- **GitHub** : Authentification via GitHub OAuth 2.0
- **Redirection** : Vers le frontend après authentification

## 🧪 Tests

Exécutez les tests d'authentification :

```bash
cd backend
python test_auth.py
```

## 📁 Structure des fichiers

```
backend/
├── config/
│   └── auth_config.py          # Configuration d'authentification
├── dependencies/
│   └── auth_dependencies.py    # Dépendances FastAPI
├── models/
│   └── auth_models.py          # Modèles Pydantic
├── routers/
│   └── auth.py                 # Router d'authentification
├── services/
│   └── supabase_auth_service.py # Service d'authentification
├── supabase_auth_setup.sql     # Script SQL Supabase
├── env.example                  # Exemple de variables d'environnement
├── test_auth.py                # Tests d'authentification
└── AUTHENTICATION_README.md    # Ce fichier
```

## 🔧 Configuration OAuth

### Google OAuth

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un projet ou sélectionnez un existant
3. Activez l'API Google+ API
4. Créez des identifiants OAuth 2.0
5. Ajoutez les URIs de redirection autorisés
6. Copiez le Client ID et Client Secret dans votre `.env`

### GitHub OAuth

1. Allez sur [GitHub Developer Settings](https://github.com/settings/developers)
2. Créez une nouvelle OAuth App
3. Ajoutez l'URL de callback
4. Copiez le Client ID et Client Secret dans votre `.env`

## 🚨 Dépannage

### Erreurs courantes

1. **Configuration manquante** : Vérifiez que toutes les variables d'environnement sont définies
2. **Erreur Supabase** : Vérifiez l'URL et les clés de votre projet
3. **Erreur JWT** : Vérifiez que JWT_SECRET_KEY est défini et sécurisé
4. **Erreur OAuth** : Vérifiez la configuration des providers OAuth

### Logs

Activez le logging détaillé en modifiant le niveau dans `main.py` :

```python
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Ressources

- [Documentation Supabase](https://supabase.com/docs)
- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Documentation JWT](https://jwt.io/)
- [Documentation OAuth 2.0](https://oauth.net/2/)

## 🤝 Support

Pour toute question ou problème :

1. Vérifiez ce README
2. Consultez les logs d'erreur
3. Testez avec `test_auth.py`
4. Vérifiez la configuration Supabase

---

**Note** : Ce système d'authentification est conçu pour être sécurisé en production. Assurez-vous de :
- Utiliser des clés secrètes fortes
- Configurer HTTPS en production
- Surveiller les tentatives d'accès
- Maintenir les dépendances à jour
