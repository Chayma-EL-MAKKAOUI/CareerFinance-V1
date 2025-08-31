# 🔐 Guide d'Authentification CareerFinance AI

Ce guide vous accompagne dans la configuration et l'utilisation du système d'authentification complet avec Supabase.

## 📋 Prérequis

- Python 3.8+
- Node.js 16+
- Compte Supabase (gratuit)
- Projet Supabase configuré

## 🚀 Configuration Rapide

### 1. Configuration Supabase

1. **Créez un projet Supabase** sur [supabase.com](https://supabase.com)
2. **Récupérez vos credentials** dans Settings > API
3. **Exécutez le script SQL** dans l'éditeur SQL de Supabase :

```sql
-- Copiez le contenu de backend/supabase_auth_setup.sql
-- et exécutez-le dans l'éditeur SQL de votre projet Supabase
```

### 2. Configuration Backend

Créez un fichier `.env` dans le dossier `backend/` :

```env
# Configuration Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# Configuration JWT
JWT_SECRET_KEY=your_super_secret_jwt_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuration App
APP_SECRET_KEY=your_app_secret_key_here
FRONTEND_URL=http://localhost:3000

# Configuration Environnement
ENV=dev
```

### 3. Configuration Frontend

Créez un fichier `.env.local` dans le dossier `frontend/` :

```env
# Configuration API Backend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🏃‍♂️ Démarrage

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

## 🧪 Tests

### Test Complet de l'Authentification

```bash
python test_auth_complete.py
```

### Test Manuel

1. **Ouvrez** http://localhost:3000
2. **Cliquez** sur "S'inscrire"
3. **Créez** un compte
4. **Testez** la navigation entre les pages protégées

## 🔒 Fonctionnalités

### ✅ Authentification Complète

- **Inscription** : Création de compte avec validation
- **Connexion** : Authentification sécurisée
- **Déconnexion** : Fermeture de session propre
- **Protection des routes** : Middleware Next.js + FastAPI
- **Redirection automatique** : Vers /login si non connecté

### ✅ Sécurité

- **JWT Tokens** : Authentification stateless
- **Hachage bcrypt** : Mots de passe sécurisés
- **Row Level Security** : Protection des données Supabase
- **Validation** : Données d'entrée sécurisées

### ✅ Interface Utilisateur

- **Design moderne** : Interface cohérente
- **Responsive** : Mobile et desktop
- **Thème sombre/clair** : Support complet
- **Feedback utilisateur** : Messages d'erreur clairs

## 📁 Structure des Fichiers

```
├── frontend/
│   ├── middleware.ts              # Protection des routes Next.js
│   ├── lib/useAuth.js             # Hook d'authentification
│   ├── components/Auth/
│   │   └── AuthGuard.tsx          # Protection côté client
│   └── app/auth/
│       ├── login/page.tsx         # Page de connexion
│       └── register/page.tsx      # Page d'inscription
├── backend/
│   ├── routers/auth.py            # Routes d'authentification
│   ├── services/supabase_auth_service.py  # Service Supabase
│   ├── dependencies/auth_dependencies.py  # Dépendances FastAPI
│   ├── models/auth_models.py      # Modèles Pydantic
│   └── config/auth_config.py      # Configuration
└── supabase_auth_setup.sql        # Script SQL Supabase
```

## 🔧 Configuration Avancée

### OAuth (Optionnel)

Pour activer Google/GitHub OAuth, ajoutez dans `.env` :

```env
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# GitHub OAuth
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
```

### Variables d'Environnement

| Variable | Description | Requis |
|----------|-------------|--------|
| `SUPABASE_URL` | URL de votre projet Supabase | ✅ |
| `SUPABASE_ANON_KEY` | Clé anonyme Supabase | ✅ |
| `SUPABASE_SERVICE_ROLE_KEY` | Clé service Supabase | ✅ |
| `JWT_SECRET_KEY` | Clé secrète JWT | ✅ |
| `APP_SECRET_KEY` | Clé secrète de l'application | ✅ |
| `FRONTEND_URL` | URL du frontend | ✅ |

## 🚨 Dépannage

### Erreurs Courantes

1. **"Configuration Supabase manquante"**
   - Vérifiez vos variables d'environnement
   - Assurez-vous que le fichier `.env` est dans le bon dossier

2. **"Token invalide"**
   - Vérifiez que JWT_SECRET_KEY est défini
   - Assurez-vous que le token n'est pas expiré

3. **"Erreur de connexion"**
   - Vérifiez que Supabase est en ligne
   - Vérifiez vos credentials Supabase

4. **"Route protégée inaccessible"**
   - Vérifiez que le middleware Next.js est actif
   - Assurez-vous que le token est envoyé dans les headers

### Logs de Débogage

Activez les logs détaillés :

```bash
# Backend
export LOG_LEVEL=DEBUG
python main.py

# Frontend
npm run dev
# Vérifiez la console du navigateur
```

## 📚 API Endpoints

### Authentification

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/auth/register` | POST | Inscription utilisateur |
| `/api/auth/login` | POST | Connexion utilisateur |
| `/api/auth/logout` | POST | Déconnexion utilisateur |
| `/api/auth/me` | GET | Profil utilisateur actuel |
| `/api/auth/health` | GET | Santé du service |

### Exemples d'Utilisation

#### Inscription
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "username",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

#### Connexion
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

#### Route Protégée
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🎯 Prochaines Étapes

1. **Personnalisation** : Adaptez le design à votre marque
2. **Fonctionnalités** : Ajoutez la récupération de mot de passe
3. **Sécurité** : Implémentez la validation d'email
4. **Performance** : Optimisez les requêtes Supabase
5. **Monitoring** : Ajoutez des logs et métriques

## 🤝 Support

Pour toute question ou problème :

1. **Vérifiez** ce guide
2. **Consultez** les logs d'erreur
3. **Testez** avec `test_auth_complete.py`
4. **Vérifiez** la configuration Supabase

---

**Note** : Ce système d'authentification est conçu pour être sécurisé en production. Assurez-vous de :
- Utiliser des clés secrètes fortes
- Configurer HTTPS en production
- Surveiller les tentatives d'accès
- Maintenir les dépendances à jour
