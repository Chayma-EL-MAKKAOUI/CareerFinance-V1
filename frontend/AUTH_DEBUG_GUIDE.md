# 🔍 Guide de Debug - Authentification

## Problème
L'authentification ne fonctionne pas correctement.

## Solutions de Diagnostic

### 1. Test de l'Authentification
Allez sur la page de test d'authentification :
```
http://localhost:3000/auth-test
```

Cette page vous permettra de :
- ✅ Voir l'état actuel de l'authentification
- ✅ Tester la connexion/déconnexion
- ✅ Voir les valeurs du localStorage
- ✅ Debugger le hook useAuth

### 2. Vérification du localStorage
Ouvrez les DevTools (F12) et vérifiez :
```javascript
// Dans la console du navigateur
localStorage.getItem('auth_token')
```

### 3. Test de la Page de Connexion
Allez sur la page de connexion :
```
http://localhost:3000/auth/login
```

Utilisez n'importe quel email/mot de passe pour la démonstration.

### 4. Vérification des Composants

#### Hook useAuth
Le hook `useAuth` dans `frontend/lib/useAuth.js` :
- ✅ Vérifie le token dans localStorage au chargement
- ✅ Accepte n'importe quel email/mot de passe pour la démo
- ✅ Retourne `isLoading` et `isLoggedIn`

#### Composant ProtectedRoute
Le composant `ProtectedRoute` dans `frontend/components/Auth/ProtectedRoute.tsx` :
- ✅ Utilise le hook useAuth
- ✅ Redirige vers `/auth/login` si non connecté
- ✅ Affiche un loader pendant la vérification

### 5. Pages Protégées
Toutes ces pages nécessitent maintenant une authentification :
- ✅ `/` - Page principale
- ✅ `/analyse-salariale` - Analyse salariale
- ✅ `/coaching-carriere` - Coaching carrière
- ✅ `/bulletin-paie` - Bulletin de paie
- ✅ `/dashboard` - Dashboard
- ✅ `/historique` - Historique
- ✅ `/test` - Page de test

### 6. Pages Publiques
Ces pages restent accessibles sans authentification :
- ✅ `/auth/login` - Connexion
- ✅ `/auth/register` - Inscription
- ✅ `/auth-test` - Test d'authentification

## Étapes de Test

1. **Nettoyer le localStorage** :
   ```javascript
   localStorage.clear()
   ```

2. **Aller sur `/auth-test`** et vérifier l'état initial

3. **Se connecter** avec n'importe quel email/mot de passe

4. **Vérifier que l'état change** dans le debug

5. **Tester une page protégée** comme `/dashboard`

6. **Se déconnecter** et vérifier la redirection

## Problèmes Courants

### Problème : Boucle de redirection
**Cause** : Le composant ProtectedRoute redirige en boucle
**Solution** : Vérifier que `isLoading` et `isLoggedIn` sont correctement définis

### Problème : Token non sauvegardé
**Cause** : localStorage non accessible
**Solution** : Vérifier que le navigateur supporte localStorage

### Problème : État non mis à jour
**Cause** : Le hook useAuth ne se met pas à jour
**Solution** : Vérifier les dépendances du useEffect

## Debug Avancé

### Ajouter des logs dans useAuth
```javascript
console.log('useAuth - isLoading:', isLoading)
console.log('useAuth - isLoggedIn:', isLoggedIn)
console.log('useAuth - user:', user)
```

### Vérifier le rendu du ProtectedRoute
```javascript
console.log('ProtectedRoute - isLoading:', isLoading)
console.log('ProtectedRoute - isLoggedIn:', isLoggedIn)
```

## Contact
Si le problème persiste, vérifiez :
1. Les erreurs dans la console du navigateur
2. Les erreurs dans les DevTools Network
3. L'état du localStorage
4. Les logs de debug
