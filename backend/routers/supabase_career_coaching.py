# routers/supabase_career_coaching.py
<<<<<<< HEAD
from fastapi import APIRouter, HTTPException, BackgroundTasks
=======
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
>>>>>>> 5e0de77 (Auth commit)
from pydantic import BaseModel
from typing import List, Dict, Any
from services.supabase_career_coaching_service import career_coaching_service
from services.careerPromt import generate_career_plan_with_rag as llm_generate_career_plan_with_rag
<<<<<<< HEAD
=======
from dependencies.auth_dependencies import get_current_user
>>>>>>> 5e0de77 (Auth commit)
import json

def _norm_priorite(val: str) -> str:
    v = (val or "").strip().lower()
    if v in {"high", "élevée", "elevee", "haute"}:
        return "high"
    if v in {"low", "faible"}:
        return "low"
    return "medium"

def _to_ui_payload(enriched: dict) -> dict:
    # Plan de carrière
    plan_src = (enriched.get("plan_carriere") or {}) if isinstance(enriched, dict) else {}
    etapes_src = plan_src.get("etapes") or []
    etapes = []
    for e in etapes_src:
        etapes.append({
            "titre": e.get("titre", ""),
            "duree": e.get("duree", ""),
            "description": e.get("description", ""),
            "competencesRequises": e.get("competences", []) or e.get("competences_requises", []),
            "salaireEstime": e.get("salaire") or e.get("salaire_estime") or 0,
        })

    # Formations
    formations_src = enriched.get("formations") or enriched.get("formations_recommandees") or []
    formations_reco = [{
        "titre": f.get("titre", f.get("nom", "")),
        "duree": f.get("duree", ""),
        "priorite": _norm_priorite(f.get("priorite", f.get("niveau", "medium"))),
        "description": f.get("description", ""),
    } for f in formations_src]

    # Négociation
    neg_src = enriched.get("negociation") or enriched.get("negociations") or {}
    script_negociation = {
        "points": neg_src.get("points_cles") or neg_src.get("points") or [],
        "arguments": neg_src.get("arguments") or [],
        "conseils": neg_src.get("conseils") or [],
    }

    # Insights LinkedIn
    insights = enriched.get("linkedin_insights") or {}
    top_profiles = insights.get("top_profiles", [])
    relevant_chunks = insights.get("relevant_chunks", [])

    linkedin_insights = {
        "profilesAnalyzed": insights.get("profiles_analyzed") or enriched.get("profiles_analyzed", 0),
        "topSkills": insights.get("top_skills", []),
        "targetCompanies": [p.get("entreprise") for p in top_profiles if p.get("entreprise")],
        "commonTitles": list({p.get("titre") for p in top_profiles if p.get("titre")}),
        "locations": [c.get("section") for c in relevant_chunks if c.get("section")],
    }

    # Petits fillers pour ne pas casser l’UI (optionnels)
    planning = [{"mois": f"M+{i+1}", "formation": fr["titre"]} for i, fr in enumerate(formations_reco[:6])]
    objectifs = [{
        "horizon": "3 mois",
        "objectif": f"Compléter: {formations_reco[0]['titre']}" if formations_reco else "Valider une formation clé",
        "smart_tags": ["Spécifique", "Mesurable", "Atteignable", "Réaliste", "Temporel"],
    }]
    suivi = [{"titre": "Certification en cours", "progression": "0"}]

    return {
        "objectif": enriched.get("objectif", ""),
        "competences": enriched.get("competences", []),
        "secteur": enriched.get("secteur", ""),
        "linkedInDataUsed": bool(enriched.get("rag_used")),
        "planCarriere": {"etapes": etapes},
        "scriptNegociation": script_negociation,
        "formationsRecommandees": formations_reco,
        "planningFormations": planning,
        "objectifsSMART": objectifs,
        "suiviProgres": suivi,
        "linkedinInsights": linkedin_insights,
        # tu peux aussi inclure des reco basées sur profils si tu veux plus tard
        "recommendationsBasedOnProfiles": [],
    }

