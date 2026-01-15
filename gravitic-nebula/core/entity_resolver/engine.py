import logging
from typing import List, Dict, Optional, Tuple
from rapidfuzz import process, fuzz
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorBackend:
    def fit(self, texts: List[str]) -> None:
        return None

    def encode(self, texts: List[str]) -> np.ndarray:
        raise NotImplementedError

    def similarity(self, query_vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
        raise NotImplementedError


class SentenceTransformerBackend(VectorBackend):
    def __init__(self, model_name: str, device: str):
        self.model = SentenceTransformer(
            model_name,
            device=device,
            local_files_only=True,
        )

    def encode(self, texts: List[str]) -> np.ndarray:
        return np.asarray(self.model.encode(texts, convert_to_tensor=False, normalize_embeddings=True))

    def similarity(self, query_vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
        return (matrix @ query_vec.T).ravel()


class TfidfBackend(VectorBackend):
    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer()

    def fit(self, texts: List[str]) -> None:
        self.vectorizer.fit(texts)

    def encode(self, texts: List[str]) -> np.ndarray:
        return self.vectorizer.transform(texts).toarray()

    def similarity(self, query_vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
        return cosine_similarity(matrix, query_vec).ravel()


class HybridResolver:
    """
    SOTA Entity Resolution (2025)
    Hybrid Approach:
    1. Fuzzy Blocking (RapidFuzz): Fast candidate generation.
    2. Vector Re-ranking (SentenceTransformer): Semantic disambiguation.
    """
    
    def __init__(
        self,
        use_gpu: bool = False,
        vector_backend: Optional[VectorBackend] = None,
        # For backward compatibility with user's tests
        vector_model: Optional[SentenceTransformer] = None,
        similarity_fn=None,
    ):
        if vector_backend:
            self.vector_backend = vector_backend
        elif vector_model:
            # Wrap manual model/fn in a backend-like interface
            class ManualBackend(VectorBackend):
                def __init__(self, model, sim_fn):
                    self.model = model
                    self.sim_fn = sim_fn
                def encode(self, texts: List[str]) -> np.ndarray:
                    # Handle single string or list
                    return self.model.encode(texts)
                def similarity(self, query_vec, matrix):
                    return self.sim_fn(query_vec, matrix).ravel()
            
            self.vector_backend = ManualBackend(vector_model, similarity_fn)
        else:
            device = 'cuda' if use_gpu else 'cpu'
            self.vector_backend = SentenceTransformerBackend('all-MiniLM-L6-v2', device=device)
        
        self.vector_backend_name = self.vector_backend.__class__.__name__
        self.known_entities: List[str] = []
        self.entity_vectors: Optional[np.ndarray] = None
        self.entity_map: Dict[str, str] = {} # canonical -> ticker
        self.alias_map: Dict[str, str] = {} # alias -> canonical

    def load_entities(self, entities: List[Dict[str, str]]):
        """
        Load known entities (canonical names + tickers + aliases).
        Format: [{"name": "Foxconn", "ticker": "2317.TW", "aliases": ["Hon Hai Precision"]}, ...]
        """
        self.known_entities = []
        self.entity_map = {}
        self.alias_map = {}
        
        for e in entities:
            name = e['name']
            self.known_entities.append(name)
            self.entity_map[name] = e['ticker']
            
            # Map aliases
            if 'aliases' in e:
                for alias in e['aliases']:
                    self.alias_map[alias.lower()] = name
                    # Also add aliases to known entities for vector search if desired, 
                    # but for now we keep strict separation: 
                    # 1. Exact/Alias Lookup 2. Fuzzy/Vector against Canonical
        
        logger.info("Embedding %d entities with %s backend...", len(self.known_entities), self.vector_backend_name)
        self.vector_backend.fit(self.known_entities)
        self.entity_vectors = self.vector_backend.encode(self.known_entities)
        logger.info("Embedding complete.")

    def resolve(self, query: str, fuzzy_threshold: int = 50) -> Optional[Dict]:
        """
        Resolve a messy query string to a Ticker.
        """
        query_norm = query.lower().strip()
        logger.info(f"Resolving: '{query}'")
        
        # Step 0: Exact/Alias Match
        if query_norm in self.alias_map:
            canonical = self.alias_map[query_norm]
            logger.info(f"Alias Match: '{query}' -> {canonical}")
            return {
                "ticker": self.entity_map[canonical],
                "canonical_name": canonical,
                "confidence": 1.0,
                "method": "alias_lookup"
            }

        # Step 1: Fuzzy Blocking (Candidates)
        # Lowered threshold to catch "Taiwan Semi" -> "TSMC" (very different)
        # But wait, "TSMC" abbreviation is hard for token_set_ratio.
        candidates = process.extract(
            query, 
            self.known_entities, 
            scorer=fuzz.token_set_ratio, 
            limit=10,
            score_cutoff=fuzzy_threshold
        )
        
        # If fuzzy fails or returns weak matches, we fallback to PURE VECTOR search across ALL entities
        # This is expensive but necessary for "SpaceX" vs "Space Exploration" if fuzzy doesn't link them.
        
        candidate_names = [c[0] for c in candidates]
        candidate_indices = [c[2] for c in candidates]
        
        # Pure Vector Fallback if candidate list is small or weak
        # For this MVP, let's ALWAYS include the vector search on the full set if N < 5
        # Or, efficiently, we just use vector search for everything since N is small (5 entities).
        # PROD: Keep blocking. MVP: Search all.
        
        query_vec = self.vector_backend.encode([query])
        
        # Search ALL vectors (MVP optimization: N is small)
        all_cosine_scores = self.vector_backend.similarity(query_vec, self.entity_vectors)
        if hasattr(all_cosine_scores, "cpu"):
            all_cosine_scores = all_cosine_scores.cpu().numpy()
        else:
            all_cosine_scores = np.asarray(all_cosine_scores)
        best_idx_vec = int(np.argmax(all_cosine_scores))
        best_score_vec = float(all_cosine_scores[best_idx_vec])
        best_name_vec = self.known_entities[best_idx_vec]
        
        logger.info(f"Vector Best: {best_name_vec} ({best_score_vec:.4f})")
        
        # Scoring Logic
        if best_score_vec > 0.35: # MiniLM threshold
             return {
                "ticker": self.entity_map[best_name_vec],
                "canonical_name": best_name_vec,
                "confidence": best_score_vec,
                "method": "pure_vector"
            }
            
        return None
