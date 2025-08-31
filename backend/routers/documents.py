# routers/documents.py
<<<<<<< HEAD
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.ocr_service import extract_text_from_pdf, extract_text_from_image
from services.supabase_doc_rag_service import supabase_doc_rag
from services.gemini_doc import analyze_with_gemini_with_context
from typing import Any, Dict, List, Optional
=======
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from services.ocr_service import extract_text_from_pdf, extract_text_from_image
from services.gemini_doc import analyze_with_gemini_with_context
from dependencies.auth_dependencies import get_current_user
from typing import Any, Dict, List, Optional
import os

# Import conditionnel de Supabase (seulement si configuré)
supabase_doc_rag = None
try:
    from services.supabase_doc_rag_service import supabase_doc_rag
except ValueError as e:
    if "SUPABASE_URL" in str(e) or "SUPABASE_KEY" in str(e):
        print("⚠️ Supabase non configuré - fonctionnalités RAG désactivées")
    else:
        raise e
>>>>>>> 5e0de77 (Auth commit)

router = APIRouter()


# ───────────────────────── Helpers ─────────────────────────

def _get(h, key):
    """Supporte dict OU objet (getattr)."""
    if isinstance(h, dict):
        return h.get(key)
    return getattr(h, key, None)

def _num(x, default: float = 0.0) -> float:
    try:
        return float(x) if x is not None else float(default)
    except Exception:
        return float(default)

