# routers/salary_enhanced.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from services.enhanced_salary_service import enhanced_salary_service
from services.rag_service import linkedin_rag
# ⬇️ nouveau service Supabase
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
    useLinkedInData: Optional[bool] = True

class SalaryBenchmarkRequest(BaseModel):
    jobTitle: str
    location: str
    experienceYears: int

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
    linkedinInsights: Optional[dict] = None
    dataQuality: Optional[dict] = None
    marketUsed: Optional[str] = None  # ⬅️ renvoie le marché utilisé

@router.get("/")
async def salary_enhanced_documentation():
    return {
        "title": "Système d'Analyse Salariale (LinkedIn + Dataset Supabase)",
        "unit": "MAD/mois",
        "version": "2.0.0",
        "endpoints": {
            "POST /api/salary-enhanced/analyze": "Analyse salariale enrichie",
            "POST /api/salary-enhanced/benchmarks": "Recherche de benchmarks (LinkedIn)",
            "GET /api/salary-enhanced/insights/{job_title}": "Insights salariaux",
            "GET /api/salary-enhanced/dataset/status": "Statut dataset salarial",
            "POST /api/salary-enhanced/dataset/reload": "Recharger FAISS à partir de Supabase",
        },
    }

@router.post("/analyze", response_model=SalaryResponse)
async def analyze_salary_enhanced(data: SalaryRequest):
    try:
        # 1) Analyse dataset Supabase + enregistrement utilisateur (+chunk+embedding)
        ds = supabase_salary_rag.analyze_and_upsert(
            job_title=data.jobTitle,
            location=data.location,
            experience_years=data.experienceYears,
            current_salary_mad=data.currentSalary,
            user_id=1,
        )

        # 2) Calcul “frontend-ready” (moyenne, écart, min/max, percentile…) à partir des stats
        stats = ds["stats"] or {}
        mean_val = int(round(stats.get("mean", data.currentSalary)))
        minimum = int(round(stats.get("min", mean_val)))
        maximum = int(round(stats.get("max", mean_val)))
        # écart utilisateur
        ecart = int(data.currentSalary - mean_val)
        ecart_pourcent = float((data.currentSalary - mean_val) / mean_val * 100.0) if mean_val else 0.0
        # percentile approx via position vs p25/p50/p75
        p50 = stats.get("p50", mean_val)
        if data.currentSalary <= stats.get("p25", p50):
            percentile = 25
        elif data.currentSalary <= p50:
            percentile = 50
        elif data.currentSalary <= stats.get("p75", p50):
            percentile = 75
        else:
            percentile = 90

        # 3) Reste de ton service “enhanced” (recommandations, tendances, étapes)
        enhanced = enhanced_salary_service.generate_enhanced_salary_analysis(
            data.jobTitle, data.location, data.experienceYears, data.currentSalary
        )

        return {
            **enhanced,
            "moyenne": mean_val,
            "ecart": ecart,
            "ecart_pourcent": ecart_pourcent,
            "minimum": minimum,
            "maximum": maximum,
            "percentile": percentile,
            "salaireActuel": data.currentSalary,
            "jobTitle": data.jobTitle,
            "location": data.location,
            "experienceYears": data.experienceYears,
            "dataQuality": ds.get("dataQuality"),
            "marketUsed": ds.get("marketUsed"),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur analyse salariale: {str(e)}")

@router.post("/benchmarks")
async def get_salary_benchmarks(data: SalaryBenchmarkRequest):
    try:
        if not linkedin_rag.profiles or not linkedin_rag.index:
            raise HTTPException(status_code=503, detail="RAG LinkedIn non initialisé.")
        benchmarks = enhanced_salary_service.search_salary_benchmarks(
            data.jobTitle, data.location, data.experienceYears
        )
        return {
            "jobTitle": data.jobTitle,
            "location": data.location,
            "experienceYears": data.experienceYears,
            "benchmarks": benchmarks["benchmarks"],
            "salaryEstimates": benchmarks["salary_estimates"],
            "totalProfiles": benchmarks["total_profiles"],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur benchmarks: {str(e)}")

@router.get("/dataset/status")
async def salary_dataset_status():
    return supabase_salary_rag.status()

@router.post("/dataset/reload")
async def salary_dataset_reload():
    try:
        # encode les chunks sans embedding + rebuild FAISS
        supabase_salary_rag.embed_new_chunks()
        ok = supabase_salary_rag.build_or_load_faiss()
        return {"ok": ok, **supabase_salary_rag.status()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reload error: {str(e)}")
