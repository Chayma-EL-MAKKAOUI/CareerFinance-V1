# services/supabase_salary_rag_service.py
import os, re, json
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple
from collections import Counter

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# ───────────────── CONFIG SUPABASE ─────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ SUPABASE_URL / SUPABASE_KEY manquants dans .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ───────────────── MODELE + FAISS ─────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

SALARY_EMBED_MODEL = os.getenv(
    "SALARY_EMBED_MODEL",
    "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
)

INDEX_PATH = os.getenv(
    "SALARY_FAISS_INDEX",
    os.path.join(PROJECT_ROOT, "data", "supabase_salary_index.faiss")
)
MAP_PATH = os.getenv(
    "SALARY_FAISS_MAP",
    os.path.join(PROJECT_ROOT, "data", "supabase_salary_index_map.json")
)
os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)

# ───────────────── Helpers ─────────────────
def _norm(s: Optional[str]) -> str:
    return (s or "").strip().lower()

def _normalize_ws(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def years_to_level(y: Optional[int]) -> str:
    if y is None: return "intermediate"
    y = int(y)
    if y <= 2: return "junior"
    if y <= 5: return "intermediate"
    if y <= 10: return "senior"
    return "expert"

def years_to_bucket(y: Optional[int]) -> str:
    lvl = years_to_level(y)
    return {
        "junior": "0-2 ans",
        "intermediate": "2-5 ans",
        "senior": "5-10 ans",
        "expert": "10+ ans",
    }[lvl]

# Villes Maroc / USA rapides + alias pays
_MA_CITIES = {
    "casablanca","rabat","salé","sale","marrakech","fes","fès","meknès","meknes",
    "agadir","tanger","tangier","oujda","kenitra","kénitra","tetouan","tétouan",
    "nador","laayoune","dakhla","beni mellal","safi","el jadida","khouribga",
    "taounate","taourirt","berkane","guelmim","taza"
}
_US_CITIES = {
    "new york","san francisco","los angeles","seattle","austin","boston",
    "chicago","atlanta","dallas","denver","miami","houston","san diego"
}
_COUNTRY_ALIASES = {
    "maroc": "Maroc", "morocco": "Maroc", "kingdom of morocco": "Maroc",
    "usa": "États-Unis", "us": "États-Unis", "united states": "États-Unis",
    "united states of america": "États-Unis", "etats-unis": "États-Unis", "états-unis":"États-Unis",
    "france": "France",
}

def infer_city_country(location_input: str) -> Tuple[str, str]:
    """
    Déduit (ville, pays) depuis l'entrée libre:
      - si c'est un pays -> (ville=pays, pays=pays)
      - si ville connue MA/USA -> map direct
      - sinon, on sonde salary_dataset: ville -> pays majoritaire, ou pays partiel
      - fallback: (TitleCase, TitleCase)
    """
    raw = location_input or ""
    if "," in raw:
        left, right = [x.strip() for x in raw.split(",", 1)]
        country = _COUNTRY_ALIASES.get(_norm(right))
        if country:
            return (left.title(), country)

    n = _norm(raw)
    if n in _COUNTRY_ALIASES:
        c = _COUNTRY_ALIASES[n]
        return (c, c)
    if n in _MA_CITIES:
        return (raw.title(), "Maroc")
    if n in _US_CITIES:
        return (raw.title(), "États-Unis")

    # Chercher dans dataset existant (ville -> pays majoritaire)
    try:
        res = supabase.table("salary_dataset").select("ville,pays").ilike("ville", f"%{raw}%").limit(1000).execute()
        pays_vals = [(_COUNTRY_ALIASES.get(_norm(r["pays"]), r["pays"])) for r in (res.data or []) if r.get("pays")]
        if pays_vals:
            most = Counter(pays_vals).most_common(1)[0][0]
            return (raw.title(), most)
    except Exception:
        pass
    # Chercher si l'entrée correspond à un pays dans la base
    try:
        res = supabase.table("salary_dataset").select("pays").ilike("pays", f"%{raw}%").limit(5).execute()
        if res.data:
            p = res.data[0]["pays"]
            return (p, p)
    except Exception:
        pass

    return (raw.title(), raw.title())

# ───────────────── DataClasses ─────────────────
@dataclass
class SalaryChunkMeta:
    chunk_id: int
    salary_row_id: int
    content: str
    poste: str
    ville: str
    pays: str
    experience: str
    salaire_min: Optional[float]
    salaire_max: Optional[float]
    salaire_moyen: Optional[float]
    status: Optional[str]

# ───────────────── Service ─────────────────
class SupabaseSalaryRAGService:
    """
    - Stocke les entrées utilisateur dans salary_dataset (user_id=1)
    - Devine ville/pays, estime min/max du marché, fixe status ('valide' si raisonnable)
    - Crée 1 chunk + embedding dans salary_chunks
    - Construit/charge index FAISS à partir des embeddings
    - Recherche + agrégation filtrées (localisation + status='valide')
    """
    def __init__(self):
        self.model = SentenceTransformer(SALARY_EMBED_MODEL)
        self.dim = self.model.get_sentence_embedding_dimension()
        self.index: Optional[faiss.Index] = None
        self.id_map: List[int] = []  # map FAISS row -> salary_chunks.id

    # ---------- Embedding ----------
    def embed_text(self, text: str) -> np.ndarray:
        v = self.model.encode([text], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
        return v[0]

    def _chunk_text(self, poste: str, ville: str, pays: str, level: str, salaire_moyen: Optional[float], salaire_min: Optional[float], salaire_max: Optional[float]) -> str:
        parts = [
            poste or "",
            ville or "",
            pays or "",
            level or "",
            f"{int(salaire_moyen)} MAD/mois" if salaire_moyen else "",
            f"min {int(salaire_min)}" if salaire_min else "",
            f"max {int(salaire_max)}" if salaire_max else "",
        ]
        return _normalize_ws(" | ".join([p for p in parts if p]))

    # ---------- Estimation marché ----------
    def _fetch_market_samples(self, poste: str, ville: str, pays: str, level_bucket: str, scope: str) -> List[float]:
        """
        Retourne une liste de valeurs (MAD/mois) à partir du dataset:
        - utilise salaire_moyen si dispo, sinon moyenne de (min,max) si les deux existent
        - filtre status='valide' uniquement
        scope ∈ {'city_country','country','global'}
        """
        q = supabase.table("salary_dataset").select(
            "salaire_moyen, salaire_min, salaire_max, poste, experience, pays, ville, status"
        ).eq("status", "valide")

        # poste: match souple
        q = q.ilike("poste", f"%{poste}%")
        # niveau: bucket exact + variantes usuelles
        bucket = level_bucket
        variants = {
            "0-2 ans": ["0-1 ans", "1-2 ans", "0–2 ans", "<2 ans", "0-2 ans"],
            "2-5 ans": ["2-4 ans", "2-5 ans", "3-5 ans"],
            "5-10 ans": ["5-8 ans", "6-10 ans", "5-10 ans"],
            "10+ ans": ["10+ ans", "10-15 ans", "15+ ans"],
        }[bucket]
        q = q.in_("experience", variants)

        if scope == "city_country":
            q = q.eq("pays", pays).eq("ville", ville)
        elif scope == "country":
            q = q.eq("pays", pays)
        # global => pas de filtre localisation

        res = q.limit(5000).execute()
        vals: List[float] = []
        for r in (res.data or []):
            m = r.get("salaire_moyen")
            if m is not None:
                try: vals.append(float(m))
                except: pass
                continue
            smin, smax = r.get("salaire_min"), r.get("salaire_max")
            try:
                if smin is not None and smax is not None:
                    vals.append((float(smin) + float(smax)) / 2.0)
                elif smin is not None:
                    vals.append(float(smin))
                elif smax is not None:
                    vals.append(float(smax))
            except:
                pass
        return vals

    def _estimate_market(self, poste: str, ville: str, pays: str, experience_years: int) -> Dict[str, object]:
        bucket = years_to_bucket(experience_years)

        # ordre de préférence: ville+pays -> pays -> global
        scopes = [("city_country", "ville+pays"), ("country", "pays"), ("global", "global")]
        chosen_scope = None
        chosen_vals: List[float] = []
        for scope_key, label in scopes:
            vals = self._fetch_market_samples(poste, ville, pays, bucket, scope_key)
            if len(vals) >= 8 or (scope_key == "global" and len(vals) >= 3):
                chosen_scope = label
                chosen_vals = vals
                break

        if not chosen_vals:
            # last resort: tiny sets (ville+pays puis pays puis global)
            for scope_key, label in scopes:
                vals = self._fetch_market_samples(poste, ville, pays, bucket, scope_key)
                if vals:
                    chosen_scope = label
                    chosen_vals = vals
                    break

        if not chosen_vals:
            return {
                "scope": "none",
                "count": 0,
                "min": None, "max": None, "mean": None,
                "p10": None, "p50": None, "p90": None,
            }

        arr = np.array(chosen_vals, dtype="float64")
        stats = {
            "scope": chosen_scope,
            "count": int(arr.size),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "mean": float(np.mean(arr)),
            "p10": float(np.percentile(arr, 10)),
            "p50": float(np.percentile(arr, 50)),
            "p90": float(np.percentile(arr, 90)),
        }
        return stats

    def _is_salary_reasonable(self, salary_user: float, est: Dict[str, object]) -> bool:
        """
        Règle simple: salaire_user ∈ [p10*0.9, p90*1.1] si p10/p90 dispo,
        sinon [min*0.8, max*1.2], sinon True (pas assez de données).
        """
        if not est or est.get("count", 0) < 3:
            return True
        p10, p90 = est.get("p10"), est.get("p90")
        if p10 is not None and p90 is not None:
            return (salary_user >= 0.9 * p10) and (salary_user <= 1.1 * p90)
        mn, mx = est.get("min"), est.get("max")
        if mn is not None and mx is not None:
            return (salary_user >= 0.8 * mn) and (salary_user <= 1.2 * mx)
        return True

    # ---------- Insertion utilisateur + chunk ----------
    def insert_user_entry_and_chunk(
        self,
        user_id: int,
        poste: str,
        location: str,
        experience_years: int,
        salaire_user_mad: float,
        source: str = "user_input"
    ) -> Dict[str, object]:
        ville, pays = infer_city_country(location)
        level = years_to_level(experience_years)
        bucket = years_to_bucket(experience_years)

        est = self._estimate_market(poste, ville, pays, experience_years)
        # salaire_moyen = salaire saisi par l'utilisateur (demandé)
        salaire_moyen = float(salaire_user_mad) if salaire_user_mad is not None else None
        # deviner min/max à partir du marché
        salaire_min = est.get("p10") or est.get("min")
        salaire_max = est.get("p90") or est.get("max")

        status = "valide" if self._is_salary_reasonable(salaire_user_mad, est) else "non_valide"

        # Insérer dans salary_dataset
        row = {
            "user_id": user_id,
            "poste": poste,
            "experience": bucket,   # ex: "2-5 ans"
            "ville": ville,
            "pays": pays,
            "salaire_min": salaire_min,
            "salaire_max": salaire_max,
            "salaire_moyen": salaire_moyen,   # salaire saisi
            "status": status,
            "source": source,
        }
        ins = supabase.table("salary_dataset").insert(row).execute()
        if not ins.data:
            raise RuntimeError("Insertion salary_dataset a échoué")
        salary_row_id = ins.data[0]["id"]

        # Chunk + embedding
        content = self._chunk_text(poste, ville, pays, level, salaire_moyen, salaire_min, salaire_max)
        emb = self.embed_text(content)
        chunk = {
            "salary_row_id": salary_row_id,
            "chunk_idx": 0,
            "content": content,
            "token_count": len(content.split()),
            "embedding": emb.tolist(),
        }
        supabase.table("salary_chunks").insert(chunk).execute()

        return {
            "row_id": salary_row_id,
            "ville": ville, "pays": pays, "level": level, "bucket": bucket,
            "market": est, "status": status, "scopeUsed": est.get("scope", "none"),
        }

    # ---------- Embeddings manquants ----------
    def embed_new_chunks(self, batch_size: int = 64) -> Dict[str, int]:
        # chunks sans embedding
        res = supabase.table("salary_chunks").select("id, content").is_("embedding", "null").order("created_at").execute()
        rows = res.data or []
        total = 0
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i+batch_size]
            texts = [r["content"] for r in batch]
            embs = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True).astype("float32")
            for r, v in zip(batch, embs):
                supabase.table("salary_chunks").update({"embedding": v.tolist()}).eq("id", r["id"]).execute()
            total += len(batch)
        return {"embedded_chunks": total}

    # ---------- FAISS ----------
    def build_or_load_faiss(self) -> bool:
        # 1) essayer disque
        try:
            if os.path.exists(INDEX_PATH) and os.path.exists(MAP_PATH):
                self.index = faiss.read_index(INDEX_PATH)
                with open(MAP_PATH, "r", encoding="utf-8") as f:
                    self.id_map = json.load(f)
                return True
        except Exception as e:
            print("[SalaryRAG] load FAISS (disk) error:", e)

        # 2) charger embeddings depuis Supabase (uniquement status='valide')
        try:
            res = supabase.table("salary_chunks").select(
                "id, embedding, salary_dataset(status)"
            ).not_.is_("embedding", "null").order("salary_row_id, chunk_idx").execute()
            rows = res.data or []
            ids, mats = [], []
            for r in rows:
                # ne garder que les chunks dont la ligne parente est 'valide'
                parent = r.get("salary_dataset", {})
                if isinstance(parent, dict):
                    st = parent.get("status")
                else:
                    st = None
                if st != "valide":
                    continue
                emb = r.get("embedding")
                if emb is None:
                    continue
                ids.append(int(r["id"]))
                mats.append(np.asarray(emb, dtype="float32"))
            if not mats:
                print("[SalaryRAG] Aucun embedding valide trouvé")
                return False
        except Exception as e:
            print("[SalaryRAG] lecture embeddings supabase erreur:", e)
            return False

        X = np.vstack(mats).astype("float32")
        faiss.normalize_L2(X)
        index = faiss.IndexFlatIP(X.shape[1])
        index.add(X)
        self.index = index
        self.id_map = ids
        try:
            faiss.write_index(index, INDEX_PATH)
            with open(MAP_PATH, "w", encoding="utf-8") as f:
                json.dump(self.id_map, f)
        except Exception as e:
            print("[SalaryRAG] save FAISS error:", e)
        return True

    # ---------- Fetch meta ----------
    def _fetch_chunk_meta(self, chunk_id: int) -> Optional[SalaryChunkMeta]:
        try:
            res = supabase.table("salary_chunks").select(
                "id, content, salary_row_id, chunk_idx, "
                "salary_dataset(poste, ville, pays, experience, salaire_min, salaire_max, salaire_moyen, status)"
            ).eq("id", chunk_id).limit(1).execute()
            if not res.data:
                return None
            r = res.data[0]
            sd = r.get("salary_dataset") or {}
            return SalaryChunkMeta(
                chunk_id=int(r["id"]),
                salary_row_id=int(r["salary_row_id"]),
                content=r["content"] or "",
                poste=sd.get("poste",""),
                ville=sd.get("ville",""),
                pays=sd.get("pays",""),
                experience=sd.get("experience",""),
                salaire_min=sd.get("salaire_min"),
                salaire_max=sd.get("salaire_max"),
                salaire_moyen=sd.get("salaire_moyen"),
                status=sd.get("status")
            )
        except Exception as e:
            print("[SalaryRAG] _fetch_chunk_meta error:", e)
            return None

    # ---------- Search ----------
    def search(self, job_title: str, location: str, experience_years: int, top_k: int = 200) -> Dict[str, object]:
        if self.index is None or not self.id_map:
            ok = self.build_or_load_faiss()
            if not ok:
                # tenter d’encoder ce qui manque puis rebâtir
                self.embed_new_chunks()
                ok = self.build_or_load_faiss()
                if not ok:
                    return {"matches": [], "marketUsed": "none"}

        ville, pays = infer_city_country(location)
        q_level = years_to_level(experience_years)
        # requête: job | ville | pays | level
        q_text = _normalize_ws(f"{job_title} | {ville} | {pays} | {q_level}")
        q = self.model.encode([q_text], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
        D, I = self.index.search(q, top_k)

        out = []
        for faiss_idx, score in zip(I[0].tolist(), D[0].tolist()):
            if faiss_idx < 0 or faiss_idx >= len(self.id_map):
                continue
            cid = self.id_map[faiss_idx]
            meta = self._fetch_chunk_meta(int(cid))
            if not meta:
                continue
            # garder uniquement les lignes valides + localisation cohérente (pays prioritaire)
            if meta.status != "valide":
                continue
            if meta.pays and _norm(meta.pays) != _norm(pays):
                continue
            # si ville renseignée coté user, préférer les villes identiques si dispo
            if _norm(ville) in _MA_CITIES or _norm(ville) in _US_CITIES or len(ville) >= 3:
                # on est tolérant si ville vide côté meta
                if meta.ville and _norm(meta.ville) != _norm(ville):
                    # on laisse passer quand même mais avec score plus faible (post-filtrage basique)
                    score = score * 0.92
            out.append({
                "chunk_id": cid,
                "score": float(score),
                "text": meta.content,
                "poste": meta.poste,
                "ville": meta.ville,
                "pays": meta.pays,
                "experience": meta.experience,
                "salaire_moyen": meta.salaire_moyen,
                "salaire_min": meta.salaire_min,
                "salaire_max": meta.salaire_max,
            })

        # tri final par score
        out.sort(key=lambda x: x["score"], reverse=True)
        return {"matches": out, "marketUsed": f"{ville}, {pays}"}

    # ---------- Aggregate ----------
    def aggregate(self, matches: List[Dict[str, object]]) -> Dict[str, float]:
        if not matches:
            return {"count": 0}
        vals = []
        for m in matches:
            v = m.get("salaire_moyen")
            if v is not None:
                vals.append(float(v))
                continue
            smin, smax = m.get("salaire_min"), m.get("salaire_max")
            if smin is not None and smax is not None:
                vals.append((float(smin) + float(smax)) / 2.0)
            elif smin is not None:
                vals.append(float(smin))
            elif smax is not None:
                vals.append(float(smax))
        if not vals:
            return {"count": 0}
        arr = np.array(vals, dtype="float64")
        return {
            "count": int(arr.size),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "mean": float(np.mean(arr)),
            "median": float(np.median(arr)),
            "p25": float(np.percentile(arr, 25)),
            "p50": float(np.percentile(arr, 50)),
            "p75": float(np.percentile(arr, 75)),
        }

    # ---------- Analyse end-to-end (+ upsert user) ----------
    def analyze_and_upsert(
        self,
        job_title: str,
        location: str,
        experience_years: int,
        current_salary_mad: float,
        user_id: int = 1
    ) -> Dict[str, object]:
        ins = self.insert_user_entry_and_chunk(
            user_id=user_id,
            poste=job_title,
            location=location,
            experience_years=experience_years,
            salaire_user_mad=current_salary_mad,
            source="user_input"
        )
        # Recherche & agrégation
        result = self.search(job_title, location, experience_years, top_k=200)
        agg = self.aggregate(result["matches"])
        scope = ins.get("scopeUsed") or "unknown"
        return {
            "stats": agg,
            "dataQuality": {
                "marketScope": scope,
                "samples": agg.get("count", 0),
                "marketLocation": result.get("marketUsed"),
                "userRowStatus": ins.get("status", "valide"),
            },
            "marketUsed": result.get("marketUsed"),  # demandé côté frontend
        }

    # ---------- Status ----------
    def status(self) -> Dict[str, object]:
        # count rows
        try:
            cnt = supabase.rpc("count_salary_chunks").execute().data  # si tu as une RPC; sinon fallback:
        except Exception:
            cnt = None
        try:
            res = supabase.table("salary_chunks").select("id", count="exact").execute()
            rows_chunks = res.count if hasattr(res, "count") else (len(res.data or []))
        except Exception:
            rows_chunks = None
        try:
            res2 = supabase.table("salary_dataset").select("id", count="exact").execute()
            rows_dataset = res2.count if hasattr(res2, "count") else (len(res2.data or []))
        except Exception:
            rows_dataset = None
        return {
            "indexExists": self.index is not None,
            "mapSize": len(self.id_map),
            "chunksCount": rows_chunks,
            "datasetRows": rows_dataset,
            "embedModel": SALARY_EMBED_MODEL,
            "indexPath": INDEX_PATH,
        }

# Instance globale
supabase_salary_rag = SupabaseSalaryRAGService()
