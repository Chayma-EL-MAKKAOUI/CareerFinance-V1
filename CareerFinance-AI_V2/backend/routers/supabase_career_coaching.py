# routers/supabase_career_coaching.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from services.supabase_career_coaching_service import career_coaching_service
from services.careerPromt import generate_career_plan
import json

router = APIRouter()

@router.get("/")
async def supabase_career_coaching_documentation():
    """Documentation du système de coaching carrière avec Supabase"""
    return {
        "title": "Système de Coaching Carrière avec Supabase",
        "description": "API pour le coaching de carrière utilisant les données LinkedIn stockées dans Supabase",
        "version": "1.0.0",
        "endpoints": {
            "GET /api/supabase-career/status": "Vérifier le statut du système",
            "POST /api/supabase-career/initialize": "Initialiser le système (charger données + créer index)",
            "POST /api/supabase-career/coaching": "Générer un plan de carrière avec données LinkedIn",
            "POST /api/supabase-career/search-profiles": "Rechercher des profils LinkedIn similaires",
            "POST /api/supabase-career/analyze-skills": "Analyser les compétences vs marché LinkedIn",
            "GET /api/supabase-career/insights/{sector}": "Obtenir des insights sur un secteur",
            "POST /api/supabase-career/save-session": "Sauvegarder une session de coaching",
            "GET /api/supabase-career/history/{user_id}": "Récupérer l'historique des sessions"
        },
        "tables_utilisees": [
            "profileslinkedin - Profils LinkedIn scrapés",
            "profile_chunks - Chunks de contenu des profils avec embeddings",
            "coaching_sessions - Historique des sessions de coaching"
        ],
        "technology": "Supabase + FAISS + sentence-transformers + Gemini AI"
    }

class CareerCoachingRequest(BaseModel):
    user_id: int
    goal: str
    skills: List[str]
    sector: str
    useLinkedInData: bool = True

class ProfileSearchRequest(BaseModel):
    query: str
    topK: int = 10

class SkillAnalysisRequest(BaseModel):
    skills: List[str]
    sector: str

class SaveSessionRequest(BaseModel):
    user_id: int
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
async def get_system_status():
    """Vérifie le statut du système de coaching carrière"""
    try:
        # Vérifier si l'index est chargé
        index_exists = career_coaching_service.index is not None
        
        # Compter les profils et chunks
        profiles_count = len(career_coaching_service.profile_map) if career_coaching_service.profile_map else 0
        chunks_count = len(career_coaching_service.chunk_map) if career_coaching_service.chunk_map else 0
        
        # Essayer de charger l'index si nécessaire
        if not index_exists:
            try:
                if career_coaching_service.load_index():
                    index_exists = True
                    profiles_count = len(career_coaching_service.profile_map)
                    chunks_count = len(career_coaching_service.chunk_map)
                else:
                    return SystemStatusResponse(
                        isInitialized=False,
                        profilesCount=0,
                        chunksCount=0,
                        indexExists=False,
                        message="Index non trouvé. Utilisez /initialize pour créer l'index."
                    )
            except Exception as e:
                return SystemStatusResponse(
                    isInitialized=False,
                    profilesCount=0,
                    chunksCount=0,
                    indexExists=False,
                    message=f"Erreur lors du chargement de l'index: {str(e)}"
                )
        
        is_initialized = profiles_count > 0 and chunks_count > 0 and index_exists
        message = f"Système initialisé avec {profiles_count} profils et {chunks_count} chunks" if is_initialized else "Système non initialisé"
        
        return SystemStatusResponse(
            isInitialized=is_initialized,
            profilesCount=profiles_count,
            chunksCount=chunks_count,
            indexExists=index_exists,
            message=message
        )
        
    except Exception as e:
        return SystemStatusResponse(
            isInitialized=False,
            profilesCount=0,
            chunksCount=0,
            indexExists=False,
            message=f"Erreur lors de la vérification du statut: {str(e)}"
        )

@router.post("/initialize")
async def initialize_system(background_tasks: BackgroundTasks):
    """Initialise le système (charge les données et crée l'index)"""
    try:
        # Charger les données depuis Supabase
        profiles = career_coaching_service.load_profiles_from_supabase()
        chunks = career_coaching_service.load_chunks_from_supabase()
        
        if not profiles:
            raise HTTPException(
                status_code=400, 
                detail="Aucun profil trouvé dans la table profileslinkedin"
            )
        
        if not chunks:
            raise HTTPException(
                status_code=400, 
                detail="Aucun chunk trouvé dans la table profile_chunks"
            )
        
        # Créer l'index en arrière-plan
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
            "message": f"Initialisation démarrée avec {len(profiles)} profils et {len(chunks)} chunks. L'index est en cours de création...",
            "profilesLoaded": len(profiles),
            "chunksLoaded": len(chunks),
            "status": "in_progress"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'initialisation: {str(e)}"
        )

