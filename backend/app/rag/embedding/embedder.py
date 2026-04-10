from typing import List
from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Download model otomatis jika belum ada (sekitar 80MB)
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> List[float]:
        if not text:
            return []
        # Ubah teks jadi vektor, lalu convert ke list python biasa
        embeddings = self.model.encode(text)
        return embeddings.tolist()