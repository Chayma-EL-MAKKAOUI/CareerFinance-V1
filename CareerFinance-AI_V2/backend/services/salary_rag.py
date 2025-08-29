# services/salary_rag.py
import os, pickle
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import psycopg2
import psycopg2.extras


@dataclass
class SalaryRow:
    job_title: str
    location: str
    experience_level: str   # junior / intermediate / senior / expert
    experience_years: Optional[float]
    salary: float           # MAD / month
    currency: str
    raw: Dict[str, Any]


LEVEL_MAP = {
    "EN": "junior", "MI": "intermediate", "SE": "senior", "EX": "expert",
    "JUNIOR": "junior", "INTERMEDIATE": "intermediate", "SENIOR": "senior", "EXPERT": "expert",
}
LEVEL_MAP_FR = {
    "débutant": "junior", "debutant": "junior",
    "intermédiaire": "intermediate", "intermediaire": "intermediate",
    "senior": "senior",
    "cadre supérieur": "expert", "cadre superieur": "expert",
}

def _map_level(val: str) -> str:
    if val is None:
        return "intermediate"
    s = str(val).strip()
    up = s.upper()
    if up in LEVEL_MAP:
        return LEVEL_MAP[up]
    low = s.lower()
    low_na = (
        low.replace("é", "e").replace("è", "e").replace("ê", "e")
           .replace("à", "a").replace("â", "a").replace("î", "i")
           .replace("ô", "o").replace("ç", "c")
    )
    return LEVEL_MAP_FR.get(low, LEVEL_MAP_FR.get(low_na, "intermediate"))

def years_to_level(y: Optional[float]) -> str:
    if y is None: return "intermediate"
    y = float(y)
    if y <= 2: return "junior"
    if y <= 5: return "intermediate"
    if y <= 10: return "senior"
    return "expert"


# =============== CONFIG PG / MODEL / PATHS ===============
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", "5433"))
PG_DB   = os.getenv("PG_DB", "mydb")
PG_USER = os.getenv("PG_USER", "admin")
PG_PASS = os.getenv("PG_PASS", "admin")

def get_conn():
    return psycopg2.connect(
        host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PASS
    )

MODEL_NAME = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
INDEX_PATH = os.getenv("SALARY_INDEX_PATH", "data/salary_index.faiss")
EMB_PATH   = os.getenv("SALARY_EMB_PATH",   "data/salary_embeddings.npy")
DATA_PATH_LABEL = f"postgresql://{PG_HOST}:{PG_PORT}/{PG_DB}#salary_dataset"
os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)


class SalaryRAGService:
    """
    RAG tabulaire pour la table salary_dataset (MAD / mois) dans PostgreSQL.
    Attend au minimum les colonnes:
      - job_title
      - company_location (ou location)
      - experience_level
      - monthly_salary_mad
    """
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        self.rows: List[SalaryRow] = []
        self.embeddings: Optional[np.ndarray] = None
        self.index: Optional[faiss.Index] = None
        # compat avec routes existantes
        self.data_path = DATA_PATH_LABEL

    # ---------- LOAD FROM PG ----------
    def load(self):
        with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        # Détecter la colonne de localisation disponible
            cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'salary_dataset'
              AND column_name IN ('location','company_location')
        """)
            cols = {r[0] for r in cur.fetchall()}
            loc_col = 'location' if 'location' in cols else 'company_location'

           # Charger les lignes avec alias 'location'
            cur.execute(f"""
            SELECT
                id,
                job_title,
                {loc_col} AS location,
                experience_level,
                monthly_salary_mad,
                COALESCE(currency, 'MAD') AS currency,
                work_year
            FROM salary_dataset
            WHERE monthly_salary_mad IS NOT NULL
              AND job_title IS NOT NULL
              AND {loc_col} IS NOT NULL
            """)
            rows = cur.fetchall()

        out: List[SalaryRow] = []
        for r in rows:
           level_final = _map_level(r["experience_level"]) if "experience_level" in r else "intermediate"
           try:
            salary = float(r["monthly_salary_mad"])
           except Exception:
            continue
           out.append(SalaryRow(
            job_title=str(r["job_title"]).strip(),
            location=str(r["location"]).strip(),
            experience_level=level_final,
            experience_years=None,
            salary=salary,
            currency=(r["currency"] or "MAD"),
            raw=dict(r)
        ))
        self.rows = out

    def _row_text(self, r: SalaryRow) -> str:
        return f"{r.job_title} | {r.location} | {r.experience_level} | {int(r.salary)} MAD/mois"

    # ---------- INDEX ----------
    def create_embeddings(self):
        if not self.rows:
            self.load()
        texts = [self._row_text(r) for r in self.rows]
        embs = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False)
        self.embeddings = embs.astype("float32")
        return self.embeddings

    def build_index(self):
        if self.embeddings is None:
            self.create_embeddings()
        dim = self.embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)   # cosine via IP + L2-normalized vectors
        faiss.normalize_L2(self.embeddings)  # sécurité
        index.add(self.embeddings)
        self.index = index
        return index

    def save_index(self):
        if self.index is not None:
            faiss.write_index(self.index, INDEX_PATH)
        if self.embeddings is not None:
            np.save(EMB_PATH, self.embeddings)

    def load_index(self) -> bool:
        try:
            if os.path.exists(INDEX_PATH) and os.path.exists(EMB_PATH):
                self.index = faiss.read_index(INDEX_PATH)
                self.embeddings = np.load(EMB_PATH).astype("float32")
                return True
        except Exception as e:
            print("load_index error:", e)
        return False

    # ---------- QUERY ----------
    def search(self, job_title: str, location: str, experience_years: int, top_k: int = 200) -> List[Tuple[int, float]]:
        if (self.index is None) or (self.embeddings is None):
            if not self.load_index():
                self.load()
                self.create_embeddings()
                self.build_index()
            else:
                if not self.rows:
                    self.load()

        q_level = years_to_level(experience_years)
        q_text  = f"{job_title} | {location} | {q_level}"
        q_emb   = self.model.encode([q_text], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
        scores, idxs = self.index.search(q_emb, top_k)
        return [(int(i), float(s)) for i, s in zip(idxs[0], scores[0]) if 0 <= i < len(self.rows)]

    def aggregate(self, matches: List[Tuple[int, float]]) -> Dict[str, Any]:
        if not matches:
            return {"count": 0}
        salaries = np.array([self.rows[i].salary for i, _ in matches], dtype="float64")
        return {
            "count": int(len(matches)),
            "min": float(np.min(salaries)),
            "max": float(np.max(salaries)),
            "mean": float(np.mean(salaries)),
            "median": float(np.median(salaries)),
            "p25": float(np.percentile(salaries, 25)),
            "p50": float(np.percentile(salaries, 50)),
            "p75": float(np.percentile(salaries, 75)),
        }


# Instance globale (nom inchangé)
salary_rag = SalaryRAGService()
