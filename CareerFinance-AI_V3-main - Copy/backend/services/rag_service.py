# services/rag_service.py
import os
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

import numpy as np
import faiss
import psycopg2
import psycopg2.extras
from sentence_transformers import SentenceTransformer


# ==================== CONFIG PG ====================
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", "5433"))
PG_DB   = os.getenv("PG_DB", "mydb")
PG_USER = os.getenv("PG_USER", "admin")
PG_PASS = os.getenv("PG_PASS", "admin")

def get_conn():
    return psycopg2.connect(
        host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PASS
    )


# ==================== MODELE EMBEDDING ====================
MODEL_NAME = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")  # 384d
INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "data/linkedin_index.faiss")
EMB_PATH   = os.getenv("FAISS_EMB_PATH",   "data/linkedin_embeddings.npy")
os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)


@dataclass
class LinkedInProfile:
    name: str
    title: str
    company: str
    location: str
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    skills: List[str]
    summary: str
    connections: int
    raw_data: Dict[str, Any]


class LinkedInRAGService:
    """
    Source: PostgreSQL (tables: profiles, experiences, competences)
    Index:  FAISS (IndexFlatIP) avec vecteurs normalisés (cosine)
    """
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        self.emb_dim = self.model.get_sentence_embedding_dimension()
        self.profiles: List[LinkedInProfile] = []
        self.embeddings: Optional[np.ndarray] = None
        self.index: Optional[faiss.Index] = None

    # ---------- PG READ ----------
    def _fetch_profiles(self, cur) -> List[Tuple[int, str, str, str]]:
        cur.execute("SELECT id, nom, titre, formation FROM profiles ORDER BY id;")
        return cur.fetchall()

    def _fetch_experiences(self, cur) -> List[Tuple[int, str, str, str, str, str]]:
        cur.execute("""
            SELECT profile_id, poste, entreprise, periode, localisation, description
            FROM experiences
            ORDER BY profile_id, id DESC;  -- id DESC ~ plus récent d'abord
        """)
        return cur.fetchall()

    def _fetch_competences(self, cur) -> List[Tuple[int, str]]:
        cur.execute("""
            SELECT profile_id, competence
            FROM competences
            ORDER BY profile_id, id;
        """)
        return cur.fetchall()

    def load_linkedin_data(self) -> List[LinkedInProfile]:
        """
        Charge les profils depuis PostgreSQL et construit self.profiles.
        (Compat API avec ton router)
        """
        with get_conn() as conn, conn.cursor() as cur:
            prof_rows = self._fetch_profiles(cur)
            xp_rows   = self._fetch_experiences(cur)
            sk_rows   = self._fetch_competences(cur)

        xp_by: Dict[int, List[Tuple[int, str, str, str, str, str]]] = {}
        for r in xp_rows:
            xp_by.setdefault(r[0], []).append(r)

        sk_by: Dict[int, List[str]] = {}
        for pid, comp in sk_rows:
            if comp:
                sk_by.setdefault(pid, []).append(comp)

        profiles: List[LinkedInProfile] = []
        for pid, nom, titre, formation in prof_rows:
            # entreprise/location courantes = première expérience (id DESC)
            current_company = ""
            current_location = ""
            exps = []
            for (_pid, poste, ent, per, loc, desc) in xp_by.get(pid, []):
                exps.append({
                    "poste": poste, "entreprise": ent, "periode": per,
                    "localisation": loc, "description": desc
                })
            if exps:
                current_company = (exps[0].get("entreprise") or "").split("·")[0].strip()
                current_location = exps[0].get("localisation") or ""

            skills = sk_by.get(pid, [])

            # résumé lisible
            parts = []
            if titre: parts.append(f"Titre: {titre}")
            if current_company: parts.append(f"Entreprise: {current_company}")
            if current_location: parts.append(f"Localisation: {current_location}")
            if exps:
                parts.append(f"Expériences: {len(exps)} postes")
                for e in exps[:2]:
                    p = e.get("poste") or ""
                    c = e.get("entreprise") or ""
                    if p:
                        parts.append(f"- {p} chez {c}".strip())
            summary = ". ".join(parts)

            profiles.append(LinkedInProfile(
                name=nom or "Unknown",
                title=titre or "",
                company=current_company,
                location=current_location,
                experience=exps,
                education=([{"description": formation}] if formation else []),
                skills=skills,
                summary=summary,
                connections=0,
                raw_data={"id": pid}
            ))

        self.profiles = profiles
        return profiles

    # ---------- EMBEDDINGS / INDEX ----------
    def _profile_text(self, p: LinkedInProfile) -> str:
        text_parts = [
            p.name, p.title, p.company, p.location, p.summary, " ".join(p.skills)
        ]
        for e in p.experience:
            text_parts.extend([
                e.get("poste",""), e.get("entreprise",""), e.get("localisation",""),
                e.get("periode",""), e.get("description","") or ""
            ])
        return " ".join([t for t in text_parts if t]).strip()

    def create_embeddings(self) -> np.ndarray:
        if not self.profiles:
            self.load_linkedin_data()
        texts = [self._profile_text(p) for p in self.profiles]
        embs = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False)
        self.embeddings = embs.astype("float32")
        return self.embeddings

    def build_index(self) -> faiss.Index:
        if self.embeddings is None:
            self.create_embeddings()
        index = faiss.IndexFlatIP(self.embeddings.shape[1])  # cosine via IP + vecteurs normalisés
        faiss.normalize_L2(self.embeddings)                  # sécurité
        index.add(self.embeddings)
        self.index = index
        return index

    def save_index(self):
        if self.index is None or self.embeddings is None:
            return
        faiss.write_index(self.index, INDEX_PATH)
        np.save(EMB_PATH, self.embeddings)

    def load_index(self) -> bool:
        try:
            if os.path.exists(INDEX_PATH) and os.path.exists(EMB_PATH):
                self.index = faiss.read_index(INDEX_PATH)
                self.embeddings = np.load(EMB_PATH).astype("float32")
                return True
        except Exception as e:
            print("Erreur load_index:", e)
        return False

    # ---------- SEARCH / INSIGHTS (compat avec tes routers) ----------
    def search_profiles(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        # S'assurer d'avoir index + profils
        if (self.index is None) or (self.embeddings is None):
            if not self.load_index():
                self.load_linkedin_data()
                self.build_index()
            else:
                if not self.profiles:
                    self.load_linkedin_data()

        q = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
        scores, idxs = self.index.search(q, top_k)

        out = []
        for rank, (s, i) in enumerate(zip(scores[0].tolist(), idxs[0].tolist()), 1):
            if i < 0 or i >= len(self.profiles):
                continue
            p = self.profiles[i]
            out.append({
                "rank": rank,
                "score": float(s),
                "profile": {
                    "name": p.name,
                    "title": p.title,
                    "company": p.company,
                    "location": p.location,
                    "summary": (p.summary[:200] + "...") if len(p.summary) > 200 else p.summary,
                    "skills": p.skills[:10],
                    "connections": p.connections
                }
            })
        return out

    def _extract_popular_skills(self, profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cnt: Dict[str, int] = {}
        for r in profiles:
            for s in r["profile"].get("skills", []):
                cnt[s] = cnt.get(s, 0) + 1
        return [{"skill": k, "count": v} for k, v in sorted(cnt.items(), key=lambda x: x[1], reverse=True)[:10]]

    def _extract_target_companies(self, profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cnt: Dict[str, int] = {}
        for r in profiles:
            c = r["profile"].get("company") or ""
            if c:
                cnt[c] = cnt.get(c, 0) + 1
        return [{"company": k, "count": v} for k, v in sorted(cnt.items(), key=lambda x: x[1], reverse=True)[:10]]

    def _extract_career_paths(self, profiles: List[Dict[str, Any]]) -> List[str]:
        titles = [r["profile"].get("title","") for r in profiles if r["profile"].get("title")]
        # unique + top
        return list(dict.fromkeys(titles))[:10]

    def _extract_locations(self, profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cnt: Dict[str, int] = {}
        for r in profiles:
            loc = r["profile"].get("location") or ""
            if loc:
                cnt[loc] = cnt.get(loc, 0) + 1
        return [{"location": k, "count": v} for k, v in sorted(cnt.items(), key=lambda x: x[1], reverse=True)[:10]]

    def _extract_similar_titles(self, profiles: List[Dict[str, Any]], target_title: str) -> List[Dict[str, Any]]:
        target_lower = (target_title or "").lower()
        cnt: Dict[str, int] = {}
        for r in profiles:
            t = (r["profile"].get("title") or "").strip()
            if t and t.lower() != target_lower:
                cnt[t] = cnt.get(t, 0) + 1
        return [{"title": k, "count": v} for k, v in sorted(cnt.items(), key=lambda x: x[1], reverse=True)[:10]]

    def _extract_experience_levels(self, profiles: List[Dict[str, Any]]) -> Dict[str, int]:
        levels = {"junior":0, "intermediate":0, "senior":0, "expert":0}
        for r in profiles:
            t = (r["profile"].get("title") or "").lower()
            if any(w in t for w in ["junior","débutant","debutant","stagiaire"]): levels["junior"] += 1
            elif any(w in t for w in ["senior","lead","principal","expert"]):   levels["senior"] += 1
            elif any(w in t for w in ["manager","chef","responsable","directeur"]): levels["expert"] += 1
            else: levels["intermediate"] += 1
        return levels

    def _extract_related_sectors(self, profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cnt: Dict[str, int] = {}
        for r in profiles:
            c = (r["profile"].get("company") or "").lower()
            if not c: continue
            if any(w in c for w in ["bank","banque","crédit","credit","finance"]): sector = "Finance/Banque"
            elif any(w in c for w in ["tech","software","digital","it"]):          sector = "Technologie"
            elif any(w in c for w in ["consulting","conseil","advisory"]):         sector = "Conseil"
            elif any(w in c for w in ["telecom","télécommunication","telecommunication"]): sector = "Télécom"
            elif any(w in c for w in ["retail","commerce","vente"]):               sector = "Commerce/Retail"
            else: sector = "Autres"
            cnt[sector] = cnt.get(sector, 0) + 1
        return [{"sector": k, "count": v} for k, v in sorted(cnt.items(), key=lambda x: x[1], reverse=True)[:8]]

    # --------- Public insights (compat avec tes services) ---------
    def get_career_insights(self, user_goal: str, user_skills: List[str], sector: str) -> Dict[str, Any]:
        q = f"{user_goal} {sector} {' '.join(user_skills or [])}".strip()
        sims = self.search_profiles(q, top_k=10)
        return {
            "profiles_similaires": sims[:5],
            "competences_populaires": self._extract_popular_skills(sims),
            "entreprises_cibles": self._extract_target_companies(sims),
            "parcours_types": self._extract_career_paths(sims),
            "localisations": self._extract_locations(sims)
        }

    def get_salary_insights(self, job_title: str, location: str, experience_years: int, top_k: int = 155) -> Dict[str, Any]:
        q = f"{job_title} {location} {experience_years} ans expérience"
        sims = self.search_profiles(q, top_k=top_k)
        return {
            "profiles_similaires": sims,
            "total_profiles": len(sims),
            "competences_demandees": self._extract_popular_skills(sims),
            "entreprises_qui_recrutent": self._extract_target_companies(sims),
            "titres_similaires": self._extract_similar_titles(sims, job_title),
            "localisations_alternatives": self._extract_locations(sims),
            "niveaux_experience": self._extract_experience_levels(sims),
            "secteurs_connexes": self._extract_related_sectors(sims)
        }

    def search_salary_benchmarks(self, job_title: str, location: str, experience_years: int):
        queries = [
            f"{job_title} {location}",
            f"{job_title} {experience_years} ans",
            f"{job_title}",
            f"{location} {experience_years} ans expérience",
        ]
        all_p = []
        for q in queries:
            all_p.extend(self.search_profiles(q, top_k=10))
        seen = set(); uniq = []
        for r in all_p:
            name = r["profile"]["name"]
            if name not in seen:
                seen.add(name); uniq.append(r)
        return uniq[:20]


# Instance globale (nom inchangé)
linkedin_rag = LinkedInRAGService()
