# app/services/enhanced_salary_service.py
from typing import List, Dict, Any
import json
import numpy as np

from services.gemini import call_gemini_api
from services.rag_service import linkedin_rag
from services.salary_rag import salary_rag, years_to_level


class EnhancedSalaryService:
    """Service d'analyse salariale enrichi (LinkedIn RAG + dataset salarial mensuel MAD)."""

    def __init__(self):
        self.rag_service = linkedin_rag
        self.salary_rag = salary_rag

    def generate_enhanced_salary_analysis(
        self, job_title: str, location: str, experience_years: int, current_salary: int
    ) -> Dict[str, Any]:
        # 1) Insights LinkedIn (si init)
        linkedin_insights = {}
        try:
            linkedin_insights = self.rag_service.get_salary_insights(job_title, location, experience_years)
        except Exception:
            linkedin_insights = {
                "profiles_similaires": [],
                "total_profiles": 0,
                "competences_demandees": [],
                "entreprises_qui_recrutent": [],
                "titres_similaires": [],
                "localisations_alternatives": [],
                "niveaux_experience": {},
                "secteurs_connexes": [],
            }

        # 2) Dataset salarial (RAG tabulaire)
        ds_matches = self.salary_rag.search(job_title, location, experience_years, top_k=200)
        ds_stats = self.salary_rag.aggregate(ds_matches)

        # 3) Estimation finale (dataset prioritaire si suffisant)
        if ds_stats.get("count", 0) >= 12:
            estimates = {
                "estimated_min": int(ds_stats["p25"]),
                "estimated_max": int(ds_stats["p75"]),
                "estimated_avg": int(ds_stats["median"]),
                "confidence_level": min(1.0, ds_stats["count"] / 200),
                "profiles_analyzed": int(ds_stats["count"]),
                "experience_level": years_to_level(experience_years),
                "source": "salary_dataset_mad_per_month",
            }
            # percentile approx
            rng = max(1.0, ds_stats["max"] - ds_stats["min"])
            percentile = int(np.clip((current_salary - ds_stats["min"]) / rng * 100, 0, 100))
        else:
            estimates = self._estimate_salaries_from_profiles(
                linkedin_insights.get("profiles_similaires", []), job_title, experience_years
            )
            percentile = 50

        # 4) Prompt LLM (cohérent MAD/mois)
        prompt = self._build_enhanced_salary_prompt_with_dataset(
            job_title, location, experience_years, current_salary,
            linkedin_insights, estimates, ds_stats if ds_stats.get("count", 0) > 0 else None, percentile
        )

        # 5) Appel Gemini
        gemini_response = call_gemini_api(prompt)
        cleaned = gemini_response.strip().removeprefix("```json").removesuffix("```").strip()
        salary_analysis = json.loads(cleaned)

        # 6) Enrichissement
        out = self._enrich_salary_analysis(salary_analysis, linkedin_insights, estimates)
        out["percentile"] = percentile
        out["dataQuality"] = {
            **out.get("dataQuality", {}),
            "salaryDatasetCount": ds_stats.get("count", 0),
            "salaryDatasetSource": self.salary_rag.data_path,
            "unit": "MAD/mois",
        }
        return out

    # ---------- Fallback (ton code existant, inchangé) ----------
    def _estimate_salaries_from_profiles(self, profiles: List[Dict[str, Any]], job_title: str, experience_years: int) -> Dict[str, Any]:
        salary_ranges = {
            'développeur': {'junior': (8000, 15000), 'intermediate': (15000, 25000), 'senior': (25000, 40000), 'expert': (40000, 60000)},
            'developer':    {'junior': (8000, 15000), 'intermediate': (15000, 25000), 'senior': (25000, 40000), 'expert': (40000, 60000)},
            'ingénieur':    {'junior': (10000, 18000), 'intermediate': (18000, 30000), 'senior': (30000, 45000), 'expert': (45000, 70000)},
            'manager':      {'junior': (20000, 30000), 'intermediate': (30000, 45000), 'senior': (45000, 65000), 'expert': (65000, 100000)},
            'chef':         {'junior': (18000, 28000), 'intermediate': (28000, 40000), 'senior': (40000, 60000), 'expert': (60000, 90000)},
            'directeur':    {'junior': (40000, 60000), 'intermediate': (60000, 80000), 'senior': (80000, 120000), 'expert': (120000, 200000)},
            'comptable':    {'junior': (6000, 12000), 'intermediate': (12000, 20000), 'senior': (20000, 35000), 'expert': (35000, 50000)},
            'analyste':     {'junior': (10000, 18000), 'intermediate': (18000, 28000), 'senior': (28000, 45000), 'expert': (45000, 70000)},
            'commercial':   {'junior': (8000, 15000), 'intermediate': (15000, 25000), 'senior': (25000, 40000), 'expert': (40000, 65000)},
            'marketing':    {'junior': (8000, 16000), 'intermediate': (16000, 26000), 'senior': (26000, 42000), 'expert': (42000, 65000)},
        }
        if experience_years <= 2: level = 'junior'
        elif experience_years <= 5: level = 'intermediate'
        elif experience_years <= 10: level = 'senior'
        else: level = 'expert'
        job_lower = job_title.lower()
        salary_range = None
        for key, ranges in salary_ranges.items():
            if key in job_lower:
                salary_range = ranges.get(level, ranges['intermediate'])
                break
        if not salary_range:
            default_ranges = {'junior': (8000, 15000), 'intermediate': (15000, 25000), 'senior': (25000, 40000), 'expert': (40000, 65000)}
            salary_range = default_ranges[level]
        min_salary, max_salary = salary_range
        avg_salary = (min_salary + max_salary) // 2
        profile_count = len(profiles)
        confidence_factor = min(profile_count / 10, 1.0)
        return {
            'estimated_min': int(min_salary * (0.9 + 0.1 * confidence_factor)),
            'estimated_max': int(max_salary * (0.9 + 0.1 * confidence_factor)),
            'estimated_avg': int(avg_salary * (0.9 + 0.1 * confidence_factor)),
            'confidence_level': confidence_factor,
            'profiles_analyzed': profile_count,
            'experience_level': level
        }

    # ---------- Prompt ----------
    def _build_enhanced_salary_prompt_with_dataset(
        self, job_title: str, location: str, experience_years: int, current_salary: int,
        insights: Dict[str, Any], estimates: Dict[str, Any], ds_stats: Dict[str, Any] | None, percentile: int
    ) -> str:
        similar_profiles_count = insights.get('total_profiles', 0)
        top_skills = [s['skill'] for s in insights.get('competences_demandees', [])[:5]]
        top_companies = [c['company'] for c in insights.get('entreprises_qui_recrutent', [])[:5]]
        similar_titles = [t['title'] for t in insights.get('titres_similaires', [])[:3]]

        ds_block = ""
        if ds_stats:
            ds_block = f"""
DONNÉES DATASET SALARIAL (MAD/mois):
- N={ds_stats['count']}, min={int(ds_stats['min'])}, p25={int(ds_stats['p25'])}, médiane={int(ds_stats['median'])}, p75={int(ds_stats['p75'])}, max={int(ds_stats['max'])}
- Salaire utilisateur ≈ {percentile}e percentile
"""

        return f"""
Tu es un expert RH au Maroc. Réponds **uniquement** en JSON valide.

CANDIDAT:
- Poste: {job_title}
- Lieu: {location}
- Expérience: {experience_years} ans
- Salaire actuel: {current_salary} MAD/mois

DONNÉES LINKEDIN:
- {similar_profiles_count} profils similaires
- Estimations: {estimates['estimated_min']:,}–{estimates['estimated_max']:,} MAD/mois (moyenne {estimates['estimated_avg']:,})
- Confiance: {estimates.get('confidence_level',0):.1%}
- Compétences: {', '.join(top_skills) if top_skills else 'n/a'}
- Entreprises: {', '.join(top_companies) if top_companies else 'n/a'}
- Titres proches: {', '.join(similar_titles) if similar_titles else 'n/a'}
{ds_block}
Rends exactement ce JSON:
{{
  "moyenne": {estimates['estimated_avg']},
  "ecart": {estimates['estimated_avg'] - current_salary},
  "ecart_pourcent": {((estimates['estimated_avg'] - max(1, current_salary)) / max(1, current_salary) * 100):.1f},
  "minimum": {estimates['estimated_min']},
  "maximum": {estimates['estimated_max']},
  "percentile": {percentile},
  "recommandations": [
    {{
      "title": "Positionnement salarial",
      "description": "Selon LinkedIn (N={similar_profiles_count}){(' et dataset N='+str(ds_stats['count'])) if ds_stats else ''}, votre salaire est {{'en dessous' if {current_salary} < {estimates['estimated_avg']} else 'au-dessus'}} de la médiane.",
      "priority": "high"
    }}
  ],
  "tendances": [
    {{
      "title": "Tendances marché",
      "detail": "Compétences clés: {', '.join(top_skills[:3]) if top_skills else 'n/a'}"
    }}
  ],
  "etapes": [
    {{ "numero": 1, "contenu": "Valider vos compétences vs. les annonces récentes." }},
    {{ "numero": 2, "contenu": "Préparer des arguments basés sur la médiane et le 75e percentile." }},
    {{ "numero": 3, "contenu": "Cibler les entreprises qui recrutent: {', '.join(top_companies[:5]) if top_companies else 'n/a'}" }}
  ]
}}
"""

    # ---------- Enrichissement (inchangé + métadonnées) ----------
    def _enrich_salary_analysis(self, analysis: Dict[str, Any], insights: Dict[str, Any], estimates: Dict[str, Any]) -> Dict[str, Any]:
        analysis['linkedinInsights'] = {
            'profilesAnalyzed': insights.get('total_profiles', 0),
            'confidenceLevel': estimates.get('confidence_level', 0),
            'experienceLevel': estimates.get('experience_level', 'intermediate'),
            'topSkills': [skill['skill'] for skill in insights.get('competences_demandees', [])[:5]],
            'targetCompanies': [company['company'] for company in insights.get('entreprises_qui_recrutent', [])[:5]],
            'similarTitles': [title['title'] for title in insights.get('titres_similaires', [])[:5]],
            'alternativeLocations': [loc['location'] for loc in insights.get('localisations_alternatives', [])[:3]],
            'relatedSectors': [sector['sector'] for sector in insights.get('secteurs_connexes', [])[:5]]
        }
        analysis['dataQuality'] = {
            'source': 'LinkedIn + Dataset + Gemini',
            'profilesCount': insights.get('total_profiles', 0),
            'confidenceScore': estimates.get('confidence_level', 0),
            'lastUpdated': 'now'
        }
        return analysis


enhanced_salary_service = EnhancedSalaryService()
