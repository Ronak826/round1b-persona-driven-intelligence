from typing import List, Tuple, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os

TRAVEL_KEYWORDS = {
    "cities": 0.25, "things to do": 0.25, "activities": 0.2,
    "cuisine": 0.15, "restaurants": 0.15, "hotels": 0.15,
    "tips": 0.05, "history": 0.05, "culture": 0.05
}

class Ranker:
    def __init__(self, persona_terms: str):
        self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.q_vec = self.embedder.encode(persona_terms, normalize_embeddings=True)
        self.vectors = None
        self.meta = []

    def build(self, sections: List[Tuple[str, str, int, str]]):
        texts = [f"{title}. {body[:512]}" for title, body, _, _ in sections]
        self.vectors = self.embedder.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        self.meta = sections
        dim = self.vectors.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(self.vectors)

    def score_keyword(self, title: str) -> float:
        title_lower = title.lower()
        return sum(weight for keyword, weight in TRAVEL_KEYWORDS.items() if keyword in title_lower)

    def topk(self, k: int = 5) -> List[Dict]:
        if self.index.ntotal == 0:
            return []

        sim, idx = self.index.search(np.asarray([self.q_vec]), len(self.meta))
        sim = sim[0]
        idx = idx[0]

        scored = []
        for i, sem in zip(idx, sim):
            title, _, page, doc = self.meta[i]
            kw_score = self.score_keyword(title)
            hybrid_score = 0.7 * sem + 0.3 * kw_score
            scored.append((hybrid_score, i))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_k = scored[:k]

        results = []
        for rank, (_, i) in enumerate(top_k, 1):
            title, _, page, doc_path = self.meta[i]
            results.append({
                "document": os.path.basename(doc_path),
                "section_title": title.strip(),
                "importance_rank": rank,
                "page_number": page
            })

        return results
