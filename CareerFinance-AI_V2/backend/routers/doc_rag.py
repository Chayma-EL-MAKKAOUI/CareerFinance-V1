# routers/doc_rag.py
from fastapi import APIRouter, HTTPException, Query
from services.supabase_doc_rag_service import supabase_doc_rag
from pydantic import BaseModel
from typing import List, Dict, Any
import numpy as np
from typing import List, Optional
router = APIRouter()

@router.post("/doc-rag/chunk")
async def chunk_docs():
    try:
        out = supabase_doc_rag.chunk_and_store_documents()
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/doc-rag/embed")
async def embed_docs():
    try:
        out = supabase_doc_rag.embed_new_chunks()
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/doc-rag/build")
async def build_index():
    ok = supabase_doc_rag.build_or_load_faiss()
    if not ok:
        raise HTTPException(status_code=400, detail="Pas d'embeddings en base. Lance d'abord /doc-rag/embed.")
    return {"index": "ready"}

@router.get("/doc-rag/status")
async def status():
    return {
        "index_ready": supabase_doc_rag.index is not None,
    }


class SearchResult(BaseModel):
    id: str                    # chunk_id (UUID)
    text: str
    score: float
    doc_id: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    ord: Optional[int] = None

@router.get("/doc-rag/query", response_model=List[SearchResult])
async def query_rag(
    text: str = Query(..., min_length=2, description="Texte ou question à chercher"),
    k: int = Query(5, ge=1, le=20),
 ):
    try:
        hits = supabase_doc_rag.search(text, top_k=k)  # le service renvoie déjà des dicts
        return [
            SearchResult(
                id=h["chunk_id"],
                text=h["text"],
                score=h["score"],
                doc_id=h.get("doc_id"),
                title=h.get("title"),
                url=h.get("url"),
                source=h.get("source"),
                ord=h.get("ord"),
            )
            for h in hits
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Nouveaux endpoints pour la migration et gestion Supabase
@router.post("/doc-rag/chunk-specific")
async def chunk_specific_doc(doc_id: str):
    """Chunke un document spécifique par son ID"""
    try:
        out = supabase_doc_rag.chunk_and_store_documents(doc_id=doc_id)
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/doc-rag/documents-count")
async def get_documents_count():
    """Retourne le nombre de documents dans Supabase"""
    try:
        from services.supabase_doc_rag_service import supabase
        result = supabase.table("documents").select("id", count="exact").execute()
        chunks_result = supabase.table("doc_chunks").select("id", count="exact").execute()

        return {
            "documents_count": result.count,
            "chunks_count": chunks_result.count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class AnalyzeRequest(BaseModel):
    text: str

class AnalyzeResponse(BaseModel):
    analysis: str
    relevant_documents: List[SearchResult]
    confidence: float

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeRequest):
    """Analyse un texte en utilisant le RAG Supabase"""
    try:
        # Recherche de documents pertinents
        hits = supabase_doc_rag.search(request.text, top_k=5)

        # Conversion en SearchResult
        relevant_docs = [
            SearchResult(
                id=h["chunk_id"],
                text=h["text"],
                score=h["score"],
                doc_id=h.get("doc_id"),
                title=h.get("title"),
                url=h.get("url"),
                source=h.get("source"),
                ord=h.get("ord"),
            )
            for h in hits
        ]

        # Génération de l'analyse (simple pour l'instant)
        if relevant_docs:
            best_match = relevant_docs[0]
            confidence = best_match.score

            analysis = f"""Basé sur votre question "{request.text}", voici les informations pertinentes trouvées :

Document le plus pertinent : {best_match.title or 'Document sans titre'}
Source : {best_match.source or 'Non spécifiée'}

Extrait pertinent :
{best_match.text[:500]}{'...' if len(best_match.text) > 500 else ''}

Cette information provient de notre base de documents RH et juridiques."""
        else:
            confidence = 0.0
            analysis = f"""Je n'ai pas trouvé d'informations pertinentes dans notre base de documents pour votre question : "{request.text}".

Vous pourriez essayer de reformuler votre question ou de contacter directement le service RH."""

        return AnalyzeResponse(
            analysis=analysis,
            relevant_documents=relevant_docs,
            confidence=confidence
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse: {str(e)}")

