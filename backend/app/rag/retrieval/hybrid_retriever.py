from rank_bm25 import BM25Okapi
import numpy as np
from app.rag.vectorstore.faiss_store import FaissVectorStore
from typing import List

class HybridRetriever:
    """Retriever yang menggabungkan Semantic Search (FAISS) dan Keyword Search (BM25) dengan RRF."""
    def __init__(self, faiss_store: FaissVectorStore):
        self.faiss_store = faiss_store
        self.bm25 = None
        self.chunks = []
        if self.faiss_store.chunks:
            self.build_bm25(self.faiss_store.chunks)
            
    def build_bm25(self, chunks: List[str]):
        self.chunks = chunks
        tokenized_corpus = [chunk.lower().split() for chunk in chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def search(self, query: str, k: int = 5) -> List[str]:
        if not self.chunks:
            return []
            
        # 1. FAISS Search
        faiss_results = []
        if self.faiss_store.index and self.faiss_store.index.ntotal > 0:
            query_vector = self.faiss_store.embedder.embed(query)
            # Find more candidates for RRF
            distances, indices = self.faiss_store.index.search(np.array([query_vector], dtype=np.float32), max(k*2, 10))
            for rank, idx in enumerate(indices[0]):
                if idx != -1 and idx < len(self.chunks):
                    faiss_results.append((idx, rank))
                    
        # 2. BM25 Search
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        bm25_top_indices = np.argsort(bm25_scores)[::-1][:max(k*2, 10)]
        bm25_results = [(idx, rank) for rank, idx in enumerate(bm25_top_indices)]
        
        # 3. Reciprocal Rank Fusion (RRF)
        rrf_scores = {}
        # semantic weight and bm25 weight can be balanced, standard RRF uses 1 / (60 + rank)
        for idx, rank in faiss_results:
            rrf_scores[idx] = rrf_scores.get(idx, 0) + 1.0 / (60 + rank)
            
        for idx, rank in bm25_results:
            rrf_scores[idx] = rrf_scores.get(idx, 0) + 1.0 / (60 + rank)
            
        # Sort and return top k
        sorted_indices = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)[:k]
        return [self.chunks[i] for i in sorted_indices]