router = APIRouter()

@router.get("/")
async def supabase_career_coaching_documentation():
    return {
        "title": "Système de Coaching Carrière avec Supabase + RAG",
        "description": "API pour le coaching de carrière utilisant RAG sur les données LinkedIn",
        "version": "2.0.0",
        "endpoints": {
            "GET /api/supabase-career/status": "Vérifier le statut du système",
            "POST /api/supabase-career/initialize": "Initialiser le système (chunking + index)",
            "POST /api/supabase-career/process-profiles": "Traiter les profils LinkedIn (chunking + embeddings)",
            "POST /api/supabase-career/coaching": "Session de coaching avec RAG",
            "POST /api/supabase-career/search-profiles": "Rechercher des profils LinkedIn similaires",
            "POST /api/supabase-career/analyze-skills": "Analyser les compétences vs marché",
            "GET /api/supabase-career/insights/{sector}": "Obtenir des insights sur un secteur",
            "GET /api/supabase-career/history/{user_id}": "Récupérer l'historique complet des sessions"
        }
    }

class CareerCoachingRequest(BaseModel):
    user_id: int = 1
    goal: str
    skills: List[str]
    sector: str
    useRAG: bool = True

class ProfileSearchRequest(BaseModel):
    query: str
    topK: int = 10

class SkillAnalysisRequest(BaseModel):
    skills: List[str]
    sector: str

class SaveSessionRequest(BaseModel):
    user_id: int = 1
    objectif: str
    competences: List[str]
    secteur: str
    plan_data: Dict[str, Any]

class SystemStatusResponse(BaseModel):
    isInitialized: bool
    profilesCount: int
    chunksCount: int
    indexExists: bool
    message: str

@router.get("/status", response_model=SystemStatusResponse)
<<<<<<< HEAD
async def get_system_status():
=======
async def get_system_status(current_user: dict = Depends(get_current_user)):
>>>>>>> 5e0de77 (Auth commit)
    try:
        index_exists = career_coaching_service.index is not None
        profiles_count = len(career_coaching_service.profile_map) if career_coaching_service.profile_map else 0
        chunks_count = len(career_coaching_service.chunk_map) if career_coaching_service.chunk_map else 0

        if not index_exists:
            try:
                if career_coaching_service.load_index():
                    index_exists = True
                    profiles_count = len(career_coaching_service.profile_map)
                    chunks_count = len(career_coaching_service.chunk_map)
                else:
                    return SystemStatusResponse(
                        isInitialized=False, profilesCount=0, chunksCount=0, indexExists=False,
                        message="Index non trouvé. Utilisez /initialize pour créer l'index."
                    )
            except Exception as e:
                return SystemStatusResponse(
                    isInitialized=False, profilesCount=0, chunksCount=0, indexExists=False,
                    message=f"Erreur lors du chargement de l'index: {str(e)}"
                )

        is_initialized = profiles_count > 0 and chunks_count > 0 and index_exists
        message = f"Système initialisé avec {profiles_count} profils et {chunks_count} chunks" if is_initialized else "Système non initialisé"

        return SystemStatusResponse(
            isInitialized=is_initialized, profilesCount=profiles_count,
            chunksCount=chunks_count, indexExists=index_exists, message=message
        )

    except Exception as e:
        return SystemStatusResponse(
            isInitialized=False, profilesCount=0, chunksCount=0,
            indexExists=False, message=f"Erreur lors de la vérification du statut: {str(e)}"
        )