def build_global_analysis(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Construit une synthèse dynamique pour l'UI à partir de l'analyse LLM.
    Renvoie:
      {
        "status": "ok|warning|alert",
        "title": "Bulletin conforme|Bulletin à vérifier|Anomalies détectées",
        "deductionRate": 22.0,
        "highlights": ["...", "..."],
        "summary": "texte court"
      }
    """
    r = analysis.get("resume", {}) or {}
    d = analysis.get("details", {}) or {}
    anomalies = analysis.get("anomalies", []) or []

    brut = _num(r.get("salaireBrut")) or _num(d.get("salaireBase"))
    net = _num(r.get("salaireNet")) or _num(d.get("netAPayer"))
    cot_resume = _num(r.get("cotisations"))
    imp_resume  = _num(r.get("impots"))

    cot_details = sum(_num(x.get("montant")) for x in d.get("cotisations", []) if isinstance(x, dict))
    imp_details = sum(_num(x.get("montant")) for x in d.get("impots", []) if isinstance(x, dict))

    cot = cot_resume if cot_resume > 0 else cot_details
    imp = imp_resume if imp_resume > 0 else imp_details

    # Taux de prélèvement robuste
    deduction_rate = 0.0
    if brut > 0:
        if net > 0:
            deduction_rate = max(0.0, round(((brut - net) / brut) * 100.0, 1))
        else:
            deduction_rate = max(0.0, round(((cot + imp) / brut) * 100.0, 1))

    # Cohérence net
    expected_net = brut - (cot + imp)
    net_ecart_abs = abs(expected_net - net) if brut > 0 and net > 0 else 0.0
    net_ecart_tol = max(0.02 * brut, 50.0)  # 2% du brut ou 50 MAD

    flags: List[str] = []
    status = "ok"

    # Seuils usuels Maroc : ~10–45%
    if deduction_rate < 10 or deduction_rate > 45:
        flags.append("Taux de prélèvement inhabituel.")
        status = "warning"

    if net > 0 and net_ecart_abs > net_ecart_tol:
        flags.append("Écart entre le net calculé et le net déclaré.")
        status = "warning"

    if any((a.get("impact", "").lower() == "élevé") for a in anomalies if isinstance(a, dict)):
        status = "alert"

    title = {
        "ok": "Bulletin conforme",
        "warning": "Bulletin à vérifier",
        "alert": "Anomalies détectées"
    }.get(status, "Analyse")

    highlights: List[str] = []
    if brut > 0:
        highlights.append(f"Salaire brut: {int(brut)} MAD")
    if net > 0:
        highlights.append(f"Salaire net: {int(net)} MAD")
    highlights.append(f"Taux de prélèvement: {deduction_rate:.1f}%")
    if flags:
        highlights.extend(flags)

    # Si le LLM a déjà fourni une synthèse (meta.summary), on la privilégie
    meta_summary = (analysis.get("meta") or {}).get("summary")
    if isinstance(meta_summary, str) and meta_summary.strip():
        summary = meta_summary.strip()
    else:
        summary = (
            f"Votre bulletin présente un taux de prélèvement de {deduction_rate:.1f}%. "
            "Les résultats semblent conformes." if status == "ok" else
            f"Taux de prélèvement {deduction_rate:.1f}%. "
            "Certaines vérifications sont recommandées." if status == "warning" else
            f"Taux de prélèvement {deduction_rate:.1f}%. "
            "Des anomalies importantes ont été détectées."
        )

    return {
        "status": status,
        "title": title,
        "deductionRate": deduction_rate,
        "highlights": highlights,
        "summary": summary
    }


# ───────────────────────── Endpoint ─────────────────────────

@router.post("/upload")
<<<<<<< HEAD
async def upload_document(file: UploadFile = File(...)):
=======
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
>>>>>>> 5e0de77 (Auth commit)
    file_bytes = await file.read()
    try:
        # 1) OCR selon le type MIME
        if file.content_type == "application/pdf":
            text = extract_text_from_pdf(file_bytes)
        elif file.content_type in {"image/jpeg", "image/jpg", "image/png"}:
            text = extract_text_from_image(file_bytes)
        else:
            raise HTTPException(
                status_code=415,
                detail=f"Format non pris en charge: {file.content_type}",
            )

        # 2) Stockage + indexation RAG (best-effort)
        try:
            doc_id = supabase_doc_rag.store_user_document(
                title=file.filename or "Document utilisateur",
                text=text,
<<<<<<< HEAD
                user_id=1,  # TODO: remplacer par l'ID utilisateur réel
=======
                user_id=current_user.get("id", 1),  # Utiliser l'ID utilisateur réel
>>>>>>> 5e0de77 (Auth commit)
                mime_type=file.content_type,
                source="user_upload"
            )
            supabase_doc_rag.chunk_and_store_documents(doc_id=doc_id)
            supabase_doc_rag.embed_new_chunks()
            supabase_doc_rag.build_or_load_faiss()
        except Exception as e:
            print(f"⚠️ Erreur stockage/indexation: {e}")

        # 3) RAG: recherche de contexte
        hits = supabase_doc_rag.search(text, top_k=6)
        contexts = [_get(h, "text") for h in hits if _get(h, "text")]

        # 4) Analyse LLM enrichie par le contexte
        analysis = analyze_with_gemini_with_context(text, contexts)
        if isinstance(analysis, dict) and "error" in analysis:
            raise HTTPException(status_code=500, detail="Erreur d'analyse Gemini")
        if not isinstance(analysis, dict):
            analysis = {}

        # 5) Mapping UI
        analysis_ui = {
            "resume": {
                "salaireBrut": analysis.get("resume", {}).get("salaireBrut", 0),
                "salaireNet": analysis.get("resume", {}).get("salaireNet", 0),
                "cotisations": analysis.get("resume", {}).get("cotisations", 0),
                "impots": analysis.get("resume", {}).get("impots", 0),
            },
            "details": analysis.get("details", {}),
            "anomalies": analysis.get("anomalies", []),
            "recommandations": analysis.get("recommandations", []),
        }

        # 6) Analyse globale dynamique
        analysis_global = build_global_analysis(analysis)

        # 7) Réponse
        return {
            "fileName": file.filename,
            "mime": file.content_type,
            "contexts": contexts,
            "context_used": [
                {
                    "title": _get(h, "title"),
                    "source": _get(h, "source"),
                    "url": _get(h, "url"),
                    "ord": _get(h, "ord"),
                    "score": _get(h, "score"),
                }
                for h in hits
            ],
            "analysis": analysis_ui,
            "analysis_global": analysis_global,   # ← bloc prêt pour l’UI
            "analysis_raw": analysis,             # debug
        }

    finally:
        await file.close()
