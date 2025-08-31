# 🚨 Dépannage Rapide - Authentification CareerFinance AI

## 🔍 Problème : Écran de chargement infini

Si l'écran de chargement d'authentification reste affiché plus d'une minute, suivez ces étapes :

### 1. Vérification Rapide de l'API

```bash
# Test rapide de l'API
python test_api_health.py
```

### 2. Vérifications de Base

#### ✅ Backend démarré ?
```bash
cd backend
python main.py
```
**Attendu** : `✅ Application démarrée`

#### ✅ Frontend démarré ?
```bash
cd frontend
npm run dev
```
**Attendu** : `Ready - started server on 0.0.0.0:3000`

#### ✅ Variables d'environnement configurées ?
```bash
# Backend
ls backend/.env

# Frontend  
ls frontend/.env.local
```

### 3. Solutions Rapides

#### 🔧 Solution 1 : Nettoyer le cache
```bash
# Frontend
cd frontend
rm -rf .next
npm run dev

# Ou dans le navigateur
# Ctrl+Shift+R (rechargement forcé)
```

#### 🔧 Solution 2 : Supprimer le token invalide
```javascript
// Dans la console du navigateur (F12)
localStorage.removeItem('auth_token')
// Puis recharger la page
```

#### 🔧 Solution 3 : Vérifier la configuration Supabase
```bash
# Vérifier que le fichier .env contient :
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
```

### 4. Diagnostic Détaillé

#### 📊 Vérifier les logs du navigateur
1. Ouvrir les outils de développement (F12)
2. Aller dans l'onglet "Console"
3. Chercher les messages d'erreur commençant par `🔍 useAuth` ou `❌`

#### 📊 Vérifier les logs du backend
```bash
cd backend
python main.py
# Chercher les erreurs dans les logs
```

### 5. Erreurs Courantes

#### ❌ "Configuration Supabase manquante"
**Solution** : Créer le fichier `backend/.env` avec vos credentials Supabase

#### ❌ "Impossible de se connecter à l'API"
**Solution** : 
1. Vérifier que le backend est démarré sur le port 8000
2. Vérifier que `NEXT_PUBLIC_API_URL=http://localhost:8000` dans `frontend/.env.local`

#### ❌ "Token invalide"
**Solution** : 
1. Supprimer le token : `localStorage.removeItem('auth_token')`
2. Se reconnecter

#### ❌ "Timeout lors de la vérification"
**Solution** :
1. Vérifier la connexion internet
2. Vérifier que Supabase est accessible
3. Redémarrer le backend

### 6. Test Complet

```bash
# Test complet de l'authentification
python test_auth_complete.py
```

### 7. Réinitialisation Complète

Si rien ne fonctionne :

```bash
# 1. Arrêter tous les serveurs (Ctrl+C)

# 2. Nettoyer le cache
cd frontend
rm -rf .next
cd ../backend
rm -rf __pycache__

# 3. Redémarrer
cd backend
python main.py

# 4. Nouveau terminal
cd frontend
npm run dev

# 5. Nettoyer le navigateur
# - Supprimer les cookies
# - Vider le cache
# - localStorage.removeItem('auth_token')
```

### 8. Configuration Minimale

Pour tester rapidement, créez un fichier `backend/.env` minimal :

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production
APP_SECRET_KEY=dev-app-secret-key-change-in-production
FRONTEND_URL=http://localhost:3000
ENV=dev
```

### 9. Support

Si le problème persiste :

1. **Vérifiez** les logs d'erreur
2. **Testez** avec `test_api_health.py`
3. **Consultez** le guide complet `AUTHENTICATION_GUIDE.md`
4. **Vérifiez** que Supabase est configuré correctement

---

**💡 Astuce** : L'écran de chargement a maintenant un timeout de 5 secondes. Si il reste affiché plus longtemps, c'est un problème de configuration ou de réseau.
