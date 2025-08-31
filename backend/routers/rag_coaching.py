#routers.rag_coaching.py
<<<<<<< HEAD
from fastapi import APIRouter, HTTPException, BackgroundTasks
=======
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
>>>>>>> 5e0de77 (Auth commit)
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from services.enhanced_career_service import enhanced_career_service
from services.rag_service import linkedin_rag
<<<<<<< HEAD
=======
from dependencies.auth_dependencies import get_current_user
>>>>>>> 5e0de77 (Auth commit)
import json

router = APIRouter()

@router.get("/")
async def rag_documentation():
    """Documentation du système RAG LinkedIn"""
    return {
        "title": "Système RAG LinkedIn pour Coaching de Carrière",
        "description": "API pour utiliser les données LinkedIn dans le coaching de carrière",
        "version": "1.0.0",
        "endpoints": {
            "GET /api/rag/status": "Vérifier le statut du système RAG",
            "POST /api/rag/initialize": "Initialiser le système RAG (charger données + créer index)",
            "POST /api/rag/enhanced-coaching": "Générer un plan de carrière enrichi avec LinkedIn",
            "POST /api/rag/search-profiles": "Rechercher des profils LinkedIn similaires",
            "POST /api/rag/analyze-skills": "Analyser les compétences vs marché LinkedIn",
            "GET /api/rag/insights/{sector}": "Obtenir des insights sur un secteur"
        },
        "setup_instructions": [
            "1. Installer les dépendances: python install_rag.py",
            "2. Placer le fichier linkedin_scraped_fixed.json dans backend/data/",
            "3. Initialiser le système: POST /api/rag/initialize",
            "4. Utiliser les endpoints enrichis"
        ],
        "data_source": "Fichier JSON avec profils LinkedIn scrapés",
        "technology": "RAG avec sentence-transformers + FAISS + Gemini AI"
    }

class EnhancedCoachingRequest(BaseModel):
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

class RAGStatusResponse(BaseModel):
    isInitialized: bool
    profilesCount: int
    indexExists: bool
    message: str

@router.get("/status", response_model=RAGStatusResponse)
<<<<<<< HEAD
async def get_rag_status():
=======
async def get_rag_status(current_user: dict = Depends(get_current_user)):
>>>>>>> 5e0de77 (Auth commit)
    """Vérifie le statut du système RAG"""
    try:
        # Vérifier si les données sont chargées
        profiles_count = len(linkedin_rag.profiles) if linkedin_rag.profiles else 0
        index_exists = linkedin_rag.index is not None
        
        # Essayer de charger les données si elles ne sont pas déjà chargées
        if profiles_count == 0:
            try:
                linkedin_rag.load_linkedin_data()
                profiles_count = len(linkedin_rag.profiles)
            except FileNotFoundError:
                return RAGStatusResponse(
                    isInitialized=False,
                    profilesCount=0,
                    indexExists=False,
                    message="Fichier LinkedIn non trouvé. Veuillez placer le fichier linkedin_scraped_fixed.json dans backend/data/"
                )
            except Exception as e:
                return RAGStatusResponse(
                    isInitialized=False,
                    profilesCount=0,
                    indexExists=False,
                    message=f"Erreur lors du chargement des données: {str(e)}"
                )
        
        # Vérifier l'index
        if not index_exists:
            try:
                if not linkedin_rag.load_index():
                    # L'index n'existe pas, il faut le créer
                    return RAGStatusResponse(
                        isInitialized=False,
                        profilesCount=profiles_count,
                        indexExists=False,
                        message="Index non trouvé. Utilisez /initialize pour créer l'index."
                    )
                else:
                    index_exists = True
            except Exception as e:
                return RAGStatusResponse(
                    isInitialized=False,
                    profilesCount=profiles_count,
                    indexExists=False,
                    message=f"Erreur lors du chargement de l'index: {str(e)}"
                )
        
        is_initialized = profiles_count > 0 and index_exists
        message = f"RAG initialisé avec {profiles_count} profils" if is_initialized else "RAG non initialisé"
        
        return RAGStatusResponse(
            isInitialized=is_initialized,
            profilesCount=profiles_count,
            indexExists=index_exists,
            message=message
        )
        
    except Exception as e:
        return RAGStatusResponse(
            isInitialized=False,
            profilesCount=0,
            indexExists=False,
            message=f"Erreur lors de la vérification du statut: {str(e)}"
        )

