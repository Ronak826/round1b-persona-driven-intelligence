from typing import List, Tuple, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os
import re

class Ranker:
    def __init__(self, persona_terms: str):
        self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
        self.q_vec = self.embedder.encode(
            persona_terms, 
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        self.keyword_patterns = self._compile_keyword_patterns()
        self.meta = []
        self.keyword_scores = []

    def _compile_keyword_patterns(self):
        """Precompile regex patterns for faster keyword matching"""
        keywords = {
            "cities", "things to do", "activities", "cuisine", 
            "restaurants", "hotels", "tips", "history", "culture"
        }
        return {kw: re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE) for kw in keywords}

    def build(self, sections: List[Tuple[str, str, int, str]]):
        """Precompute embeddings and keyword scores for all sections"""
        titles = [title for title, _, _, _ in sections]
        texts = [f"{title}. {body[:512]}" for title, body, _, _ in sections]
        
        # Batch process embeddings
        self.vectors = self.embedder.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=False
        )
        
        # Precompute keyword scores
        self.keyword_scores = [self._precomputed_score(title) for title in titles]
        self.meta = sections
        
        # Create FAISS index
        dim = self.vectors.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(self.vectors)

    def _precomputed_score(self, title: str) -> float:
        """Calculate keyword score with precompiled patterns"""
        title_lower = title.lower()
        score = 0.0
        for kw, pattern in self.keyword_patterns.items():
            if pattern.search(title_lower):
                score += {
                    "cities": 0.25, "things to do": 0.25, "activities": 0.2,
                    "cuisine": 0.15, "restaurants": 0.15, "hotels": 0.15,
                    "tips": 0.05, "history": 0.05, "culture": 0.05
                }[kw]
        return score

    def topk(self, k: int = 5) -> List[Dict]:
        """Efficient top-k retrieval with hybrid scoring"""
        if not self.meta:
            return []
        
        # Retrieve candidate pool (3x more than needed)
        candidate_count = min(3 * k, len(self.meta))
        sim_scores, indices = self.index.search(np.asarray([self.q_vec]), candidate_count)
        sim_scores = sim_scores[0]
        indices = indices[0]
        
        # Hybrid scoring on candidate subset
        candidates = []
        for idx, sim in zip(indices, sim_scores):
            hybrid_score = 0.7 * sim + 0.3 * self.keyword_scores[idx]
            candidates.append((hybrid_score, idx))
        
        # Get top-k from candidate pool
        candidates.sort(key=lambda x: x[0], reverse=True)
        top_k = candidates[:k]
        
        # Prepare results
        results = []
        for rank, (_, idx) in enumerate(top_k, 1):
            title, _, page, doc_path = self.meta[idx]
            results.append({
                "document": os.path.basename(doc_path),
                "section_title": title.strip(),
                "importance_rank": rank,
                "page_number": page
            })
            
        return results