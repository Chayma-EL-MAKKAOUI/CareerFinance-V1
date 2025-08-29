# services/doc_rag_service.py
import os, re, json
from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import faiss
import psycopg2
import psycopg2.extras
from sentence_transformers import SentenceTransformer

# ==================== CONFIG ====================
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", "5433"))
PG_DB   = os.getenv("PG_DB", "mydb")
PG_USER = os.getenv("PG_USER", "admin")
PG_PASS = os.getenv("PG_PASS", "admin")

def pg_conn():
    return psycopg2.connect(
        host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PASS
    )

# Base du projet (chemin du fichier courant)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

# Modèle multilingue FR/EN (dim=768)
EMBED_MODEL = os.getenv("DOC_EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-mpnet-base-v2")

# Chemins FAISS ABSOLUS
INDEX_PATH = os.getenv("DOC_FAISS_INDEX", os.path.join(PROJECT_ROOT, "data", "doc_index.faiss"))
MAP_PATH   = os.getenv("DOC_FAISS_MAP",   os.path.join(PROJECT_ROOT, "data", "doc_index_map.json"))
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

class DocRAGService:
    def __init__(self):
        self.model = SentenceTransformer(EMBED_MODEL)
        self.dim = self.model.get_sentence_embedding_dimension()
        if self.dim != 768:
            print(f"[DocRAG] Embedding dimension = {self.dim}")
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

    # ---------- 1) CHUNKING ----------
    def chunk_and_store_documents(self, max_chars: int = 1200, overlap_chars: int = 200, limit: Optional[int] = None):
        with pg_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            q = "SELECT id, title, text, url, source FROM public.documents ORDER BY retrieved_at"
            if limit:
                q += f" LIMIT {int(limit)}"
            cur.execute(q)
            docs = cur.fetchall()

            inserted_total = 0
            for d in docs:
                doc_id = d["id"]
                body   = d["text"]
                if not body or not normalize_ws(body):
                    continue

                # déjà chunké ?
                cur.execute("SELECT 1 FROM public.chunks WHERE doc_id = %s LIMIT 1;", (doc_id,))
                if cur.fetchone():
                    continue

                parts = chunk_by_sentences(body, max_chars=max_chars, overlap_chars=overlap_chars)
                ord_ = 0
                for part in parts:
                    part = normalize_ws(part)
                    if not part:
                        continue
                    cur.execute("""
                        INSERT INTO public.chunks (id, doc_id, ord, n_chars, n_words, text)
                        VALUES (gen_random_uuid(), %s, %s, %s, %s, %s);
                    """, (doc_id, ord_, len(part), len(part.split()), part))
                    ord_ += 1
                    inserted_total += 1
            print(f"[DocRAG] Chunks insérés: {inserted_total}")
        return {"inserted_chunks": inserted_total}

    # ---------- 2) EMBEDDINGS ----------
    def embed_new_chunks(self, batch_size: int = 64):
        with pg_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
               SELECT id, text
               FROM public.chunks
               WHERE embedding IS NULL
               ORDER BY created_at NULLS FIRST, ord ASC
            """)
            rows = cur.fetchall()

            total = 0
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i+batch_size]
                texts = [r["text"] for r in batch]
                embs = self.model.encode(
                    texts, convert_to_numpy=True, normalize_embeddings=True
                ).astype("float32")

                for r, v in zip(batch, embs):
                    vec_str = "[" + ",".join(f"{float(x):.6f}" for x in v.tolist()) + "]"
                    cur.execute(
                        "UPDATE public.chunks SET embedding = %s WHERE id = %s;",
                        (vec_str, r["id"])
                    )
                conn.commit()
                total += len(batch)

            print(f"[DocRAG] embeddings générés pour {total} chunks")
            return {"embedded_chunks": total}

    # ---------- 3) FAISS ----------
    def build_or_load_faiss(self) -> bool:
        # 1) Essayer depuis disque
        try:
            if os.path.exists(INDEX_PATH) and os.path.exists(MAP_PATH):
                self.index = faiss.read_index(INDEX_PATH)
                with open(MAP_PATH, "r", encoding="utf-8") as f:
                    self.id_map = json.load(f)
                print("[DocRAG] FAISS index chargé depuis disque")
                return True
        except Exception as e:
            print("[DocRAG] load FAISS error:", e)

        # helper local
        def _to_vec(emb_val):
            if emb_val is None:
                return None
            if isinstance(emb_val, (list, tuple, np.ndarray)):
                return np.asarray(emb_val, dtype="float32")
            if isinstance(emb_val, (bytes, bytearray, memoryview)):
                return np.frombuffer(bytes(emb_val), dtype="float32")
            if isinstance(emb_val, str):
                s = emb_val.strip().strip("[]")
                if not s:
                    return None
                try:
                    vals = [float(x) for x in s.split(",") if x.strip()]
                    return np.asarray(vals, dtype="float32")
                except Exception as e:
                    print("[DocRAG] parse string embedding error:", e)
                    return None
            try:
                return np.asarray(emb_val, dtype="float32")
            except Exception:
                return None

        # 2) Lire depuis PostgreSQL
        with pg_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                SELECT id, embedding
                FROM public.chunks
                WHERE embedding IS NOT NULL
                ORDER BY doc_id, ord;
            """)
            rows = cur.fetchall()
            if not rows:
                print("[DocRAG] Aucun embedding trouvé en base")
                return False

            ids, mats = [], []
            for cid, emb in rows:
                v = _to_vec(emb)
                if v is None:
                    continue
                ids.append(str(cid))
                mats.append(v)

            if not mats:
                print("[DocRAG] Tous les embeddings lus sont vides/invalides")
                return False

        # 3) Construire l’index FAISS
        X = np.vstack(mats).astype("float32")
        faiss.normalize_L2(X)
        index = faiss.IndexFlatIP(X.shape[1])
        index.add(X)

        self.index = index
        self.id_map = ids  # LISTE ordonnée (alignée avec add)
        faiss.write_index(index, INDEX_PATH)
        with open(MAP_PATH, "w", encoding="utf-8") as f:
            json.dump(self.id_map, f)

        print(f"[DocRAG] FAISS construit: {X.shape[0]} vecteurs, dim={X.shape[1]}")
        return True

    # ---------- 4) SEARCH ----------
    def _fetch_chunk_meta(self, chunk_id: str) -> dict:
        with pg_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
                SELECT c.id AS chunk_id, c.text, c.doc_id, c.ord, d.title, d.url, d.source
                FROM public.chunks c
                JOIN public.documents d ON d.id = c.doc_id
                WHERE c.id = %s
            """, (chunk_id,))
            r = cur.fetchone()
            if not r:
                return {}
            return {
                "chunk_id": str(r["chunk_id"]),
                "text": r["text"] or "",
                "doc_id": str(r["doc_id"]),
                "ord": int(r["ord"]),
                "title": r.get("title") if isinstance(r, dict) else r["title"],
                "url": r.get("url") if isinstance(r, dict) else r["url"],
                "source": r.get("source") if isinstance(r, dict) else r["source"],
            }

    # ---------- 4) SEARCH ----------
    def search(self, query: str, top_k: int = 6) -> list[dict]:
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
doc_rag = DocRAGService()
