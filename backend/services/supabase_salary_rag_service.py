# services/supabase_salary_rag_service.py
import os, re, json
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple, Any

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client
from dotenv import load_dotenv
import requests

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ SUPABASE_URL / SUPABASE_KEY manquants dans .env")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

def call_gemini_api(prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("❌ GEMINI_API_KEY manquant dans .env")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    r = requests.post(url, json=payload, timeout=90)
    r.raise_for_status()
    data = r.json()
    txt = ""
    for c in (data.get("candidates") or []):
        for p in (c.get("content") or {}).get("parts") or []:
            if "text" in p:
                txt += p["text"]
    return txt.strip()

SALARY_EMBED_MODEL = os.getenv("SALARY_EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
INDEX_PATH = os.getenv("SALARY_FAISS_INDEX", os.path.join(os.path.dirname(__file__), "..", "data", "supabase_salary_index.faiss"))
MAP_PATH   = os.getenv("SALARY_FAISS_MAP",   os.path.join(os.path.dirname(__file__), "..", "data", "supabase_salary_index_map.json"))
os.makedirs(os.path.abspath(os.path.join(os.path.dirname(INDEX_PATH))), exist_ok=True)

def _clean(s: Optional[str]) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def _level_from_years(y: Optional[int]) -> str:
    if y is None: return "intermediate"
    if y <= 2: return "junior"
    if y <= 5: return "intermediate"
    if y <= 10: return "senior"
    return "expert"

# Base de données flexible des villes par pays
CITIES_DATABASE = {
    "Maroc": {
        "casablanca", "rabat", "tanger", "tangier", "fes", "fès", "marrakech", "marrakesh", "agadir",
        "meknes", "meknès", "kenitra", "kénitra", "tetouan", "tétouan", "safi", "el jadida", "oujda",
        "nador", "salé", "sale", "temara", "témara", "mohammedia", "khouribga", "laayoune", "al hoceima",
        "beni mellal", "berrechid", "berkan", "guelmim"
    },
    "France": {
        "paris", "lyon", "marseille", "toulouse", "nice", "nantes", "montpellier", "strasbourg", 
        "bordeaux", "lille", "rennes", "reims", "toulon", "saint-étienne", "le havre", "grenoble",
        "dijon", "angers", "nîmes", "villeurbanne"
    },
    "United States": {
        "new york", "los angeles", "chicago", "houston", "phoenix", "philadelphia", "san antonio",
        "san diego", "dallas", "san jose", "austin", "jacksonville", "fort worth", "columbus",
        "charlotte", "san francisco", "indianapolis", "seattle", "denver", "boston", "el paso",
        "detroit", "nashville", "portland", "oklahoma city", "las vegas", "baltimore", "louisville",
        "milwaukee", "albuquerque", "tucson", "fresno", "sacramento", "mesa", "kansas city",
        "atlanta", "long beach", "colorado springs", "raleigh", "miami", "virginia beach", "omaha",
        "oakland", "minneapolis", "tulsa", "arlington", "wichita", "new orleans", "cleveland"
    },
    "Canada": {
        "toronto", "montreal", "vancouver", "calgary", "ottawa", "edmonton", "mississauga", "winnipeg",
        "quebec", "québec", "halifax", "hamilton", "london", "kitchener", "st. catharines", "niagara",
        "oshawa", "victoria", "windsor", "saskatoon", "regina", "sherbrooke", "kelowna", "barrie"
    },
    "Germany": {
        "berlin", "hamburg", "munich", "münchen", "cologne", "köln", "frankfurt", "stuttgart",
        "düsseldorf", "dortmund", "essen", "leipzig", "bremen", "dresden", "hanover", "hannover",
        "nuremberg", "nürnberg", "duisburg", "bochum", "wuppertal", "bielefeld", "bonn", "münster"
    },
    "United Kingdom": {
        "london", "birmingham", "liverpool", "leeds", "glasgow", "sheffield", "bradford", "edinburgh",
        "leicester", "manchester", "bristol", "wakefield", "cardiff", "coventry", "nottingham",
        "newcastle", "belfast", "brighton", "hull", "plymouth", "stoke", "wolverhampton", "derby",
        "swansea", "southampton", "salford", "aberdeen", "westminster", "portsmouth", "york"
    }
}

def guess_city_country(location: str) -> tuple[Optional[str], str]:
    """Devine la ville et le pays à partir d'une localisation flexible"""
    loc = _clean(location).lower()
    if not loc:
        return None, "Global"
    
    # Recherche directe dans la base de données des villes
    for country, cities in CITIES_DATABASE.items():
        for city in cities:
            if city in loc:
                # Retourner le nom propre de la ville
                city_proper = city.title().replace("Fes","Fès").replace("Meknes","Meknès")
                return city_proper, country
    
    # Recherche par mots-clés de pays
    country_keywords = {
        "Maroc": ["maroc", "morocco", "ma"],
        "France": ["france", "french", "fr"],
        "United States": ["usa", "united states", "etats-unis", "états-unis", "us", "u.s.", "america"],
        "Canada": ["canada", "canadian", "ca"],
        "Germany": ["germany", "deutschland", "german", "de"],
        "United Kingdom": ["uk", "united kingdom", "britain", "england", "scotland", "wales", "gb"]
    }
    
    for country, keywords in country_keywords.items():
        if any(keyword in loc for keyword in keywords):
            return None, country
    
    # Si rien trouvé, retourner la localisation comme ville générique
    return (loc.split(",")[0].title(), "Global")

def get_market_from_country(country: str) -> str:
    """Identifie le marché économique principal d'un pays"""
    market_mapping = {
        "Maroc": "Marché Maghreb",
        "France": "Marché Européen", 
        "United States": "Marché Nord-Américain",
        "Canada": "Marché Nord-Américain",
        "Germany": "Marché Européen",
        "United Kingdom": "Marché Anglo-Saxon",
        "Global": "Marché Global"
    }
    return market_mapping.get(country, "Marché Global")

def years_str(y: Optional[int]) -> str:
    if y is None: return "3-5 ans"
    if y <= 2: return "0-2 ans"
    if y <= 5: return "3-5 ans"
    if y <= 10: return "5-10 ans"
    return "10+ ans"

# parse pgvector -> np.float32
def _as_float32_vector(emb):
    if emb is None:
        return None
    if isinstance(emb, np.ndarray):
        return emb.astype("float32")
    if isinstance(emb, list):
        return np.asarray(emb, dtype="float32")
    if isinstance(emb, str):
        s = emb.strip()
        if s.startswith("[") and s.endswith("]"):
            return np.asarray(json.loads(s), dtype="float32")
        s = s.strip("()[]{}")
        parts = re.split(r"[,\s]+", s)
        vals = [float(x) for x in parts if x]
        return np.asarray(vals, dtype="float32")
    raise TypeError(f"Unsupported embedding type: {type(emb)}")

@dataclass
class SalaryRow:
    id: int
    job_title: str
    location: str
    experience_level: str
    salary: float
    currency: str
    country: str
    market: str
    raw: Dict

class SupabaseSalaryRAGService:
    def __init__(self):
        self.model = SentenceTransformer(SALARY_EMBED_MODEL)
        self.index: Optional[faiss.Index] = None
        self.id_map: List[int] = []
        self.rows: List[SalaryRow] = []

    # ---------- utils DB ----------
    def has_any_chunk(self) -> bool:
        try:
            data = supabase.table("salary_chunks").select("id").limit(1).execute().data or []
            return len(data) > 0
        except Exception:
            return False

    def seed_if_needed(self) -> dict:
        """Backfill + embed + FAISS si aucun chunk encore présent."""
        if self.has_any_chunk():
            return {"seeded": False}
        created = self.backfill_chunks_from_salary_dataset(only_status="valide")
        self.embed_new_chunks()
        self.build_or_load_faiss()
        return {"seeded": True, **created}

    def _estimate_salary_with_llm(self, job_title: str, location: str, experience_years: int, current_salary: float) -> tuple[float, float]:
        """Utilise le LLM pour estimer UNIQUEMENT min/max quand pas de données"""
        try:
            prompt = f"""
Tu es un expert RH. Pour ce profil:

Poste: {job_title}
Localisation: {location} 
Expérience: {experience_years} ans
Salaire actuel: {current_salary} MAD/mois

Estime une fourchette réaliste pour ce marché. Réponds UNIQUEMENT:
{{"salaire_min": X, "salaire_max": Y}}
"""
            
            response = call_gemini_api(prompt)
            result = json.loads(response.strip().removeprefix("```json").removeprefix("```").removesuffix("```"))
            return float(result.get("salaire_min", current_salary * 0.9)), float(result.get("salaire_max", current_salary * 1.1))
            
        except:
            # Fallback simple basé sur le salaire actuel
            return current_salary * 0.9, current_salary * 1.1

    # ---------- ingestion améliorée ----------
    def store_user_entry(
        self, job_title: str, location: str, experience_years: int, current_salary: float, user_id: int = 1,
    ) -> tuple[int, str]:
        city, country = guess_city_country(location)
        market = get_market_from_country(country)
        exp_label = years_str(experience_years)

        # Recherche de données similaires pour estimation
        min_guess, max_guess = None, None
        try:
            # Priorité: même ville puis même pays puis même marché
            search_locations = [city, country, market] if city else [country, market]
            matches = []
            
            for search_loc in search_locations:
                if search_loc and search_loc != "Global":
                    matches = self.search(job_title, search_loc, experience_years, top_k=100)
                    if len(matches) >= 10:  # Assez de données
                        break
            
        except Exception:
            matches = []

        # Recherche de données similaires AVEC priorité expérience
        min_guess, max_guess, status = None, None, "valide"
        target_exp = years_str(experience_years)
        
        try:
            # Recherche stricte avec même niveau d'expérience d'abord
            matches = self.search_with_experience_priority(job_title, location, experience_years, top_k=100)
            
        except Exception:
            matches = []

        if matches and len(matches) >= 2:  # Assez de données similaires
            arr = np.array([self.rows[i].salary for i, _ in matches], dtype="float64")
            p25, p75 = np.percentile(arr, [25, 75])
            min_guess = float(p25 * 0.9)
            max_guess = float(p75 * 1.1)
            
            # Validation stricte basée sur les données réelles
            q10, q90 = np.percentile(arr, [10, 90])
            if not (q10 * 0.6 <= current_salary <= q90 * 1.4):
                status = "non_valide"
                
        else:
            # PAS de données suffisantes → Demander au LLM d'estimer
            min_guess, max_guess = self._estimate_salary_with_llm(
                job_title, city or country, experience_years, current_salary
            )
            
            # Pour les nouvelles entrées sans référentiel, on accepte par défaut
            # La validation se fera plus tard quand on aura plus de données
            status = "valide"

        # Insertion dans salary_dataset
        row = {
            "user_id": user_id,
            "poste": _clean(job_title),
            "ville": city,
            "pays": country,
            "experience": exp_label,
            "salaire_min": float(min_guess),
            "salaire_max": float(max_guess),
            "salaire_moyen": float(current_salary),
            "status": status,
        }
        
        try:
            res = supabase.table("salary_dataset").insert(row).execute()
            if not res.data:
                raise RuntimeError("Insertion salary_dataset échouée")
            return int(res.data[0]["id"]), status
        except Exception as e:
            raise RuntimeError(f"Erreur insertion salary_dataset: {str(e)}")

    def chunk_row(self, salary_row_id: int) -> None:
        """Crée un chunk optimisé pour une ligne de salary_dataset"""
        try:
            ds = supabase.table("salary_dataset").select("*").eq("id", salary_row_id).single().execute().data
            if not ds:
                return
            
            # Ne chunk QUE les entrées valides
            if str(ds.get("status") or "").lower().startswith("non"):
                return
            
            # Vérifier si chunk existe déjà
            existing = supabase.table("salary_chunks").select("id").eq("salary_row_id", salary_row_id).limit(1).execute().data
            if existing:
                return
            
            # Contenu enrichi pour le RAG
            location_str = ds.get("ville") or ds.get("pays") or "Global"
            market = get_market_from_country(ds.get("pays") or "Global")
            
            content = _clean(
                f"Poste: {ds.get('poste') or ''} | "
                f"Localisation: {location_str} | "
                f"Pays: {ds.get('pays') or 'Global'} | "
                f"Marché: {market} | "
                f"Experience: {ds.get('experience') or ''} | "
                f"Salaire: {int(float(ds.get('salaire_moyen') or 0))} MAD/mois | "
                f"Fourchette: {int(float(ds.get('salaire_min') or 0))}-{int(float(ds.get('salaire_max') or 0))} MAD"
            )
            
            supabase.table("salary_chunks").insert({
                "salary_row_id": salary_row_id,
                "chunk_idx": 0,
                "content": content,
                "token_count": len(content.split()),
            }).execute()
            
        except Exception as e:
            print(f"Erreur chunk_row {salary_row_id}: {str(e)}")

    # ---------- backfill amélioré ----------
    def backfill_chunks_from_salary_dataset(self, only_status: Optional[str] = "valide") -> dict:
        try:
            q = supabase.table("salary_dataset").select("id, poste, ville, pays, experience, salaire_min, salaire_max, salaire_moyen, status")
            if only_status:
                q = q.ilike("status", f"{only_status}%")
            rows = q.order("id").execute().data or []
            
            created = 0
            for ds in rows:
                if str(ds.get("status") or "").lower().startswith("non"):
                    continue
                    
                # Vérifier si chunk existe
                exists = supabase.table("salary_chunks").select("id").eq("salary_row_id", ds["id"]).limit(1).execute().data
                if exists:
                    continue
                
                # Créer chunk enrichi
                location_str = ds.get("ville") or ds.get("pays") or "Global"
                market = get_market_from_country(ds.get("pays") or "Global")
                
                content = _clean(
                    f"Poste: {ds.get('poste') or ''} | "
                    f"Localisation: {location_str} | "
                    f"Pays: {ds.get('pays') or 'Global'} | "
                    f"Marché: {market} | "
                    f"Experience: {ds.get('experience') or ''} | "
                    f"Salaire: {int(float(ds.get('salaire_moyen') or 0))} MAD/mois | "
                    f"Fourchette: {int(float(ds.get('salaire_min') or 0))}-{int(float(ds.get('salaire_max') or 0))} MAD"
                )
                
                supabase.table("salary_chunks").insert({
                    "salary_row_id": ds["id"],
                    "chunk_idx": 0,
                    "content": content,
                    "token_count": len(content.split()),
                }).execute()
                created += 1
                
            return {"created": created, "scanned": len(rows)}
            
        except Exception as e:
            return {"created": 0, "scanned": 0, "error": str(e)}

    # ---------- embeddings ----------
    def embed_new_chunks(self, batch_size: int = 64) -> int:
        try:
            rows = supabase.table("salary_chunks").select("id, content").is_("embedding", "null").order("id").execute().data or []
            total = 0
            
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i+batch_size]
                texts = [r["content"] for r in batch]
                embs = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True).astype("float32")
                
                for r, v in zip(batch, embs):
                    supabase.table("salary_chunks").update({"embedding": v.tolist()}).eq("id", r["id"]).execute()
                total += len(batch)
                
            return total
        except Exception as e:
            print(f"Erreur embed_new_chunks: {str(e)}")
            return 0

    # ---------- FAISS amélioré ----------
    def build_or_load_faiss(self) -> bool:
        # Tentative de chargement depuis fichiers
        try:
            if os.path.exists(INDEX_PATH) and os.path.exists(MAP_PATH):
                self.index = faiss.read_index(INDEX_PATH)
                with open(MAP_PATH, "r", encoding="utf-8") as f:
                    self.id_map = [int(x) for x in json.load(f)]
                self._rebuild_rows_from_id_map()
                return True
        except Exception:
            pass

        # Construction depuis la DB
        try:
            chunks = (
                supabase.table("salary_chunks")
                .select("id,salary_row_id,content,embedding")
                .not_.is_("embedding", "null")
                .order("id")
                .execute()
                .data or []
            )
            
            if not chunks:
                self.index, self.id_map, self.rows = None, [], []
                return False

            # Récupération des données salary_dataset
            row_ids = sorted({int(c["salary_row_id"]) for c in chunks if c.get("salary_row_id") is not None})
            ds_rows = (
                supabase.table("salary_dataset")
                .select("id,poste,ville,pays,experience,salaire_moyen,status")
                .in_("id", row_ids)
                .execute()
                .data or []
            )
            ds_by_id = {int(r["id"]): r for r in ds_rows}

            # Construction des vecteurs et métadonnées
            mats, id_map, rows = [], [], []
            for ch in chunks:
                ds = ds_by_id.get(int(ch["salary_row_id"]))
                if not ds:
                    continue
                if (str(ds.get("status") or "")).lower().startswith("non"):
                    continue
                    
                emb_vec = _as_float32_vector(ch.get("embedding"))
                if emb_vec is None:
                    continue
                    
                mats.append(emb_vec)
                id_map.append(int(ds["id"]))
                
                location_str = ds.get("ville") or ds.get("pays") or "Global"
                country = ds.get("pays") or "Global"
                market = get_market_from_country(country)
                
                rows.append(SalaryRow(
                    id=int(ds["id"]),
                    job_title=_clean(ds.get("poste") or ""),
                    location=_clean(location_str),
                    experience_level=_level_from_years(None),
                    salary=float(ds.get("salaire_moyen") or 0.0),
                    currency="MAD",
                    country=country,
                    market=market,
                    raw={"chunk_id": ch["id"], "content": ch.get("content", "")}
                ))

            if not mats:
                self.index, self.id_map, self.rows = None, [], []
                return False

            # Construction FAISS
            X = np.vstack(mats).astype("float32")
            faiss.normalize_L2(X)
            index = faiss.IndexFlatIP(X.shape[1])
            index.add(X)

            self.index = index
            self.id_map = id_map
            self.rows = rows

            # Sauvegarde
            faiss.write_index(index, INDEX_PATH)
            with open(MAP_PATH, "w", encoding="utf-8") as f:
                json.dump([int(x) for x in id_map], f)
            return True
            
        except Exception as e:
            print(f"Erreur build_or_load_faiss: {str(e)}")
            self.index, self.id_map, self.rows = None, [], []
            return False

    def _rebuild_rows_from_id_map(self):
        """Reconstruit les métadonnées depuis l'id_map"""
        if not self.id_map:
            self.rows = []
            return
            
        rows: List[SalaryRow] = []
        try:
            for rid in self.id_map:
                ds = supabase.table("salary_dataset").select("*").eq("id", rid).single().execute().data
                if not ds:
                    continue
                if (ds.get("status") or "").lower().startswith("non"):
                    continue
                    
                location_str = ds.get("ville") or ds.get("pays") or "Global"
                country = ds.get("pays") or "Global"
                market = get_market_from_country(country)
                # Récupérer l'expérience réelle depuis la DB
                experience_from_db = ds.get("experience") or "3-5 ans"
                
                rows.append(SalaryRow(
                    id=int(ds["id"]),
                    job_title=_clean(ds.get("poste") or ""),
                    location=_clean(location_str),
                    experience_level=experience_from_db,  # Utiliser la vraie expérience
                    salary=float(ds.get("salaire_moyen") or 0.0),
                    currency="MAD",
                    country=country,
                    market=market,
                    raw={}
                ))
        except Exception as e:
            print(f"Erreur _rebuild_rows_from_id_map: {str(e)}")
            
        self.rows = rows

    def ensure_faiss_ready(self) -> None:
        """S'assure que FAISS est prêt avec les dernières données"""
        self.seed_if_needed()
        self.embed_new_chunks()
        ok = self.build_or_load_faiss()
        if not ok:
            self.build_or_load_faiss()

    # ---------- recherche améliorée avec filtrage expérience ----------
    def search(self, job_title: str, location: str, experience_years: int, top_k: int = 200) -> List[Tuple[int, float]]:
        if (self.index is None) or (not self.rows):
            ok = self.build_or_load_faiss()
            if not ok:
                return []
                
        q_level = _level_from_years(experience_years)
        city, country = guess_city_country(location)
        market = get_market_from_country(country)
        
        # Requête enrichie avec contexte du marché
        location_context = city or country or location
        q_text = f"{_clean(job_title)} | {_clean(location_context)} | {country} | {market} | {q_level}"
        
        q_emb = self.model.encode([q_text], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
        scores, idxs = self.index.search(q_emb, top_k * 3)  # Chercher plus pour filtrer
        
        # Filtrage par expérience compatible
        experience_ranges = {
            "0-2 ans": ["0-2 ans"],
            "3-5 ans": ["0-2 ans", "3-5 ans", "2-5 ans"],
            "5-10 ans": ["3-5 ans", "5-10 ans", "5+ ans"],
            "10+ ans": ["5-10 ans", "10+ ans", "5+ ans", "8+ ans"]
        }
        
        target_exp = years_str(experience_years)
        compatible_exp = experience_ranges.get(target_exp, [target_exp])
        
        filtered_results = []
        for i, s in zip(idxs[0].tolist(), scores[0].tolist()):
            if 0 <= i < len(self.rows):
                # Récupérer l'expérience réelle depuis la DB
                row_id = self.id_map[i]
                try:
                    ds = supabase.table("salary_dataset").select("experience").eq("id", row_id).single().execute().data
                    if ds and ds.get("experience") in compatible_exp:
                        filtered_results.append((int(i), float(s)))
                        if len(filtered_results) >= top_k:
                            break
                except:
                    # Si erreur DB, inclure quand même
                    filtered_results.append((int(i), float(s)))
                    
        return filtered_results[:top_k]

    def search_with_experience_priority(self, job_title: str, location: str, experience_years: int, top_k: int = 200) -> List[Tuple[int, float]]:
        """Recherche avec priorité stricte sur l'expérience"""
        city, country = guess_city_country(location)
        target_exp = years_str(experience_years)
        
        # 1. Recherche exacte: même expérience + localisation
        exact_matches = self._search_by_criteria(job_title, location, target_exp, top_k)
        
        if len(exact_matches) >= 10:
            return exact_matches
            
        # 2. Élargir l'expérience mais garder la localisation
        experience_ranges = {
            "0-2 ans": ["0-2 ans", "2-5 ans"],
            "3-5 ans": ["0-2 ans", "3-5 ans", "2-5 ans", "3-6 ans"],
            "5-10 ans": ["3-5 ans", "5-10 ans", "5+ ans", "3-6 ans"],
            "10+ ans": ["5-10 ans", "10+ ans", "5+ ans", "8+ ans"]
        }
        
        compatible_exp = experience_ranges.get(target_exp, [target_exp])
        broader_matches = []
        
        for exp in compatible_exp:
            matches = self._search_by_criteria(job_title, location, exp, top_k // len(compatible_exp) + 10)
            broader_matches.extend(matches)
            
        # Supprimer doublons et trier par score
        unique_matches = {}
        for idx, score in broader_matches:
            if idx not in unique_matches or score > unique_matches[idx]:
                unique_matches[idx] = score
                
        return sorted(unique_matches.items(), key=lambda x: x[1], reverse=True)[:top_k]

    def _search_by_criteria(self, job_title: str, location: str, experience: str, top_k: int) -> List[Tuple[int, float]]:
        """Recherche par critères spécifiques"""
        if (self.index is None) or (not self.rows):
            return []
            
        city, country = guess_city_country(location)
        market = get_market_from_country(country)
        location_context = city or country or location
        
        q_text = f"{_clean(job_title)} | {_clean(location_context)} | {country} | {market} | {experience}"
        q_emb = self.model.encode([q_text], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
        scores, idxs = self.index.search(q_emb, top_k * 2)
        
        # Filtrer par expérience exacte depuis la DB
        results = []
        for i, s in zip(idxs[0].tolist(), scores[0].tolist()):
            if 0 <= i < len(self.rows):
                row_id = self.id_map[i]
                try:
                    ds = supabase.table("salary_dataset").select("experience").eq("id", row_id).single().execute().data
                    if ds and ds.get("experience") == experience:
                        results.append((int(i), float(s)))
                        if len(results) >= top_k:
                            break
                except:
                    continue
                    
        return results

    def aggregate_matches(self, matches: List[Tuple[int, float]]) -> Dict[str, Any]:
        if not matches:
            return {"count": 0}
            
        arr = np.array([self.rows[i].salary for i, _ in matches], dtype="float64")
        markets = [self.rows[i].market for i, _ in matches]
        countries = [self.rows[i].country for i, _ in matches]
        
        # Statistiques du marché dominant
        from collections import Counter
        market_counts = Counter(markets)
        dominant_market = market_counts.most_common(1)[0][0] if market_counts else "Marché Global"
        
        return {
            "count": int(len(matches)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "mean": float(np.mean(arr)),
            "median": float(np.median(arr)),
            "p25": float(np.percentile(arr, 25)),
            "p75": float(np.percentile(arr, 75)),
            "dominant_market": dominant_market,
            "market_distribution": dict(market_counts),
            "country_distribution": dict(Counter(countries))
        }

    def nearest_neighbors(self, job_title: str, location: str, experience_years: int, top_k: int = 8) -> List[Dict[str, Any]]:
        matches = self.search(job_title, location, experience_years, top_k=top_k)
        out = []
        for i, score in matches:
            r = self.rows[i]
            out.append({
                "title": r.job_title,
                "location": r.location,
                "country": r.country,
                "market": r.market,
                "experience_level": r.experience_level,
                "salary_mad_month": int(r.salary),
                "score": round(float(score), 4),
            })
        return out

    # ---------- analyse Gemini améliorée ----------
    def _build_prompt(self, job_title: str, location: str, experience_years: int, current_salary: int,
                      stats: Dict[str, Any], percentile: int, neighbors: List[Dict[str, Any]]) -> str:
        count = stats.get("count", 0)
        minv = int(stats.get("min", 0))
        p25 = int(stats.get("p25", 0))
        med = int(stats.get("median", 0))
        p75 = int(stats.get("p75", 0))
        maxv = int(stats.get("max", 0))
        dominant_market = stats.get("dominant_market", "Marché Global")
        
        voisins_json = json.dumps(neighbors[:8], ensure_ascii=False)
        
        return f"""
Tu es un expert RH international. Réponds **uniquement** en JSON valide (pas de texte hors JSON).

CONTEXTE MARCHÉ:
- Marché dominant analysé: {dominant_market}
- Unité: MAD/mois (converti si nécessaire)
- Échantillon dataset: N={count}, min={minv}, p25={p25}, médiane={med}, p75={p75}, max={maxv}
- Voisins proches: {voisins_json}

CANDIDAT:
- Poste: {job_title}
- Lieu: {location}
- Expérience: {experience_years} ans
- Salaire actuel: {current_salary} MAD/mois
- Positionnement: {percentile}e percentile

Rends exactement ce JSON:
{{
  "moyenne": {med},
  "ecart": {med - current_salary},
  "ecart_pourcent": {((med - max(1, current_salary)) / max(1, current_salary) * 100):.1f},
  "minimum": {p25 if count>0 else max(0, int(current_salary*0.8))},
  "maximum": {p75 if count>0 else int(current_salary*1.2)},
  "percentile": {percentile},
  "recommandations": [
    {{
      "title": "Positionnement sur {dominant_market}",
      "description": "Votre salaire se situe au {percentile}e percentile sur un échantillon de {count} profils similaires du {dominant_market}.",
      "priority": "high"
    }}
  ],
  "tendances": [
    {{
      "title": "Analyse {dominant_market}",
      "detail": "Médiane: {med} MAD/mois, fourchette interquartile: [{p25}, {p75}] sur le {dominant_market}."
    }}
  ],
  "etapes": [
    {{ "numero": 1, "contenu": "Analyser les profils similaires du {dominant_market}." }},
    {{ "numero": 2, "contenu": "Comparer avec la médiane {med} MAD/mois du marché." }},
    {{ "numero": 3, "contenu": "Négocier en s'appuyant sur les données du {dominant_market}." }}
  ],
  "dataQuality": {{
    "source": "Supabase salary_dataset (status=valide)",
    "unit": "MAD/mois",
    "sampleSize": {count},
    "marketAnalyzed": "{dominant_market}"
  }},
  "marketUsed": "{dominant_market}"
}}
""".strip()

    def analyze_with_gemini(self, job_title: str, location: str, experience_years: int, current_salary: int) -> Dict[str, Any]:
        self.ensure_faiss_ready()
        
        # Recherche progressive pour maximiser les résultats
        city, country = guess_city_country(location)
        market = get_market_from_country(country)
        
        matches = []
        search_contexts = []
        
        # 1. Recherche par ville si disponible
        if city:
            matches = self.search(job_title, city, experience_years, top_k=200)
            search_contexts.append(f"ville: {city}")
            
        # 2. Si pas assez, recherche par pays
        if len(matches) < 20 and country != "Global":
            country_matches = self.search(job_title, country, experience_years, top_k=200)
            matches.extend(country_matches)
            search_contexts.append(f"pays: {country}")
            
        # 3. Si encore insuffisant, recherche par marché
        if len(matches) < 30:
            market_matches = self.search(job_title, market, experience_years, top_k=200)
            matches.extend(market_matches)
            search_contexts.append(f"marché: {market}")
            
        # Supprimer les doublons tout en gardant les scores
        unique_matches = {}
        for idx, score in matches:
            if idx not in unique_matches or score > unique_matches[idx]:
                unique_matches[idx] = score
        matches = [(idx, score) for idx, score in unique_matches.items()]
        
        stats = self.aggregate_matches(matches)
        
    def analyze_with_gemini(self, job_title: str, location: str, experience_years: int, current_salary: int) -> Dict[str, Any]:
        self.ensure_faiss_ready()
        
        city, country = guess_city_country(location)
        market = get_market_from_country(country)
        target_experience = years_str(experience_years)
        
        # Recherche progressive AVEC filtrage par expérience
        matches = []
        search_contexts = []
        
        # 1. Recherche prioritaire avec expérience exacte
        if city:
            matches = self.search_with_experience_priority(job_title, city, experience_years, top_k=100)
            search_contexts.append(f"ville: {city}, exp: {target_experience}")
            
        # 2. Si pas assez, élargir au pays avec expérience prioritaire  
        if len(matches) < 10 and country != "Global":
            country_matches = self.search_with_experience_priority(job_title, country, experience_years, top_k=100)
            # Ajouter uniquement les nouveaux
            existing_ids = {idx for idx, _ in matches}
            for idx, score in country_matches:
                if idx not in existing_ids:
                    matches.append((idx, score))
            search_contexts.append(f"pays: {country}, exp: {target_experience}")
            
        # 3. En dernier recours, recherche par marché avec expérience élargie
        if len(matches) < 15:
            market_matches = self.search(job_title, market, experience_years, top_k=50)
            existing_ids = {idx for idx, _ in matches}
            for idx, score in market_matches:
                if idx not in existing_ids:
                    matches.append((idx, score))
            search_contexts.append(f"marché: {market}")
            
        # Trier par score décroissant et limiter
        matches = sorted(matches, key=lambda x: x[1], reverse=True)[:100]
        
        stats = self.aggregate_matches(matches)
        
        # Log pour debugging
        print(f"DEBUG: {job_title}, {location}, {experience_years} ans → {len(matches)} matches trouvés")
        print(f"DEBUG: Contextes de recherche: {search_contexts}")
        
        if stats.get("count", 0) >= 5:
            # Assez de données réelles pour une analyse fiable
            rng = max(1.0, stats["max"] - stats["min"])
            percentile = int(np.clip((current_salary - stats["min"]) / rng * 100, 0, 100))
            market_used = stats.get("dominant_market", market)
        else:
            # PAS assez de données → Demander au LLM de faire l'analyse complète
            return self._analyze_with_llm_only(job_title, location, experience_years, current_salary, market)
            
    def _analyze_with_llm_only(self, job_title: str, location: str, experience_years: int, current_salary: int, market: str) -> Dict[str, Any]:
        """Analyse complète par LLM quand pas assez de données dans le dataset"""
        try:
            prompt = f"""
Tu es un expert RH international. Analyse ce profil salarial en te basant sur tes connaissances du marché.

PROFIL:
- Poste: {job_title}
- Localisation: {location}
- Expérience: {experience_years} ans  
- Salaire actuel: {current_salary} MAD/mois
- Marché identifié: {market}

IMPORTANT: Aucune donnée suffisante dans notre dataset. Base-toi sur tes connaissances du marché réel.

Réponds exactement en JSON:
{{
  "moyenne": (salaire médian estimé pour ce profil),
  "ecart": (moyenne - {current_salary}),
  "ecart_pourcent": (pourcentage d'écart),
  "minimum": (salaire minimum réaliste),
  "maximum": (salaire maximum réaliste),
  "percentile": (position estimée 0-100),
  "recommandations": [
    {{
      "title": "Analyse basée sur les standards du marché",
      "description": "Estimation basée sur les connaissances du marché {market} pour {job_title}",
      "priority": "medium"
    }}
  ],
  "tendances": [
    {{
      "title": "Tendance marché {market}",
      "detail": "Analyse basée sur les standards généraux du marché pour ce type de profil"
    }}
  ],
  "etapes": [
    {{ "numero": 1, "contenu": "Rechercher des références salariales similaires sur le marché" }},
    {{ "numero": 2, "contenu": "Comparer avec les standards du secteur" }},
    {{ "numero": 3, "contenu": "Préparer une négociation basée sur l'analyse de marché" }}
  ],
  "dataQuality": {{
    "source": "LLM estimation (données insuffisantes)",
    "unit": "MAD/mois",
    "sampleSize": 0,
    "marketAnalyzed": "{market}",
    "note": "Estimation LLM - données réelles insuffisantes"
  }},
  "marketUsed": "{market}"
}}
"""
            
            response = call_gemini_api(prompt)
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.removeprefix("```json").removeprefix("```").strip()
            if cleaned.endswith("```"):
                cleaned = cleaned.removesuffix("```").strip()
                
            return json.loads(cleaned)
            
        except Exception as e:
            print(f"Erreur analyse LLM pure: {e}")
            # Fallback minimal
            return {
                "moyenne": current_salary,
                "ecart": 0,
                "ecart_pourcent": 0.0,
                "minimum": int(current_salary * 0.8),
                "maximum": int(current_salary * 1.2), 
                "percentile": 50,
                "recommandations": [{"title": "Données insuffisantes", "description": "Pas assez de données pour une analyse précise", "priority": "low"}],
                "tendances": [{"title": "Analyse limitée", "detail": "Données insuffisantes dans le dataset"}],
                "etapes": [{"numero": 1, "contenu": "Collecter plus de données de marché"}],
                "dataQuality": {"source": "fallback", "unit": "MAD/mois", "sampleSize": 0, "marketAnalyzed": market},
                "marketUsed": market
            }

        neighbors = self.nearest_neighbors(job_title, location, experience_years, top_k=8)
        prompt = self._build_prompt(job_title, location, experience_years, current_salary, stats, percentile, neighbors)
        
        try:
            raw = call_gemini_api(prompt)
            cleaned = raw.strip()
            if cleaned.startswith("```"): 
                cleaned = cleaned.removeprefix("```json").removeprefix("```").strip()
            if cleaned.endswith("```"):   
                cleaned = cleaned.removesuffix("```").strip()
                
            result = json.loads(cleaned)
            
            # S'assurer que marketUsed est défini
            if "marketUsed" not in result:
                result["marketUsed"] = market_used
            if "dataQuality" in result and "marketAnalyzed" not in result["dataQuality"]:
                result["dataQuality"]["marketAnalyzed"] = market_used
                
            return result
            
        except Exception as e:
            print(f"Erreur Gemini: {str(e)}")
            return {
                "moyenne": int(stats["median"]),
                "ecart": int(stats["median"] - current_salary),
                "ecart_pourcent": round(((stats["median"] - max(1, current_salary)) / max(1, current_salary) * 100), 1),
                "minimum": int(stats["p25"]), 
                "maximum": int(stats["p75"]),
                "percentile": percentile, 
                "recommandations": [
                    {
                        "title": f"Analyse {market_used}",
                        "description": f"Positionnement estimé au {percentile}e percentile sur le {market_used}.",
                        "priority": "medium"
                    }
                ], 
                "tendances": [
                    {
                        "title": f"Tendance {market_used}",
                        "detail": f"Médiane estimée: {stats['median']} MAD/mois sur le {market_used}."
                    }
                ], 
                "etapes": [
                    {"numero": 1, "contenu": f"Analyser le contexte du {market_used}."},
                    {"numero": 2, "contenu": "Comparer avec les médianes du marché."},
                    {"numero": 3, "contenu": "Préparer une négociation basée sur les données."}
                ],
                "dataQuality": {
                    "source": "supabase", 
                    "unit": "MAD/mois", 
                    "sampleSize": int(stats.get("count", 0)),
                    "marketAnalyzed": market_used,
                    "searchContexts": search_contexts
                },
                "marketUsed": market_used,
            }

    def debug_search_process(self, job_title: str, location: str, experience_years: int) -> Dict[str, Any]:
        """Fonction debug pour tracer le processus de recherche"""
        target_exp = years_str(experience_years)
        city, country = guess_city_country(location)
        
        # Compter les profils par expérience dans le dataset
        experience_counts = {}
        location_counts = {}
        
        for row in self.rows:
            exp = row.experience_level
            loc = row.location
            experience_counts[exp] = experience_counts.get(exp, 0) + 1
            location_counts[loc] = location_counts.get(loc, 0) + 1
            
        # Test des différentes recherches
        exact_matches = self._search_by_criteria(job_title, location, target_exp, 50)
        broad_matches = self.search_with_experience_priority(job_title, location, experience_years, 50)
        
        return {
            "query": {
                "job_title": job_title,
                "location": location, 
                "experience_years": experience_years,
                "target_experience": target_exp,
                "deduced_city": city,
                "deduced_country": country
            },
            "dataset_stats": {
                "total_rows": len(self.rows),
                "experience_distribution": experience_counts,
                "location_distribution": location_counts
            },
            "search_results": {
                "exact_experience_matches": len(exact_matches),
                "priority_experience_matches": len(broad_matches),
                "exact_match_ids": [self.id_map[i] for i, _ in exact_matches[:5]],
                "broad_match_ids": [self.id_map[i] for i, _ in broad_matches[:5]]
            }
        }

    def status(self) -> dict:
        market_stats = {}
        if self.rows:
            from collections import Counter
            markets = [r.market for r in self.rows]
            countries = [r.country for r in self.rows]
            market_stats = {
                "markets": dict(Counter(markets)),
                "countries": dict(Counter(countries)),
                "total_markets": len(set(markets))
            }
            
        return {
            "faissLoaded": self.index is not None and len(self.rows) > 0,
            "rows": len(self.rows), 
            "idMapSize": len(self.id_map),
            "indexPath": os.path.abspath(INDEX_PATH), 
            "mapPath": os.path.abspath(MAP_PATH),
            "model": SALARY_EMBED_MODEL,
            "supportedMarkets": list(CITIES_DATABASE.keys()),
            **market_stats
        }

supabase_salary_rag = SupabaseSalaryRAGService()