@router.post("/process-profiles")
<<<<<<< HEAD
async def process_linkedin_profiles(background_tasks: BackgroundTasks):
=======
async def process_linkedin_profiles(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
>>>>>>> 5e0de77 (Auth commit)
    try:
        def process_profiles():
            try:
                success = career_coaching_service.process_and_chunk_profiles()
                if success:
                    print("✅ Traitement des profils terminé avec succès")
                else:
                    print("❌ Échec du traitement des profils")
            except Exception as e:
                print(f"❌ Erreur lors du traitement: {e}")

        profiles = career_coaching_service.load_profiles_from_supabase()
        if not profiles:
            raise HTTPException(status_code=400, detail="Aucun profil LinkedIn trouvé dans la base de données")

        background_tasks.add_task(process_profiles)
        return {
            "message": f"Traitement démarré pour {len(profiles)} profils LinkedIn",
            "profiles_found": len(profiles),
            "status": "processing",
            "note": "Le chunking et les embeddings sont en cours de création..."
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du démarrage du traitement: {str(e)}")

@router.post("/initialize")
<<<<<<< HEAD
async def initialize_system(background_tasks: BackgroundTasks):
=======
async def initialize_system(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
>>>>>>> 5e0de77 (Auth commit)
    try:
        profiles = career_coaching_service.load_profiles_from_supabase()
        chunks = career_coaching_service.load_chunks_from_supabase()

        if not profiles:
            raise HTTPException(status_code=400, detail="Aucun profil trouvé dans la table profileslinkedin")

        if not chunks:
            return {
                "message": "Aucun chunk trouvé. Utilisez /process-profiles d'abord pour créer les chunks.",
                "profiles_found": len(profiles),
                "chunks_found": 0,
                "next_step": "POST /process-profiles"
            }

        def create_index():
            try:
                success = career_coaching_service.build_index_from_supabase()
                if success:
                    print(f"✅ Index créé avec succès pour {len(profiles)} profils et {len(chunks)} chunks")
                else:
                    print("❌ Échec de la création de l'index")
            except Exception as e:
                print(f"❌ Erreur lors de la création de l'index: {e}")

        background_tasks.add_task(create_index)
        return {
            "message": f"Initialisation démarrée avec {len(profiles)} profils et {len(chunks)} chunks",
            "profilesLoaded": len(profiles),
            "chunksLoaded": len(chunks),
            "status": "building_index"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'initialisation: {str(e)}")

@router.post("/coaching")
<<<<<<< HEAD
async def coaching_session_with_rag(data: CareerCoachingRequest):
=======
async def coaching_session_with_rag(
    data: CareerCoachingRequest,
    current_user: dict = Depends(get_current_user)
):
>>>>>>> 5e0de77 (Auth commit)
    """Session de coaching utilisant le RAG sur les profils LinkedIn"""
    try:
        print(f"📥 Requête coaching reçue: {data}")
        
        # Vérification et chargement de l'index une seule fois
        if not career_coaching_service.index or not career_coaching_service.profile_map:
            print("⚠️ Système non initialisé, tentative de chargement...")
            if not career_coaching_service.load_index():
                print("❌ Impossible de charger l'index")
                raise HTTPException(
                    status_code=503, 
                    detail="Système non initialisé. Utilisez /process-profiles puis /initialize"
                )
            print("✅ Index chargé avec succès")

        # Génération du plan de carrière
        if data.useRAG:
            print("🔍 Utilisation du RAG pour enrichir l'analyse")
            rag_query = f"{data.goal} {data.sector} {' '.join(data.skills)}"
            rag_context = career_coaching_service.get_rag_context(rag_query, top_k=8)
            
            response_text = llm_generate_career_plan_with_rag(
                goal=data.goal, 
                skills=data.skills, 
                sector=data.sector, 
                rag_context=rag_context
            )
            
            # Parsing de la réponse JSON
            cleaned_output = response_text.strip().removeprefix("```json").removesuffix("```").strip()
            try:
                plan_data = json.loads(cleaned_output)
            except json.JSONDecodeError as e:
                print(f"⚠️ Erreur parsing JSON: {e}")
                plan_data = {
                    "plan_carriere": {"description": response_text},
                    "formations": [],
                    "negociation": {"conseils": [response_text]}
                }

            # Enrichissement avec insights LinkedIn
            insights = career_coaching_service.get_career_insights(data.goal, data.skills, data.sector)
            enriched_response = {
                "objectif": data.goal,
                "competences": data.skills,
                "secteur": data.sector,
                "rag_used": True,
                "profiles_analyzed": insights.get("profiles_analyzed", 0),
                "linkedin_insights": insights,
                **plan_data
            }
        else:
            print("📊 Analyse classique sans RAG")
            response_text = llm_generate_career_plan_with_rag(
                goal=data.goal, 
                skills=data.skills, 
                sector=data.sector, 
                rag_context=""
            )
            
            cleaned_output = response_text.strip().removeprefix("```json").removesuffix("```").strip()
            try:
                plan_data = json.loads(cleaned_output)
            except json.JSONDecodeError as e:
                print(f"⚠️ Erreur parsing JSON: {e}")
                plan_data = {
                    "plan_carriere": {"description": response_text},
                    "formations": [],
                    "negociation": {"conseils": [response_text]}
                }
                
            enriched_response = {
                "objectif": data.goal,
                "competences": data.skills,
                "secteur": data.sector,
                "rag_used": False,
                **plan_data
            }

        # Sauvegarde de la session
        try:
            session_id = career_coaching_service.save_coaching_session(
                data.user_id, data.goal, data.skills, data.sector, enriched_response
            )
            enriched_response["session_id"] = session_id
            print(f"✅ Session sauvegardée avec l'ID: {session_id}")
            
            ui_payload = _to_ui_payload(enriched_response)

            return {
               "success": True,
    "session_id": session_id,
    "message": "Session de coaching générée et sauvegardée avec succès",
    "data": ui_payload
               }

            
        except Exception as e:
            print(f"⚠️ Erreur lors de la sauvegarde de la session: {e}")
            enriched_response["session_id"] = None
            enriched_response["save_error"] = str(e)
            
            ui_payload = _to_ui_payload(enriched_response)
            ui_payload["session_id"] = None
            ui_payload["save_error"] = str(e)

            return {
    "success": True,
    "session_id": None,
    "message": "Session générée mais non sauvegardée",
    "data": ui_payload,
    "warning": f"Erreur de sauvegarde: {str(e)}"
}


    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur générale dans coaching_session_with_rag: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors de la génération du plan: {str(e)}"
        )

@router.post("/search-profiles")
<<<<<<< HEAD
async def search_similar_profiles(data: ProfileSearchRequest):
=======
async def search_similar_profiles(
    data: ProfileSearchRequest,
    current_user: dict = Depends(get_current_user)
):
>>>>>>> 5e0de77 (Auth commit)
    try:
        if not career_coaching_service.index or not career_coaching_service.profile_map:
            raise HTTPException(status_code=503, detail="Système non initialisé. Utilisez /process-profiles puis /initialize")

        results = career_coaching_service.search_similar_profiles(data.query, data.topK)
        return {
            "query": data.query,
            "resultsCount": len(results),
            "profiles": [
                {
                    "id": p.profile_id,
                    "nom": p.nom,
                    "titre": p.titre,
                    "formation": p.formation,
                    "url": p.url,
                    "score": p.score
                } for p in results
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la recherche: {str(e)}")

@router.post("/rag-search")
<<<<<<< HEAD
async def rag_search_chunks(query: str, top_k: int = 5):
=======
async def rag_search_chunks(
    query: str,
    top_k: int = 5,
    current_user: dict = Depends(get_current_user)
):
>>>>>>> 5e0de77 (Auth commit)
    try:
        if not career_coaching_service.index or not career_coaching_service.chunk_map:
            raise HTTPException(status_code=503, detail="Système non initialisé")

        chunks = career_coaching_service.search_relevant_chunks(query, top_k)
        rag_context = career_coaching_service.get_rag_context(query, top_k)
        return {
            "query": query,
            "chunks_found": len(chunks),
            "rag_context": rag_context,
            "chunks": [
                {
                    "chunk_id": c.chunk_id,
                    "profile_nom": c.nom,
                    "profile_titre": c.titre,
                    "section": c.section,
                    "content_preview": c.content[:150] + "...",
                    "score": c.score
                } for c in chunks
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la recherche RAG: {str(e)}")

@router.post("/analyze-skills")
<<<<<<< HEAD
async def analyze_skills_gap(data: SkillAnalysisRequest):
=======
async def analyze_skills_gap(
    data: SkillAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
>>>>>>> 5e0de77 (Auth commit)
    try:
        if not career_coaching_service.index or not career_coaching_service.profile_map:
            raise HTTPException(status_code=503, detail="Système non initialisé")

        skills_query = " ".join(data.skills)
        profiles = career_coaching_service.search_similar_profiles(skills_query, top_k=20)
        chunks = career_coaching_service.search_relevant_chunks(skills_query, top_k=10)

        analysis = {
            "skills": data.skills,
            "sector": data.sector,
            "profiles_analyzed": len(profiles),
            "top_matching_profiles": [
                {"nom": p.nom, "titre": p.titre, "score": p.score, "url": p.url}
                for p in profiles[:5]
            ],
            "relevant_content": [
                {"content": c.content[:200] + "...", "nom": c.nom, "titre": c.titre,
                 "section": c.section, "score": c.score}
                for c in chunks[:3]
            ],
            "market_demand": {
                "total_profiles": len(profiles),
                "avg_score": (sum(p.score for p in profiles) / len(profiles)) if profiles else 0,
                "demand_level": "Élevé" if len(profiles) > 10 else "Moyen" if len(profiles) > 5 else "Faible"
            }
        }
        return analysis

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse des compétences: {str(e)}")

@router.get("/insights/{sector}")
<<<<<<< HEAD
async def get_sector_insights(sector: str, limit: int = 10):
=======
async def get_sector_insights(
    sector: str,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
>>>>>>> 5e0de77 (Auth commit)
    try:
        if not career_coaching_service.index or not career_coaching_service.profile_map:
            raise HTTPException(status_code=503, detail="Système non initialisé")

        profiles = career_coaching_service.search_similar_profiles(sector, top_k=limit * 2)
        insights = career_coaching_service.get_career_insights("", [], sector)
        return {
            "sector": sector,
            "profilesAnalyzed": len(profiles),
            "topProfiles": insights.get("top_profiles", [])[:10],
            "relevantContent": insights.get("relevant_chunks", [])[:5],
            "sectorAnalysis": insights.get("sector_analysis", {})
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse du secteur: {str(e)}")

@router.post("/save-session")
<<<<<<< HEAD
async def save_coaching_session(data: SaveSessionRequest):
=======
async def save_coaching_session(
    data: SaveSessionRequest,
    current_user: dict = Depends(get_current_user)
):
>>>>>>> 5e0de77 (Auth commit)
    try:
        session_id = career_coaching_service.save_coaching_session(
            data.user_id, data.objectif, data.competences, data.secteur, data.plan_data
        )
        return {"message": "Session sauvegardée avec succès", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la sauvegarde: {str(e)}")

@router.get("/history/{user_id}")
<<<<<<< HEAD
async def get_coaching_history(user_id: int):
=======
async def get_coaching_history(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
>>>>>>> 5e0de77 (Auth commit)
    try:
        history = career_coaching_service.get_coaching_history(user_id)
        return {
            "user_id": user_id,
            "sessions_count": len(history),
            "sessions": [
                {
                    "id": s["id"],
                    "objectif": s["objectif"],
                    "competences": json.loads(s["competences"]) if s.get("competences") else [],
                    "secteur": s.get("secteur"),
                    "created_at": s.get("created_at"),
                    "plans_carriere": s.get("plans_carriere", []),
                    "formations": s.get("formations", []),
                    "negociations": s.get("negociations", [])
                } for s in history
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de l'historique: {str(e)}")
