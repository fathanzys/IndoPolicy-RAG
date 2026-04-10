import os
import faiss
import numpy as np
import pickle
from typing import List
from app.rag.embedding.embedder import Embedder

class FaissVectorStore:
    def __init__(self, index_path: str = "faiss_index"):
        self.index_path = index_path
        self.index_file = os.path.join(index_path, "index.faiss")
        self.metadata_file = os.path.join(index_path, "metadata.pkl")
        self.embedder = Embedder()
        self.index = None
        self.chunks = [] # Menyimpan teks asli

        # Coba load jika ada
        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            self.load()
        else:
            # Dimensi vector all-MiniLM-L6-v2 adalah 384
            self.index = faiss.IndexFlatL2(384)

    def create_index(self, chunks: List[str]):
        """Membuat index baru dari list teks"""
        if not chunks:
            return

        print("Sedang membuat embedding (ini memakan waktu)...")
        self.chunks = chunks
        
        # 1. Embed semua chunks
        vectors = self.embedder.model.encode(chunks)
        
        # 2. Masukkan ke FAISS
        # Reset index lama jika ada
        self.index = faiss.IndexFlatL2(384)
        self.index.add(np.array(vectors, dtype=np.float32))
        
        # 3. Simpan
        self.save()
        print(f"Index berhasil dibuat dengan {len(chunks)} dokumen.")

    def search(self, query: str, k: int = 4) -> List[str]:
        """Mencari k teks termirip"""
        if not self.index or self.index.ntotal == 0:
            return []

        # 1. Embed query
        query_vector = self.embedder.embed(query)
        query_np = np.array([query_vector], dtype=np.float32)

        # 2. Search di FAISS
        distances, indices = self.index.search(query_np, k)

        # 3. Ambil teks berdasarkan index
        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.chunks):
                results.append(self.chunks[idx])
        
        return results

    def save(self):
        if not os.path.exists(self.index_path):
            os.makedirs(self.index_path)
        
        faiss.write_index(self.index, self.index_file)
        with open(self.metadata_file, "wb") as f:
            pickle.dump(self.chunks, f)

    def load(self):
        self.index = faiss.read_index(self.index_file)
        with open(self.metadata_file, "rb") as f:
            self.chunks = pickle.load(f)