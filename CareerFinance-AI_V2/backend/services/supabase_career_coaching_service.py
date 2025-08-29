# services/supabase_career_coaching_service.py
import os, re, json
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import uuid
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
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ SUPABASE_URL et SUPABASE_KEY doivent être définis dans .env")

# Initialiser le client Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Base du projet (chemin du fichier courant)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

# Modèle multilingue FR/EN (dim=768)
EMBED_MODEL = os.getenv("CAREER_EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-mpnet-base-v2")

# Chemins FAISS ABSOLUS pour Supabase
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

# ==================== SERVICE ====================
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

class SupabaseCareerCoachingService:
    def __init__(self):
        self.model = SentenceTransformer(EMBED_MODEL)
        self.dim = self.model.get_sentence_embedding_dimension()
        if self.dim != 768:
            print(f"[SupabaseCareerCoaching] Embedding dimension = {self.dim}")
        self.index: Optional[faiss.Index] = None
        self.chunk_map: Dict[int, Dict] = {}
        self.profile_map: Dict[int, Dict] = {}
        
    def load_profiles_from_supabase(self) -> List[Dict]:
        """Charge tous les profils LinkedIn depuis Supabase"""
        try:
            response = supabase.table("profileslinkedin").select("*").execute()
            profiles = response.data
            print(f"✅ {len(profiles)} profils LinkedIn chargés depuis Supabase")
            return profiles
        except Exception as e:
            print(f"❌ Erreur lors du chargement des profils: {e}")
            return []
    
    def load_chunks_from_supabase(self) -> List[Dict]:
        """Charge tous les chunks de profils depuis Supabase"""
        try:
            response = supabase.table("profile_chunks").select("*").execute()
            chunks = response.data
            print(f"✅ {len(chunks)} chunks de profils chargés depuis Supabase")
            return chunks
        except Exception as e:
            print(f"❌ Erreur lors du chargement des chunks: {e}")
            return []
    
    def save_coaching_session(self, user_id: int, objectif: str, competences: List[str], 
                            secteur: str, plan_data: Dict[str, Any]) -> int:
        """Sauvegarde une session de coaching dans Supabase"""
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
            print(f"✅ Session de coaching sauvegardée avec l'ID: {session_id}")
            return session_id
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde de la session: {e}")
            raise
    
    def get_coaching_history(self, user_id: int) -> List[Dict]:
        """Récupère l'historique des sessions de coaching d'un utilisateur"""
        try:
            response = supabase.table("coaching_sessions").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            return response.data
        except Exception as e:
            print(f"❌ Erreur lors de la récupération de l'historique: {e}")
            return []
    
    def build_index_from_supabase(self):
        """Construit l'index FAISS à partir des données Supabase"""
        try:
            # Charger les profils et chunks
            profiles = self.load_profiles_from_supabase()
            chunks = self.load_chunks_from_supabase()
            
            if not profiles or not chunks:
                raise ValueError("Aucune donnée trouvée dans Supabase")
            
            # Créer les mappings
            self.profile_map = {p["id"]: p for p in profiles}
            self.chunk_map = {c["id"]: c for c in chunks}
            
            # Préparer les embeddings
            texts = []
            chunk_ids = []
            
            for chunk in chunks:
                content = chunk.get("content", "")
                if content and len(content.strip()) > 10:
                    texts.append(content)
                    chunk_ids.append(chunk["id"])
            
            if not texts:
                raise ValueError("Aucun contenu valide trouvé dans les chunks")
            
            # Générer les embeddings
            print(f"🔄 Génération des embeddings pour {len(texts)} chunks...")
            embeddings = self.model.encode(texts, show_progress_bar=True, batch_size=32)
            
            # Créer l'index FAISS
            self.index = faiss.IndexFlatIP(self.dim)
            self.index.add(embeddings.astype('float32'))
            
            # Sauvegarder l'index et le mapping
            faiss.write_index(self.index, INDEX_PATH)
            
            mapping_data = {
                "chunk_ids": chunk_ids,
                "profile_map": self.profile_map,
                "chunk_map": self.chunk_map,
                "created_at": datetime.now().isoformat()
            }
            
            with open(MAP_PATH, 'w', encoding='utf-8') as f:
                json.dump(mapping_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Index FAISS créé avec {len(texts)} chunks")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la création de l'index: {e}")
            return False
    
    def load_index(self) -> bool:
        """Charge l'index FAISS et les mappings"""
        try:
            if not os.path.exists(INDEX_PATH) or not os.path.exists(MAP_PATH):
                return False
            
            self.index = faiss.read_index(INDEX_PATH)
            
            with open(MAP_PATH, 'r', encoding='utf-8') as f:
                mapping_data = json.load(f)
            
            self.chunk_map = mapping_data["chunk_map"]
            self.profile_map = mapping_data["profile_map"]
            
            print(f"✅ Index FAISS chargé avec {self.index.ntotal} vecteurs")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement de l'index: {e}")
            return False
    
    def search_similar_profiles(self, query: str, top_k: int = 10) -> List[ProfileHit]:
        """Recherche des profils similaires basés sur le contenu"""
        if not self.index or not self.chunk_map:
            raise ValueError("Index non initialisé")
        
        # Encoder la requête
        query_embedding = self.model.encode([query])
        
        # Rechercher dans l'index
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k * 2)
        
        # Grouper par profil et calculer le score moyen
        profile_scores = {}
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunk_map):
                chunk_id = list(self.chunk_map.keys())[idx]
                chunk = self.chunk_map[chunk_id]
                profile_id = chunk["profile_id"]
                
                if profile_id not in profile_scores:
                    profile_scores[profile_id] = []
                profile_scores[profile_id].append(score)
        
        # Créer les résultats
        results = []
        for profile_id, scores_list in profile_scores.items():
            if profile_id in self.profile_map:
                profile = self.profile_map[profile_id]
                avg_score = np.mean(scores_list)
                
                results.append(ProfileHit(
                    profile_id=profile_id,
                    score=float(avg_score),
                    nom=profile.get("nom", ""),
                    titre=profile.get("titre", ""),
                    formation=profile.get("formation", ""),
                    url=profile.get("url", "")
                ))
        
        # Trier par score et limiter
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]
    
    def search_relevant_chunks(self, query: str, top_k: int = 10) -> List[ChunkHit]:
        """Recherche des chunks pertinents"""
        if not self.index or not self.chunk_map:
            raise ValueError("Index non initialisé")
        
        # Encoder la requête
        query_embedding = self.model.encode([query])
        
        # Rechercher dans l'index
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunk_map):
                chunk_id = list(self.chunk_map.keys())[idx]
                chunk = self.chunk_map[chunk_id]
                profile_id = chunk["profile_id"]
                
                if profile_id in self.profile_map:
                    profile = self.profile_map[profile_id]
                    
                    results.append(ChunkHit(
                        chunk_id=chunk_id,
                        profile_id=profile_id,
                        score=float(score),
                        content=chunk.get("content", ""),
                        section=chunk.get("section", ""),
                        nom=profile.get("nom", ""),
                        titre=profile.get("titre", "")
                    ))
        
        return results
    
    def get_career_insights(self, query: str, skills: List[str], sector: str) -> Dict[str, Any]:
        """Obtient des insights de carrière basés sur les données LinkedIn"""
        try:
            # Rechercher des profils dans le secteur
            sector_query = f"{sector} {query}"
            profiles = self.search_similar_profiles(sector_query, top_k=50)
            
            # Analyser les compétences
            skills_query = " ".join(skills)
            chunks = self.search_relevant_chunks(skills_query, top_k=20)
            
            # Extraire les insights
            insights = {
                "profiles_analyzed": len(profiles),
                "top_profiles": [
                    {
                        "nom": p.nom,
                        "titre": p.titre,
                        "score": p.score,
                        "url": p.url
                    } for p in profiles[:10]
                ],
                "relevant_chunks": [
                    {
                        "content": c.content[:200] + "...",
                        "nom": c.nom,
                        "titre": c.titre,
                        "section": c.section,
                        "score": c.score
                    } for c in chunks[:5]
                ],
                "sector_analysis": {
                    "total_profiles": len(profiles),
                    "avg_score": np.mean([p.score for p in profiles]) if profiles else 0,
                    "top_titles": list(set([p.titre for p in profiles[:20] if p.titre]))
                }
            }
            
            return insights
            
        except Exception as e:
            print(f"❌ Erreur lors de l'analyse des insights: {e}")
            return {"error": str(e)}

# Instance globale du service
career_coaching_service = SupabaseCareerCoachingService()