@router.post("/coaching")
async def generate_career_plan_with_supabase(data: CareerCoachingRequest):
    """Génère un plan de carrière avec les données LinkedIn de Supabase"""
    try:
        # Vérifier que le système est initialisé
        if not career_coaching_service.index or not career_coaching_service.profile_map:
            # Essayer de charger automatiquement
            try:
                if not career_coaching_service.load_index():
                    raise HTTPException(
                        status_code=503,
                        detail="Système non initialisé. Utilisez /initialize d'abord."
                    )
            except Exception:
                raise HTTPException(
                    status_code=503,
                    detail="Système non initialisé. Utilisez /initialize d'abord."
                )
        
        if data.useLinkedInData:
            # Obtenir des insights LinkedIn
            insights = career_coaching_service.get_career_insights(
                data.goal, data.skills, data.sector
            )
            
            # Générer le plan de carrière classique
            response_text = generate_career_plan(data.goal, data.skills, data.sector)
            cleaned_output = response_text.strip().removeprefix("```json").removesuffix("```").strip()
            plan_data = json.loads(cleaned_output)
            
            # Enrichir avec les données LinkedIn
            enriched_response = {
                "objectif": data.goal,
                "competences": data.skills,
                "secteur": data.sector,
                "linkedInDataUsed": True,
                "linkedInInsights": insights,
                **plan_data
            }
        else:
            # Utiliser seulement le service classique
            response_text = generate_career_plan(data.goal, data.skills, data.sector)
            cleaned_output = response_text.strip().removeprefix("```json").removesuffix("```").strip()
            plan_data = json.loads(cleaned_output)
            
            enriched_response = {
                "objectif": data.goal,
                "competences": data.skills,
                "secteur": data.sector,
                "linkedInDataUsed": False,
                **plan_data
            }
        
        # Sauvegarder la session
        try:
            session_id = career_coaching_service.save_coaching_session(
                data.user_id, data.goal, data.skills, data.sector, enriched_response
            )
            enriched_response["session_id"] = session_id
        except Exception as e:
            print(f"⚠️ Erreur lors de la sauvegarde de la session: {e}")
            enriched_response["session_id"] = None
        
        return enriched_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération du plan: {str(e)}"
        )

@router.post("/search-profiles")
async def search_similar_profiles(data: ProfileSearchRequest):
    """Recherche des profils LinkedIn similaires"""
    try:
        if not career_coaching_service.index or not career_coaching_service.profile_map:
            raise HTTPException(
                status_code=503,
                detail="Système non initialisé. Utilisez /initialize d'abord."
            )
        
        results = career_coaching_service.search_similar_profiles(
            data.query, data.topK
        )
        
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
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la recherche: {str(e)}"
        )

@router.post("/analyze-skills")
async def analyze_skills_gap(data: SkillAnalysisRequest):
    """Analyse les compétences par rapport au marché LinkedIn"""
    try:
        if not career_coaching_service.index or not career_coaching_service.profile_map:
            raise HTTPException(
                status_code=503,
                detail="Système non initialisé. Utilisez /initialize d'abord."
            )
        
        # Rechercher des profils avec ces compétences
        skills_query = " ".join(data.skills)
        profiles = career_coaching_service.search_similar_profiles(skills_query, top_k=20)
        
        # Analyser les chunks pertinents
        chunks = career_coaching_service.search_relevant_chunks(skills_query, top_k=10)
        
        analysis = {
            "skills": data.skills,
            "sector": data.sector,
            "profiles_analyzed": len(profiles),
            "top_matching_profiles": [
                {
                    "nom": p.nom,
                    "titre": p.titre,
                    "score": p.score,
                    "url": p.url
                } for p in profiles[:5]
            ],
            "relevant_content": [
                {
                    "content": c.content[:200] + "...",
                    "nom": c.nom,
                    "titre": c.titre,
                    "section": c.section,
                    "score": c.score
                } for c in chunks[:3]
            ],
            "market_demand": {
                "total_profiles": len(profiles),
                "avg_score": sum(p.score for p in profiles) / len(profiles) if profiles else 0,
                "demand_level": "Élevé" if len(profiles) > 10 else "Moyen" if len(profiles) > 5 else "Faible"
            }
        }
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse des compétences: {str(e)}"
        )

@router.get("/insights/{sector}")
async def get_sector_insights(sector: str, limit: int = 10):
    """Obtient des insights sur un secteur spécifique"""
    try:
        if not career_coaching_service.index or not career_coaching_service.profile_map:
            raise HTTPException(
                status_code=503,
                detail="Système non initialisé. Utilisez /initialize d'abord."
            )
        
        # Rechercher des profils dans le secteur
        profiles = career_coaching_service.search_similar_profiles(sector, top_k=limit * 2)
        
        # Analyser les données
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
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse du secteur: {str(e)}"
        )

@router.post("/save-session")
async def save_coaching_session(data: SaveSessionRequest):
    """Sauvegarde une session de coaching"""
    try:
        session_id = career_coaching_service.save_coaching_session(
            data.user_id, data.objectif, data.competences, data.secteur, data.plan_data
        )
        
        return {
            "message": "Session sauvegardée avec succès",
            "session_id": session_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la sauvegarde: {str(e)}"
        )

@router.get("/history/{user_id}")
async def get_coaching_history(user_id: int):
    """Récupère l'historique des sessions de coaching d'un utilisateur"""
    try:
        history = career_coaching_service.get_coaching_history(user_id)
        
        return {
            "user_id": user_id,
            "sessions_count": len(history),
            "sessions": [
                {
                    "id": session["id"],
                    "objectif": session["objectif"],
                    "competences": json.loads(session["competences"]) if session["competences"] else [],
                    "secteur": session["secteur"],
                    "created_at": session["created_at"]
                } for session in history
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération de l'historique: {str(e)}"
        )