@router.post("/initialize")
<<<<<<< HEAD
async def initialize_rag(background_tasks: BackgroundTasks):
=======
async def initialize_rag(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
>>>>>>> 5e0de77 (Auth commit)
    """Initialise le système RAG (charge les données et crée l'index)"""
    try:
        # Charger les données LinkedIn
        profiles = linkedin_rag.load_linkedin_data()
        
        if not profiles:
            raise HTTPException(
                status_code=400, 
                detail="Aucun profil trouvé dans le fichier LinkedIn"
            )
        
        # Créer l'index en arrière-plan pour ne pas bloquer la requête
        def create_index():
            try:
                linkedin_rag.build_index()
                linkedin_rag.save_index()
                print(f"✅ Index RAG créé avec succès pour {len(profiles)} profils")
            except Exception as e:
                print(f"❌ Erreur lors de la création de l'index: {e}")
        
        background_tasks.add_task(create_index)
        
        return {
            "message": f"Initialisation démarrée avec {len(profiles)} profils. L'index est en cours de création...",
            "profilesLoaded": len(profiles),
            "status": "in_progress"
        }
        
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Fichier LinkedIn non trouvé. Veuillez placer le fichier linkedin_scraped_fixed.json dans backend/data/"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'initialisation: {str(e)}"
        )

@router.post("/enhanced-coaching")
<<<<<<< HEAD
async def generate_enhanced_career_plan(data: EnhancedCoachingRequest):
=======
async def generate_enhanced_career_plan(
    data: EnhancedCoachingRequest,
    current_user: dict = Depends(get_current_user)
):
>>>>>>> 5e0de77 (Auth commit)
    """Génère un plan de carrière enrichi avec les données LinkedIn"""
    try:
        # Vérifier que le RAG est initialisé
        if not linkedin_rag.profiles or not linkedin_rag.index:
            # Essayer de charger automatiquement
            try:
                linkedin_rag.load_linkedin_data()
                if not linkedin_rag.load_index():
                    linkedin_rag.build_index()
            except Exception:
                raise HTTPException(
                    status_code=503,
                    detail="Système RAG non initialisé. Utilisez /initialize d'abord."
                )
        
        if data.useLinkedInData:
            # Utiliser le service enrichi avec LinkedIn
            response = enhanced_career_service.generate_enhanced_career_plan(
                data.goal, data.skills, data.sector
            )
        else:
            # Fallback vers le service classique
            from services.careerPromt import generate_career_plan
            response_text = generate_career_plan(data.goal, data.skills, data.sector)
            cleaned_output = response_text.strip().removeprefix("```json").removesuffix("```").strip()
            response = json.loads(cleaned_output)
        
        # Ajouter les métadonnées de la requête
        enriched_response = {
            "objectif": data.goal,
            "competences": data.skills,
            "secteur": data.sector,
            "linkedInDataUsed": data.useLinkedInData,
            **response
        }
        
        return enriched_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération du plan enrichi: {str(e)}"
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
    """Recherche des profils LinkedIn similaires"""
    try:
        if not linkedin_rag.profiles or not linkedin_rag.index:
            raise HTTPException(
                status_code=503,
                detail="Système RAG non initialisé. Utilisez /initialize d'abord."
            )
        
        results = enhanced_career_service.search_similar_professionals(
            data.query, data.topK
        )
        
        return {
            "query": data.query,
            "resultsCount": len(results),
            "profiles": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la recherche: {str(e)}"
        )

@router.post("/analyze-skills")
<<<<<<< HEAD
async def analyze_skills_gap(data: SkillAnalysisRequest):
=======
async def analyze_skills_gap(
    data: SkillAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
>>>>>>> 5e0de77 (Auth commit)
    """Analyse les compétences par rapport au marché LinkedIn"""
    try:
        if not linkedin_rag.profiles or not linkedin_rag.index:
            raise HTTPException(
                status_code=503,
                detail="Système RAG non initialisé. Utilisez /initialize d'abord."
            )
        
        analysis = enhanced_career_service.get_skill_analysis(
            data.skills, data.sector
        )
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse des compétences: {str(e)}"
        )

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
    """Obtient des insights sur un secteur spécifique"""
    try:
        if not linkedin_rag.profiles or not linkedin_rag.index:
            raise HTTPException(
                status_code=503,
                detail="Système RAG non initialisé. Utilisez /initialize d'abord."
            )
        
        # Rechercher des profils dans le secteur
        results = linkedin_rag.search_profiles(sector, top_k=limit * 2)
        
        # Analyser les données
        insights = linkedin_rag.get_career_insights("", [], sector)
        
        return {
            "sector": sector,
            "profilesAnalyzed": len(results),
            "topSkills": insights.get('competences_populaires', [])[:10],
            "topCompanies": insights.get('entreprises_cibles', [])[:10],
            "commonTitles": insights.get('parcours_types', [])[:10],
            "locations": insights.get('localisations', [])[:5]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse du secteur: {str(e)}"
        )
