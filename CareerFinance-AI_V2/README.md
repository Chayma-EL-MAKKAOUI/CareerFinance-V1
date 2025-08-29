# 🎯 CareerFinance AI - Coaching Carrière avec Supabase

Application complète de coaching carrière utilisant l'IA et les données LinkedIn stockées dans Supabase.

## 🚀 Démarrage Rapide

### 1. Installation des dépendances

```bash
# Backend (Python)
cd backend
pip install -r requirements_rag.txt

# Frontend (Node.js)
cd frontend
npm install
```

### 2. Configuration Supabase

Créez un fichier `backend/.env` avec vos credentials Supabase :

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
CAREER_EMBED_MODEL=sentence-transformers/paraphrase-multilingual-mpnet-base-v2
```

### 3. Migration des données (optionnel)

```bash
cd backend
python migrate_career_data.py
```

### 4. Lancement de l'application

**Option 1: Script automatique (recommandé)**
```bash
python start_app.py
```

**Option 2: Manuel**
```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## 📱 URLs de l'application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentation API**: http://localhost:8000/docs
- **Coaching carrière**: http://localhost:3000/coaching-carriere

## 🎯 Fonctionnalités

### ✅ Coaching Carrière avec Supabase
- Génération de plans de carrière personnalisés
- Analyse des compétences vs marché LinkedIn
- Recherche de profils similaires
- Insights sectoriels
- Historique des sessions

### ✅ Autres fonctionnalités
- Analyse de bulletins de paie
- Coaching carrière classique
- RAG documents
- Analyse salariale

## 🏗️ Architecture

- **Backend**: FastAPI + Supabase + FAISS + sentence-transformers
- **Frontend**: Next.js + React + Tailwind CSS
- **Base de données**: Supabase (PostgreSQL)
- **IA**: Gemini AI + RAG (Retrieval-Augmented Generation)

## 📊 Tables Supabase utilisées

- `profileslinkedin` - Profils LinkedIn scrapés
- `profile_chunks` - Chunks de contenu avec embeddings
- `coaching_sessions` - Historique des sessions de coaching

## 🧪 Tests

```bash
# Tests backend
cd backend
python test_supabase_career_coaching.py
```

## 🔧 Dépannage

### Problèmes courants

1. **"Système non initialisé"**
   ```bash
   curl -X POST http://localhost:8000/api/supabase-career/initialize
   ```

2. **"Aucune donnée trouvée"**
   ```bash
   cd backend
   python migrate_career_data.py
   ```

3. **Erreur de connexion Supabase**
   - Vérifiez vos variables d'environnement dans `backend/.env`
   - Assurez-vous que les tables existent dans Supabase

## 📚 Documentation

- [Documentation API](http://localhost:8000/docs)
- [Guide détaillé](backend/SUPABASE_CAREER_COACHING.md)

---

**🎉 Prêt à utiliser!** Votre application de coaching carrière est maintenant opérationnelle!
