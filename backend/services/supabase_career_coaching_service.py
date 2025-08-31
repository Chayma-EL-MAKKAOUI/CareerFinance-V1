# services/supabase_career_coaching_service.py
import os, re, json
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# ==================== CONFIG ====================
SUPABASE_URL = os.getenv("SUPABASE_URL")
<<<<<<< HEAD
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
=======
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
>>>>>>> 5e0de77 (Auth commit)

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL et SUPABASE_KEY doivent être définis dans .env")

# Initialiser le client Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Base du projet
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

# Modèle multilingue FR/EN (dim=768 par défaut)
EMBED_MODEL = os.getenv("CAREER_EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-mpnet-base-v2")

# Chemins FAISS
INDEX_PATH = os.getenv("CAREER_FAISS_INDEX", os.path.join(PROJECT_ROOT, "data", "supabase_career_index.faiss"))
MAP_PATH   = os.getenv("CAREER_FAISS_MAP",   os.path.join(PROJECT_ROOT, "data", "supabase_career_index_map.json"))
os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)

# ==================== HELPERS ====================
def normalize_ws(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def simple_sentence_split(text: str) -> List[str]:
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        return []
    ABBRS = {"M.", "Mme.", "Dr.", "Pr.", "etc.", "p.", "n°"}
    tokens = text.split()
    sents, buf = [], []
    for tok in tokens:
        buf.append(tok)
        end_punct = re.search(r"[.!?]$", tok) is not None
        if end_punct and tok not in ABBRS:
            sents.append(" ".join(buf))
            buf = []
    if buf:
        sents.append(" ".join(buf))
    return sents

def chunk_by_sentences(text: str, max_chars: int = 1200, overlap_chars: int = 200) -> List[str]:
    sents = simple_sentence_split(text)
    chunks: List[str] = []
    buf = ""
    for sent in sents:
        if len(buf) + len(sent) + 1 <= max_chars:
            buf = (buf + " " + sent).strip()
        else:
            if buf:
                chunks.append(buf)
                buf = buf[-overlap_chars:] if overlap_chars > 0 and len(buf) > overlap_chars else ""
            if len(sent) > max_chars:
                for i in range(0, len(sent), max_chars):
                    part = sent[i:i+max_chars]
                    if part:
                        chunks.append(part)
                buf = ""
            else:
                buf = sent
    if buf:
        chunks.append(buf)
    return chunks

def parse_embedding(raw) -> Optional[np.ndarray]:
    """Accepte list[float] OU str '[...]' renvoyée par PostgREST. Retourne np.float32 ou None."""
    if raw is None:
        return None
    if isinstance(raw, list):
        try:
            return np.asarray(raw, dtype=np.float32)
        except Exception:
            return None
    if isinstance(raw, str):
        s = raw.strip()
        try:
            if s.startswith('[') and s.endswith(']'):
                arr = json.loads(s)
                return np.asarray(arr, dtype=np.float32)
            # fallback split simple
            s = s.replace('[', '').replace(']', '')
            vals = [v for v in (x.strip() for x in s.split(',')) if v]
            return np.asarray([float(v) for v in vals], dtype=np.float32)
        except Exception:
            return None
    # types inattendus
    return None

# ==================== DATACLASSES ====================
@dataclass
class ProfileHit:
    profile_id: int
    score: float
    nom: str
    titre: str
    formation: str
    url: str

@dataclass
class ChunkHit:
    chunk_id: int
    profile_id: int
    score: float
    content: str
    section: str
    nom: str
    titre: str

# ==================== SERVICE ====================
class SupabaseCareerCoachingService:
    def __init__(self):
        self.model = SentenceTransformer(EMBED_MODEL)
        self.dim = self.model.get_sentence_embedding_dimension()
        self.index: Optional[faiss.Index] = None
        self.chunk_map: Dict[int, Dict] = {}
        self.profile_map: Dict[int, Dict] = {}
        self.id_by_pos: List[int] = []  # mapping FAISS position -> chunk_id

    # ----------- Chargements depuis Supabase -----------
    def load_profiles_from_supabase(self) -> List[Dict]:
        try:
            response = supabase.table("profileslinkedin").select("*").execute()
            profiles = response.data or []
            print(f"✅ {len(profiles)} profils LinkedIn chargés depuis Supabase")
            return profiles
        except Exception as e:
            print(f"❌ Erreur lors du chargement des profils: {e}")
            return []

    def load_chunks_from_supabase(self) -> List[Dict]:
        try:
            response = supabase.table("profile_chunks").select("*").execute()
            chunks = response.data or []
            # parser embeddings ici
            ok, bad_dim, bad_none = 0, 0, 0
            for c in chunks:
                vec = parse_embedding(c.get("embedding"))
                if vec is None:
                    c["embedding"] = None
                    bad_none += 1
                    continue
                if vec.shape[0] != self.dim:
                    # dimension incompatible → ignore
                    c["embedding"] = None
                    bad_dim += 1
                    continue
                c["embedding"] = vec.astype(np.float32, copy=False)
                ok += 1
            print(f"✅ {len(chunks)} chunks chargés (ok: {ok}, dim_mismatch: {bad_dim}, vides: {bad_none})")
            return chunks
        except Exception as e:
            print(f"❌ Erreur lors du chargement des chunks: {e}")
            return []

    # ----------- Création des chunks + embeddings -----------
    def process_and_chunk_profiles(self) -> bool:
        try:
            profiles_response = supabase.table("profileslinkedin").select("*").execute()
            profiles = profiles_response.data or []
            if not profiles:
                print("❌ Aucun profil LinkedIn trouvé")
                return False

            print(f"🔄 Traitement de {len(profiles)} profils LinkedIn...")
            for profile in profiles:
                profile_id = profile["id"]

                competences_response = supabase.table("competences").select("*").eq("profile_id", profile_id).execute()
                competences = [comp["competence"] for comp in (competences_response.data or [])]

                experiences_response = supabase.table("experiences").select("*").eq("profile_id", profile_id).execute()
                experiences = experiences_response.data or []

                profile_content = self._build_profile_content(profile, competences, experiences)
                chunks = chunk_by_sentences(profile_content, max_chars=1200, overlap_chars=200)

                for i, chunk_content in enumerate(chunks):
                    if len(chunk_content.strip()) > 50:  # ignorer trop courts
                        emb = self.model.encode([chunk_content])[0].astype(np.float32)
                        chunk_data = {
                            "profile_id": profile_id,
                            "chunk_idx": i,
                            "section": f"profile_{i}",
                            "content": chunk_content,
                            "embedding": emb.tolist(),  # JSON-friendly
                            "token_count": len(chunk_content.split()),
                            "created_at": datetime.now().isoformat()
                        }
                        try:
                            supabase.table("profile_chunks").insert(chunk_data).execute()
                        except Exception as e:
                            print(f"⚠️ Erreur insertion chunk pour profil {profile_id}: {e}")
                            continue

            print(f"✅ Chunking et embedding terminés pour {len(profiles)} profils")
            return True

        except Exception as e:
            print(f"❌ Erreur lors du traitement des profils: {e}")
            return False

    def _build_profile_content(self, profile: Dict, competences: List[str], experiences: List[Dict]) -> str:
        parts = []
        if profile.get("nom"):
            parts.append(f"Nom: {profile['nom']}")
        if profile.get("titre"):
            parts.append(f"Titre: {profile['titre']}")
        if profile.get("formation"):
            parts.append(f"Formation: {profile['formation']}")
        if competences:
            parts.append(f"Compétences: {', '.join(competences)}")
        for exp in (experiences or []):
            exp_text = []
            if exp.get("poste"):
                exp_text.append(f"Poste: {exp['poste']}")
            if exp.get("entreprise"):
                exp_text.append(f"Entreprise: {exp['entreprise']}")
            if exp.get("periode"):
                exp_text.append(f"Période: {exp['periode']}")
            if exp.get("localisation"):
                exp_text.append(f"Localisation: {exp['localisation']}")
            if exp.get("description"):
                exp_text.append(f"Description: {exp['description']}")
            if exp_text:
                parts.append("Expérience: " + " | ".join(exp_text))
        return "\n\n".join(parts)

    # ----------- Sauvegarde sessions coaching -----------
    def save_coaching_session(self, user_id: int, objectif: str, competences: List[str],
                              secteur: str, plan_data: Dict[str, Any]) -> int:
        try:
            session_data = {
                "user_id": user_id,
                "objectif": objectif,
                "competences": json.dumps(competences),
                "secteur": secteur,
                "created_at": datetime.now().isoformat()
            }
            response = supabase.table("coaching_sessions").insert(session_data).execute()
            session_id = response.data[0]["id"]

            if "plan_carriere" in plan_data or "etapes" in plan_data:
                self._save_plan_carriere(session_id, plan_data)
            if "formations" in plan_data or "formations_recommandees" in plan_data:
                self._save_formations(session_id, plan_data)
            if "negociations" in plan_data or "conseils_negociations" in plan_data:
                self._save_negociations(session_id, plan_data)

            print(f"✅ Session complète sauvegardée avec l'ID: {session_id}")
            return session_id

        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde de la session: {e}")
            raise

    def _save_plan_carriere(self, session_id: int, plan_data: Dict):
        """
        Sauvegarde 1 ligne par ÉTAPE dans public.plan_carriere :
        - title (étape.titre)
        - description
        - competences (JSON string)
        - duree (string)
        - salaire (numeric)
        """
        try:
            # 1) Récupérer la source du plan
            plan_src = plan_data.get("plan_carriere")
            steps: List[Dict] = []

            # Cas A : plan_carriere = dict avec etapes
            if isinstance(plan_src, dict):
                steps = plan_src.get("etapes") or plan_src.get("steps") or []
            # Cas B : plan_carriere = list d'étapes directement
            elif isinstance(plan_src, list):
                steps = plan_src
            # Cas C : certains prompts renvoient "etapes" à la racine
            if not steps and isinstance(plan_data.get("etapes"), list):
                steps = plan_data["etapes"]

            if not steps:
                # rien à sauver -> on sort proprement
                print("ℹ️ Aucune étape à sauvegarder dans plan_carriere")
                return

            # 2) Insérer chaque étape
            for i, etape in enumerate(steps, start=1):
                if not isinstance(etape, dict):
                    continue

                titre = etape.get("titre") or f"Étape {i}"
                description = etape.get("description", "")

                # alias compétences : competences / competencesRequises
                comps = (
                    etape.get("competences") or
                    etape.get("competencesRequises") or
                    []
                )
                if not isinstance(comps, list):
                    # au cas où l'LLM renvoie une string
                    comps = [str(comps)]

                # alias salaire : salaire / salaireEstime
                salaire_val = etape.get("salaire", None)
                if salaire_val is None:
                    salaire_val = etape.get("salaireEstime", None)
                try:
                    salaire_num = float(salaire_val) if salaire_val is not None else None
                except Exception:
                    salaire_num = None

                row = {
                    "coaching_session_id": session_id,
                    "title": titre,
                    "description": description,
                    "competences": json.dumps(comps, ensure_ascii=False),
                    "duree": etape.get("duree", ""),
                    "salaire": salaire_num,
                }

                try:
                    supabase.table("plan_carriere").insert(row).execute()
                    print(f"✅ Étape sauvegardée: {titre}")
                except Exception as e:
                    print(f"⚠️ Erreur insertion étape '{titre}': {e}")

        except Exception as e:
            print(f"⚠️ Erreur sauvegarde plan carrière: {e}")

    def _save_formations(self, session_id: int, plan_data: Dict):
        try:
            formations = plan_data.get("formations") or plan_data.get("formations_recommandees")
            if not formations:
                return
            if isinstance(formations, list):
                for formation in formations:
                    if isinstance(formation, dict):
                        formation_data = {
                            "coaching_session_id": session_id,
                            "title": formation.get("titre", formation.get("nom", "")),
                            "description": formation.get("description", ""),
                            "duree": formation.get("duree", ""),
                            "niveau_priorite": formation.get("priorite", formation.get("niveau", "")),
                        }
                        supabase.table("formation").insert(formation_data).execute()
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde formations: {e}")

    def _save_negociations(self, session_id: int, plan_data: Dict):
        try:
            negociations = plan_data.get("negociations") or plan_data.get("conseils_negociations")
            if not negociations:
                return
            if isinstance(negociations, dict):
                negociations_data = {
                    "coaching_session_id": session_id,
                    "description": json.dumps(negociations),
                    "point_a_discuter": json.dumps(negociations.get("points_cles", [])),
                    "arguments_cles": json.dumps(negociations.get("arguments", [])),
                    "conseils": json.dumps(negociations.get("conseils", [])),
                }
            else:
                negociations_data = {
                    "coaching_session_id": session_id,
                    "description": str(negociations),
                    "point_a_discuter": "[]",
                    "arguments_cles": "[]",
                    "conseils": "[]",
                }
            supabase.table("negociations").insert(negociations_data).execute()
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde négociation: {e}")

    def get_coaching_history(self, user_id: int) -> List[Dict]:
        try:
            sessions_response = supabase.table("coaching_sessions").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            sessions = sessions_response.data or []
            for session in sessions:
                sid = session["id"]
                plans_response = supabase.table("plan_carriere").select("*").eq("coaching_session_id", sid).execute()
                session["plans_carriere"] = plans_response.data or []
                formations_response = supabase.table("formation").select("*").eq("coaching_session_id", sid).execute()
                session["formations"] = formations_response.data or []
                negociationss_response = supabase.table("negociations").select("*").eq("coaching_session_id", sid).execute()
                session["negociations"] = negociationss_response.data or []
            return sessions
        except Exception as e:
            print(f"❌ Erreur lors de la récupération de l'historique: {e}")
            return []

    # ----------- FAISS : build / load / search -----------
    def build_index_from_supabase(self):
        try:
            chunks = self.load_chunks_from_supabase()
            if not chunks:
                print("📝 Aucun chunk trouvé, création des chunks...")
                if not self.process_and_chunk_profiles():
                    raise ValueError("Échec de la création des chunks")
                chunks = self.load_chunks_from_supabase()
            if not chunks:
                raise ValueError("Impossible de créer ou charger les chunks")

            profiles = self.load_profiles_from_supabase()
            if not profiles:
                raise ValueError("Aucun profil trouvé")

            self.profile_map = {p["id"]: p for p in profiles}
            self.chunk_map = {c["id"]: c for c in chunks}

            embeddings: List[np.ndarray] = []
            chunk_ids: List[int] = []

            for c in chunks:
                vec = c.get("embedding")
                if isinstance(vec, np.ndarray) and vec.shape[0] == self.dim:
                    embeddings.append(vec.astype(np.float32, copy=False))
                    chunk_ids.append(c["id"])
                else:
                    content = (c.get("content") or "").strip()
                    if len(content) > 10:
                        emb = self.model.encode([content])[0].astype(np.float32)
                        embeddings.append(emb)
                        chunk_ids.append(c["id"])
                        try:
                            supabase.table("profile_chunks").update({"embedding": emb.tolist()}).eq("id", c["id"]).execute()
                        except Exception as e:
                            print(f"⚠️ Erreur mise à jour embedding chunk {c['id']}: {e}")

            if not embeddings:
                raise ValueError("Aucun embedding valide trouvé")

            X = np.stack(embeddings, axis=0).astype(np.float32)
            if X.shape[1] != self.dim:
                raise ValueError(f"Dimension FAISS {X.shape[1]} != modèle {self.dim}")

            # Cosine via produit scalaire
            faiss.normalize_L2(X)
            self.index = faiss.IndexFlatIP(self.dim)
            self.index.add(X)
            self.id_by_pos = chunk_ids[:]  # alignement position -> chunk_id

            # Sauvegardes
            faiss.write_index(self.index, INDEX_PATH)
            with open(MAP_PATH, "w", encoding="utf-8") as f:
                json.dump({
                    "id_by_pos": self.id_by_pos,
                    "created_at": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)

            print(f"✅ Index FAISS créé avec {len(embeddings)} chunks")
            return True

        except Exception as e:
            print(f"❌ Erreur lors de la création de l'index: {e}")
            return False

    def load_index(self) -> bool:
        try:
            if not os.path.exists(INDEX_PATH) or not os.path.exists(MAP_PATH):
                return False

            self.index = faiss.read_index(INDEX_PATH)
            with open(MAP_PATH, "r", encoding="utf-8") as f:
                mapping_data = json.load(f)

            self.id_by_pos = mapping_data.get("id_by_pos") or []

            # Recharger les maps depuis Supabase (plus robuste que de les sérialiser)
            profiles = self.load_profiles_from_supabase()
            chunks = self.load_chunks_from_supabase()
            self.profile_map = {p["id"]: p for p in profiles}
            self.chunk_map = {c["id"]: c for c in chunks}

            print(f"✅ Index FAISS chargé avec {self.index.ntotal} vecteurs")
            return True

        except Exception as e:
            print(f"❌ Erreur lors du chargement de l'index: {e}")
            return False

    def _ids_from_indices(self, idxs: np.ndarray) -> List[int]:
        ids = []
        for i in idxs:
            if 0 <= i < len(self.id_by_pos):
                ids.append(self.id_by_pos[i])
        return ids

    def search_similar_profiles(self, query: str, top_k: int = 10) -> List[ProfileHit]:
        if not self.index or not self.chunk_map:
            raise ValueError("Index non initialisé")

        q = self.model.encode([query]).astype(np.float32)
        faiss.normalize_L2(q)
        scores, indices = self.index.search(q, top_k * 2)

        profile_scores: Dict[int, List[float]] = {}
        id_list = self._ids_from_indices(indices[0])

        for score, chunk_id in zip(scores[0], id_list):
            chunk = self.chunk_map.get(chunk_id)
            if not chunk:
                continue
            pid = chunk.get("profile_id")
            if pid is None:
                continue
            profile_scores.setdefault(pid, []).append(float(score))

        results: List[ProfileHit] = []
        for pid, s_list in profile_scores.items():
            prof = self.profile_map.get(pid)
            if not prof:
                continue
            avg = float(np.mean(s_list)) if s_list else 0.0
            results.append(ProfileHit(
                profile_id=pid,
                score=avg,
                nom=prof.get("nom", ""),
                titre=prof.get("titre", ""),
                formation=prof.get("formation", ""),
                url=prof.get("url", "")
            ))

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def search_relevant_chunks(self, query: str, top_k: int = 10) -> List[ChunkHit]:
        if not self.index or not self.chunk_map:
            raise ValueError("Index non initialisé")

        q = self.model.encode([query]).astype(np.float32)
        faiss.normalize_L2(q)
        scores, indices = self.index.search(q, top_k)

        results: List[ChunkHit] = []
        id_list = self._ids_from_indices(indices[0])

        for score, chunk_id in zip(scores[0], id_list):
            chunk = self.chunk_map.get(chunk_id)
            if not chunk:
                continue
            pid = chunk.get("profile_id")
            prof = self.profile_map.get(pid, {})
            results.append(ChunkHit(
                chunk_id=chunk_id,
                profile_id=pid,
                score=float(score),
                content=chunk.get("content", ""),
                section=chunk.get("section", ""),
                nom=prof.get("nom", ""),
                titre=prof.get("titre", "")
            ))
        return results

    def get_rag_context(self, query: str, top_k: int = 5) -> str:
        try:
            chunks = self.search_relevant_chunks(query, top_k)
            parts = []
            for ch in chunks:
                parts.append(
                    f"\nProfil: {ch.nom} - {ch.titre}\n"
                    f"Section: {ch.section}\n"
                    f"Contenu: {ch.content}\n"
                    f"Score de pertinence: {ch.score:.3f}\n"
                )
            return "\n" + "="*50 + "".join(parts)
        except Exception as e:
            print(f"❌ Erreur génération contexte RAG: {e}")
            return ""

    def get_career_insights(self, query: str, skills: List[str], sector: str) -> Dict[str, Any]:
        try:
            combined_query = f"{query} {sector} {' '.join(skills)}".strip()
            rag_context = self.get_rag_context(combined_query, top_k=10)
            profiles = self.search_similar_profiles(combined_query, top_k=20)
            chunks = self.search_relevant_chunks(combined_query, top_k=10)

            insights = {
                "profiles_analyzed": len(profiles),
                "rag_context": rag_context,
                "top_profiles": [
                    {"nom": p.nom, "titre": p.titre, "score": p.score, "url": p.url}
                    for p in profiles[:10]
                ],
                "relevant_chunks": [
                    {"content": c.content[:200] + "...", "nom": c.nom, "titre": c.titre,
                     "section": c.section, "score": c.score}
                    for c in chunks[:5]
                ],
                "sector_analysis": {
                    "total_profiles": len(profiles),
                    "avg_score": float(np.mean([p.score for p in profiles])) if profiles else 0.0,
                    "top_titles": list({p.titre for p in profiles[:20] if p.titre})
                }
            }
            return insights
        except Exception as e:
            print(f"❌ Erreur lors de l'analyse des insights: {e}")
            return {"error": str(e)}

# Instance globale du service
career_coaching_service = SupabaseCareerCoachingService()
