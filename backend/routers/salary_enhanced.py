# routers/salary_enhanced.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from typing import List, Optional, Any, Dict

from services.supabase_salary_rag_service import supabase_salary_rag

router = APIRouter()

class Recommendation(BaseModel):
    title: str
    description: str
    priority: str

class Trend(BaseModel):
    title: str
    detail: str

class Step(BaseModel):
    numero: int
    contenu: str

class SalaryRequest(BaseModel):
    jobTitle: str
    location: str
    experienceYears: int
    currentSalary: int
    
    @validator('jobTitle')
    def validate_job_title(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Le titre du poste doit contenir au moins 2 caractères')
        return v.strip()
    
    @validator('location')
    def validate_location(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('La localisation doit contenir au moins 2 caractères')
        return v.strip()
    
    @validator('experienceYears')
    def validate_experience_years(cls, v):
        if v < 0 or v > 50:
            raise ValueError('Les années d\'expérience doivent être entre 0 et 50')
        return v
    
    @validator('currentSalary')
    def validate_current_salary(cls, v):
        if v < 1000 or v > 1000000:
            raise ValueError('Le salaire doit être entre 1 000 et 1 000 000 MAD/mois')
        return v

class SalaryResponse(BaseModel):
    moyenne: int
    ecart: int
    ecart_pourcent: float
    minimum: int
    maximum: int
    percentile: int
    recommandations: List[Recommendation]
    tendances: List[Trend]
    salaireActuel: int
    jobTitle: str
    location: str
    experienceYears: int
    etapes: List[Step]
    dataQuality: Optional[dict] = None
    marketUsed: Optional[str] = None

@router.get("/")
async def salary_enhanced_documentation():
    """Documentation de l'API d'analyse salariale"""
    return {
        "title": "Système d'Analyse Salariale Intelligent (Supabase + Gemini)",
        "description": "Analyse salariale basée sur RAG avec support multi-marchés",
        "unit": "MAD/mois",
        "version": "3.0.0",
        "features": [
            "Déduction automatique ville/pays depuis localisation",
            "Support multi-marchés (Maghreb, Européen, Nord-Américain, etc.)",
            "Validation intelligente des données",
            "Chunking et embedding automatique",
            "RAG avec recherche contextuelle progressive",
            "Analyse par Gemini AI"
        ],
        "supported_markets": [
            "Marché Maghreb", "Marché Européen", "Marché Nord-Américain", 
            "Marché Anglo-Saxon", "Marché Global"
        ],
        "endpoints": {
            "POST /api/salary-enhanced/analyze": "Analyse salariale complète",
            "POST /api/salary-enhanced/dataset/backfill": "Créer chunks/embeddings depuis salary_dataset",
            "POST /api/salary-enhanced/dataset/reload": "Recharger l'index FAISS",
            "GET  /api/salary-enhanced/dataset/status": "Statut du système RAG",
            "POST /api/salary-enhanced/dataset/validate": "Valider données existantes",
        },
    }

@router.post("/analyze", response_model=SalaryResponse)
async def analyze_salary(data: SalaryRequest):
    """
    Analyse salariale intelligente avec RAG multi-marchés
    
    - Devine automatiquement le pays depuis la ville
    - Identifie le marché économique pertinent  
    - Valide la cohérence des données
    - Utilise RAG pour trouver des profils similaires
    - Retourne analyse complète avec Gemini AI
    """
    try:
        # 1. Initialisation et seed si nécessaire
        init_result = supabase_salary_rag.seed_if_needed()
        
        # 2. Stockage de l'entrée utilisateur avec validation intelligente
        row_id, status = supabase_salary_rag.store_user_entry(
            job_title=data.jobTitle,
            location=data.location,
            experience_years=data.experienceYears,
            current_salary=float(data.currentSalary),
            user_id=1,  # À remplacer par l'ID utilisateur authentifié
        )
        
        # 3. Chunking et embedding uniquement si entrée valide
        chunks_created = 0
        if status.lower().startswith("valide"):
            try:
                supabase_salary_rag.chunk_row(row_id)
                chunks_created = supabase_salary_rag.embed_new_chunks()
                supabase_salary_rag.build_or_load_faiss()
            except Exception as e:
                print(f"Avertissement chunking/embedding: {str(e)}")

        # 4. Analyse complète avec Gemini
        analysis_result: Dict[str, Any] = supabase_salary_rag.analyze_with_gemini(
            data.jobTitle, data.location, data.experienceYears, data.currentSalary
        )
        
        # 5. Enrichissement de la réponse
        analysis_result.update({
            "salaireActuel": data.currentSalary,
            "jobTitle": data.jobTitle,
            "location": data.location,
            "experienceYears": data.experienceYears,
        })
        
        # Ajout métadonnées techniques si pas présentes
        if "dataQuality" not in analysis_result:
            analysis_result["dataQuality"] = {
                "source": "supabase",
                "unit": "MAD/mois",
                "entryStatus": status,
                "rowId": row_id,
                "chunksCreated": chunks_created
            }
        else:
            analysis_result["dataQuality"]["entryStatus"] = status
            analysis_result["dataQuality"]["rowId"] = row_id
            analysis_result["dataQuality"]["chunksCreated"] = chunks_created
        
        return analysis_result
        
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Données invalides: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur analyse salariale: {str(e)}")

@router.post("/dataset/backfill")
async def dataset_backfill():
    """
    Crée les chunks et embeddings depuis salary_dataset
    Traite uniquement les entrées avec status='valide'
    """
    try:
        # Création des chunks
        created_result = supabase_salary_rag.backfill_chunks_from_salary_dataset(only_status="valide")
        
        # Création des embeddings
        embedded_count = supabase_salary_rag.embed_new_chunks()
        
        # Reconstruction FAISS
        faiss_ok = supabase_salary_rag.build_or_load_faiss()
        
        return {
            "success": True,
            "chunks_created": created_result.get("created", 0),
            "rows_scanned": created_result.get("scanned", 0),
            "embeddings_created": embedded_count,
            "faiss_rebuilt": faiss_ok,
            "status": supabase_salary_rag.status()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur backfill: {str(e)}")

@router.post("/dataset/reload")
async def dataset_reload():
    """
    Recharge l'index FAISS avec les dernières données
    """
    try:
        # Embedding des nouveaux chunks
        embedded_count = supabase_salary_rag.embed_new_chunks()
        
        # Reconstruction FAISS
        faiss_ok = supabase_salary_rag.build_or_load_faiss()
        
        system_status = supabase_salary_rag.status()
        
        return {
            "success": faiss_ok,
            "embeddings_created": embedded_count,
            **system_status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur reload: {str(e)}")

@router.get("/dataset/status")
async def dataset_status():
    """
    Retourne le statut détaillé du système RAG
    """
    try:
        status = supabase_salary_rag.status()
        
        # Statistiques additionnelles de la DB
        try:
            dataset_count = len(supabase_salary_rag.supabase.table("salary_dataset").select("id").execute().data or [])
            chunks_count = len(supabase_salary_rag.supabase.table("salary_chunks").select("id").execute().data or [])
            valid_count = len(supabase_salary_rag.supabase.table("salary_dataset").select("id").ilike("status", "valide%").execute().data or [])
        except:
            dataset_count = chunks_count = valid_count = 0
            
        status.update({
            "database": {
                "salary_dataset_rows": dataset_count,
                "salary_chunks_rows": chunks_count, 
                "valid_entries": valid_count,
                "invalid_entries": dataset_count - valid_count
            },
            "system_ready": status.get("faissLoaded", False) and status.get("rows", 0) > 0
        })
        
        return status
        
    except Exception as e:
        return {"error": str(e), "system_ready": False}

@router.post("/dataset/validate")
async def validate_dataset():
    """
    Revalide les statuts des entrées existantes dans salary_dataset
    Utile après changement des règles de validation
    """
    try:
        # Cette fonction nécessiterait d'être implémentée dans le service
        # Pour l'instant, on retourne un placeholder
        return {
            "message": "Fonction de revalidation à implémenter",
            "status": "pending"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur validation: {str(e)}")

@router.get("/markets")
async def get_supported_markets():
    """
    Retourne la liste des marchés et pays supportés
    """
    from services.supabase_salary_rag_service import CITIES_DATABASE, get_market_from_country
    
    markets_info = {}
    for country, cities in CITIES_DATABASE.items():
        market = get_market_from_country(country)
        if market not in markets_info:
            markets_info[market] = {"countries": [], "sample_cities": []}
        markets_info[market]["countries"].append(country)
        markets_info[market]["sample_cities"].extend(list(cities)[:5])  # 5 villes exemples
    
    return {
        "supported_markets": markets_info,
        "total_countries": len(CITIES_DATABASE),
        "total_cities": sum(len(cities) for cities in CITIES_DATABASE.values())
    }

@router.post("/debug/search")
async def debug_search_process(data: SalaryRequest):
    """
    Endpoint de debug pour tracer le processus de recherche
    Utile pour comprendre pourquoi les résultats sont identiques
    """
    try:
        debug_info = supabase_salary_rag.debug_search_process(
            data.jobTitle, data.location, data.experienceYears
        )
        return debug_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur debug: {str(e)}")