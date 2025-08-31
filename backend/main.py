# backend/main.py
from __future__ import annotations

import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings, SettingsConfigDict

# ── Routers ───────────────────────────────────────────────────────────────
from routers import documents as documents_router
from routers import doc_rag   as doc_rag_router
from routers import salary    as salary_router
from routers import salary_enhanced as salary_enhanced_router
from routers import coaching  as coaching_router
from routers import rag_coaching as rag_coaching_router
from routers import supabase_career_coaching as supabase_career_coaching_router
<<<<<<< HEAD
=======
from routers import auth as auth_router
>>>>>>> 5e0de77 (Auth commit)

# ── Services (instances globales) ────────────────────────────────────────
try:
    from services.rag_service import linkedin_rag  # LinkedIn RAG (profils)
except Exception:
    linkedin_rag = None

try:
    from services.salary_rag import salary_rag     # RAG tabulaire salaire
except Exception:
    salary_rag = None

try:
    from services.doc_rag_service import doc_rag   # RAG documents (local)
except Exception:
    doc_rag = None

try:
    from services.supabase_doc_rag_service import supabase_doc_rag  # RAG documents Supabase
except Exception:
    supabase_doc_rag = None

try:
    from services.supabase_career_coaching_service import career_coaching_service  # RAG coaching carrière Supabase
except Exception:
    career_coaching_service = None

# ── Logging ──────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("careerfinance")

# ── Config ───────────────────────────────────────────────────────────────
class Settings(BaseSettings):
    APP_NAME: str = "CareerFinance AI"
    APP_VERSION: str = "v2"
    ENV: str = "dev"

    # Chemins FAISS docs (si fournis via .env)
    DOC_FAISS_INDEX: str = ""
    DOC_FAISS_MAP: str = ""
    DOC_EMBED_MODEL: str = ""  # ex: paraphrase-multilingual-mpnet-base-v2

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "*"]
    CORS_CREDENTIALS: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

# Normalise chemins FAISS docs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "data"))
os.makedirs(DATA_DIR, exist_ok=True)

os.environ.setdefault("DOC_FAISS_INDEX", settings.DOC_FAISS_INDEX or os.path.join(DATA_DIR, "doc_index.faiss"))
os.environ.setdefault("DOC_FAISS_MAP",   settings.DOC_FAISS_MAP   or os.path.join(DATA_DIR, "doc_index_map.json"))
if settings.DOC_EMBED_MODEL:
    os.environ["DOC_EMBED_MODEL"] = settings.DOC_EMBED_MODEL

# ── Lifespan ─────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    log.info("🚀 Démarrage CareerFinance AI...")

    # 1) LinkedIn RAG (non bloquant)
    try:
        if linkedin_rag:
            log.info("Init LinkedIn RAG…")
            if not getattr(linkedin_rag, "load_index", lambda: False)():
                linkedin_rag.load_linkedin_data()
                linkedin_rag.create_embeddings()
                linkedin_rag.build_index()
                if getattr(linkedin_rag, "save_index", None):
                    linkedin_rag.save_index()
            log.info("✓ LinkedIn RAG prêt")
        else:
            log.info("⚠ LinkedIn RAG non disponible")
    except Exception as e:
        log.warning("⚠ Init LinkedIn RAG: %s", e)

    # 2) Salary RAG (tabulaire)
    try:
        if salary_rag:
            log.info("Init Salary RAG…")
            if not getattr(salary_rag, "load_index", lambda: False)():
                salary_rag.load()
                salary_rag.create_embeddings()
                salary_rag.build_index()
                salary_rag.save_index()
            log.info("✓ Salary RAG prêt")
        else:
            log.info("⚠ Salary RAG non disponible")
    except Exception as e:
        log.warning("⚠ Init Salary RAG: %s", e)

    # 3) RAG documents local
    try:
        if doc_rag:
            log.info("Init Doc RAG local…")
            doc_rag.build_or_load_faiss()
            log.info("✓ Doc RAG local prêt")
        else:
            log.info("⚠ Doc RAG local non disponible")
    except Exception as e:
        log.warning("⚠ Init Doc RAG local: %s", e)

    # 4) Supabase Doc RAG
    try:
        if supabase_doc_rag:
            log.info("Init Supabase Doc RAG… ✓")
    except Exception as e:
        log.warning("⚠ Init Supabase Doc RAG: %s", e)

    # 5) Supabase Career Coaching
    try:
        if career_coaching_service:
            log.info("Init Supabase Career Coaching… ✓")
    except Exception as e:
        log.warning("⚠ Init Supabase Career Coaching: %s", e)

    log.info("✅ Application démarrée")
    yield
    log.info("🛑 Arrêt de l'application...")

# ── App ──────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
=======
# Middleware d'authentification global - DÉSACTIVÉ pour utiliser les dépendances FastAPI
# try:
#     from middleware.auth_middleware import add_auth_middleware
#     add_auth_middleware(app)
# except Exception as e:
#     log.warning(f"⚠️  Middleware d'authentification non chargé: {e}")
#     log.warning("L'application fonctionnera sans protection globale")

# Note: L'authentification est maintenant gérée par les dépendances FastAPI dans chaque router
log.info("🔒 Authentification JWT activée via les dépendances FastAPI")

>>>>>>> 5e0de77 (Auth commit)
# Health/version
@app.get("/api/health")
async def health():
    return {"ok": True}

@app.get("/api/version")
async def version():
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION, "env": settings.ENV}

# ── Mount routers (✅ préfixes corrects) ──────────────────────────────────
<<<<<<< HEAD
=======
# Authentification (routes publiques - pas de protection)
app.include_router(auth_router.router,              prefix="/api/auth",             tags=["authentication"])

# Routes protégées (nécessitent une authentification)
# Note: Toutes les autres routes sont maintenant protégées par défaut
>>>>>>> 5e0de77 (Auth commit)
app.include_router(documents_router.router,         prefix="/api/documents",        tags=["documents"])
# Laisse /api pour ton doc_rag existant si tu en dépends déjà
app.include_router(doc_rag_router.router,           prefix="/api",                  tags=["doc-rag"])

# ✅ Fix principal : bons préfixes pour les routes salaire
app.include_router(salary_router.router,            prefix="/api/salary",           tags=["salary"])
app.include_router(salary_enhanced_router.router,   prefix="/api/salary-enhanced",  tags=["salary-enhanced"])

# Coaching
app.include_router(coaching_router.router,          prefix="/api/coaching",         tags=["coaching"])
app.include_router(rag_coaching_router.router,      prefix="/api/rag",              tags=["rag-coaching"])
app.include_router(supabase_career_coaching_router.router, prefix="/api/supabase-career", tags=["supabase-career-coaching"])

# (optionnel) exécution directe: uvicorn backend.main:app --reload
if __name__ == "__main__":  # pragma: no cover
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
