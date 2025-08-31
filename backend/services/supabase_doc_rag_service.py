# services/supabase_doc_rag_service.py
import os, re, json
from dataclasses import dataclass
from typing import List, Optional
import uuid

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
    raise ValueError("❌ SUPABASE_URL et SUPABASE_KEY doivent être définis dans .env")

# Initialiser le client Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Base du projet (chemin du fichier courant)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

# Modèle multilingue FR/EN (dim=768)
EMBED_MODEL = os.getenv("DOC_EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-mpnet-base-v2")

# Chemins FAISS ABSOLUS pour Supabase
INDEX_PATH = os.getenv("DOC_FAISS_INDEX", os.path.join(PROJECT_ROOT, "data", "supabase_doc_index.faiss"))
MAP_PATH   = os.getenv("DOC_FAISS_MAP",   os.path.join(PROJECT_ROOT, "data", "supabase_doc_index_map.json"))
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

# ==================== SERVICE ====================
@dataclass
class ChunkHit:
    chunk_id: str
    score: float
    text: str
    doc_id: str
    title: Optional[str]
    url: Optional[str]
    source: Optional[str]
    ord: int

class SupabaseDocRAGService:
    def __init__(self):
        self.model = SentenceTransformer(EMBED_MODEL)
        self.dim = self.model.get_sentence_embedding_dimension()
        if self.dim != 768:
            print(f"[SupabaseDocRAG] Embedding dimension = {self.dim}")
        self.index: Optional[faiss.Index] = None
        self.id_map: List[str] = []  # map: faiss row -> chunk_id

    # ---------- UTIL: encode requête ----------
    def embed_text(self, text: str) -> np.ndarray:
        """Encode un texte en vecteur float32 normalisé (cosine-ready)."""
        if text is None:
            text = ""
        vec = self.model.encode(
            [text], convert_to_numpy=True, normalize_embeddings=True
        ).astype("float32")
        return vec[0]  # (dim,)

    # ---------- 1) STORE USER DOCUMENT ----------
    def store_user_document(self, title: str, text: str, user_id: int = 1, 
                          url: str = None, storage_path: str = None, 
                          mime_type: str = None, source: str = "user_upload") -> str:
        """
        Stocke un document utilisateur dans la table documents de Supabase
        Retourne l'ID du document créé
        """
        try:
            doc_data = {
                "user_id": user_id,
                "title": title,
                "text": text,
                "url": url,
                "storage_path": storage_path,
                "mime_type": mime_type,
                "source": source,
                "type": "user_document"
            }
            
            result = supabase.table("documents").insert(doc_data).execute()
            
            if result.data and len(result.data) > 0:
                doc_id = result.data[0]["id"]
                print(f"[SupabaseDocRAG] Document stocké avec ID: {doc_id}")
                return str(doc_id)
            else:
                raise Exception("Aucune donnée retournée lors de l'insertion")
                
        except Exception as e:
            print(f"[SupabaseDocRAG] Erreur lors du stockage du document: {e}")
            raise e

    # ---------- 2) CHUNKING ----------
    def chunk_and_store_documents(self, max_chars: int = 1200, overlap_chars: int = 200, 
                                limit: Optional[int] = None, doc_id: Optional[str] = None):
        """
        Chunke les documents depuis Supabase et stocke les chunks dans doc_chunks
        Si doc_id est fourni, ne traite que ce document
        """
        try:
            # Construire la requête
            query = supabase.table("documents").select("id, title, text, url, source")
            
            if doc_id:
                query = query.eq("id", doc_id)
            else:
                query = query.order("created_at")
                if limit:
                    query = query.limit(limit)
            
            result = query.execute()
            docs = result.data
            
            inserted_total = 0
            for d in docs:
                doc_id_current = d["id"]
                body = d["text"]
                if not body or not normalize_ws(body):
                    continue

                # Vérifier si déjà chunké
                existing_chunks = supabase.table("doc_chunks").select("id").eq("doc_id", doc_id_current).limit(1).execute()
                if existing_chunks.data:
                    continue

                parts = chunk_by_sentences(body, max_chars=max_chars, overlap_chars=overlap_chars)
                
                for ord_, part in enumerate(parts):
                    part = normalize_ws(part)
                    if not part:
                        continue
                    
                    chunk_data = {
                        "doc_id": doc_id_current,
                        "chunk_idx": ord_,
                        "content": part,
                        "token_count": len(part.split())
                    }
                    
                    supabase.table("doc_chunks").insert(chunk_data).execute()
                    inserted_total += 1
                    
            print(f"[SupabaseDocRAG] Chunks insérés: {inserted_total}")
            return {"inserted_chunks": inserted_total}
            
        except Exception as e:
            print(f"[SupabaseDocRAG] Erreur lors du chunking: {e}")
            raise e

    # ---------- 3) EMBEDDINGS ----------
    def embed_new_chunks(self, batch_size: int = 64):
        """
        Génère les embeddings pour les chunks qui n'en ont pas encore
        """
        try:
            # Récupérer les chunks sans embedding
            result = supabase.table("doc_chunks").select("id, content").is_("embedding", "null").order("created_at").execute()
            rows = result.data
            
            total = 0
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i+batch_size]
                texts = [r["content"] for r in batch]
                embs = self.model.encode(
                    texts, convert_to_numpy=True, normalize_embeddings=True
                ).astype("float32")

                for r, v in zip(batch, embs):
                    # Convertir l'embedding en liste pour Supabase
                    embedding_list = v.tolist()
                    
                    supabase.table("doc_chunks").update({
                        "embedding": embedding_list
                    }).eq("id", r["id"]).execute()
                    
                total += len(batch)

            print(f"[SupabaseDocRAG] embeddings générés pour {total} chunks")
            return {"embedded_chunks": total}
            
        except Exception as e:
            print(f"[SupabaseDocRAG] Erreur lors de la génération d'embeddings: {e}")
            raise e

    # ---------- 4) FAISS ----------
    def build_or_load_faiss(self) -> bool:
        # 1) Essayer depuis disque
        try:
            if os.path.exists(INDEX_PATH) and os.path.exists(MAP_PATH):
                self.index = faiss.read_index(INDEX_PATH)
                with open(MAP_PATH, "r", encoding="utf-8") as f:
                    self.id_map = json.load(f)
                print("[SupabaseDocRAG] FAISS index chargé depuis disque")
                return True
        except Exception as e:
            print("[SupabaseDocRAG] load FAISS error:", e)

        # 2) Lire depuis Supabase
        try:
            result = supabase.table("doc_chunks").select("id, embedding").not_.is_("embedding", "null").order("doc_id, chunk_idx").execute()
            rows = result.data
            
            if not rows:
                print("[SupabaseDocRAG] Aucun embedding trouvé en base")
                return False

            ids, mats = [], []
            for row in rows:
                chunk_id = str(row["id"])
                embedding = row["embedding"]
                
                if embedding is None:
                    continue
                    
                # Convertir l'embedding en numpy array
                v = np.asarray(embedding, dtype="float32")
                ids.append(chunk_id)
                mats.append(v)

            if not mats:
                print("[SupabaseDocRAG] Tous les embeddings lus sont vides/invalides")
                return False

        except Exception as e:
            print(f"[SupabaseDocRAG] Erreur lors de la lecture des embeddings: {e}")
            return False

        # 3) Construire l'index FAISS
        X = np.vstack(mats).astype("float32")
        faiss.normalize_L2(X)
        index = faiss.IndexFlatIP(X.shape[1])
        index.add(X)

        self.index = index
        self.id_map = ids  # LISTE ordonnée (alignée avec add)
        faiss.write_index(index, INDEX_PATH)
        with open(MAP_PATH, "w", encoding="utf-8") as f:
            json.dump(self.id_map, f)

        print(f"[SupabaseDocRAG] FAISS construit: {X.shape[0]} vecteurs, dim={X.shape[1]}")
        return True

    # ---------- 5) SEARCH ----------
    def _fetch_chunk_meta(self, chunk_id: str) -> dict:
        """
        Récupère les métadonnées d'un chunk depuis Supabase
        """
        try:
            # Convertir chunk_id en int si c'est une string numérique
            try:
                chunk_id_int = int(chunk_id)
            except (ValueError, TypeError):
                # Si ce n'est pas un entier, essayons de chercher par UUID dans une autre colonne
                # ou retournons un dict vide
                print(f"[SupabaseDocRAG] chunk_id {chunk_id} n'est pas un entier valide")
                return {}

            result = supabase.table("doc_chunks").select(
                "id, content, doc_id, chunk_idx, documents(title, url, source)"
            ).eq("id", chunk_id_int).execute()

            if not result.data:
                print(f"[SupabaseDocRAG] Aucun chunk trouvé avec l'ID {chunk_id_int}")
                return {}

            r = result.data[0]
            doc_info = r.get("documents", {})

            return {
                "chunk_id": str(r["id"]),
                "text": r["content"] or "",
                "doc_id": str(r["doc_id"]),
                "ord": int(r["chunk_idx"]),
                "title": doc_info.get("title"),
                "url": doc_info.get("url"),
                "source": doc_info.get("source"),
            }

        except Exception as e:
            print(f"[SupabaseDocRAG] Erreur lors de la récupération des métadonnées pour chunk {chunk_id}: {e}")
            return {}

    def search(self, query: str, top_k: int = 6) -> list[dict]:
        """
        Recherche dans l'index FAISS et retourne les chunks les plus pertinents
        """
        if self.index is None or not self.id_map:
            ok = self.build_or_load_faiss()
            if not ok:
               return []

        q = self.embed_text(query)[None, :]  # (1, dim)
        D, I = self.index.search(q.astype("float32"), top_k)

        out: list[dict] = []
        for faiss_idx, score in zip(I[0].tolist(), D[0].tolist()):
            if faiss_idx < 0 or faiss_idx >= len(self.id_map):
              continue
            cid = self.id_map[faiss_idx]
            m = self._fetch_chunk_meta(cid)
            if not m:
                continue
            out.append({
            "chunk_id": cid,
            "score": float(score),
            "text": m["text"],
            "doc_id": m["doc_id"],
            "title": m.get("title"),
            "url": m.get("url"),
            "source": m.get("source"),
            "ord": int(m["ord"]),
        })
        return out


# Instance globale
supabase_doc_rag = SupabaseDocRAGService()
