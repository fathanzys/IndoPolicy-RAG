import os
from app.rag.loader.text_loader import TextLoader
from app.rag.chunking.basic_chunker import BasicChunker
from app.rag.embedding.embedder import Embedder
from app.rag.vectorstore.faiss_store import FaissVectorStore
from app.rag.llm.llm_client import LLMClient


from app.rag.retrieval.hybrid_retriever import HybridRetriever

class RAGService:
    """
    Setup service: bertanggung jawab untuk load, chunk, embed, dan build FAISS index.
    Meng-expose retriever untuk digunakan oleh AgentService.
    """

    def __init__(self, doc_path: str):
        self.doc_path = doc_path

        # 1. Load Document
        loader = TextLoader()
        text = loader.load(doc_path)
        print(f"Total karakter dokumen: {len(text)}")

        # 2. Chunking
        chunker = BasicChunker(chunk_size=1000, chunk_overlap=200)
        chunks = chunker.chunk(text)
        print(f"Total chunks dibuat: {len(chunks)}")

        if not chunks:
            print("WARNING: Dokumen kosong atau gagal di-chunk!")

        # 3. Embedding & Vector Store
        index_folder = "faiss_index"
        if not os.path.exists(index_folder):
            os.makedirs(index_folder)

        self.vector_store = FaissVectorStore(index_path=index_folder)
        self.vector_store.create_index(chunks)
        
        # 4. Hybrid Retriever
        self.retriever = HybridRetriever(self.vector_store)

    def search(self, query: str, k: int = 5):
        """Publik method — digunakan oleh AgentService untuk retrieval."""
        return self.retriever.search(query, k=k)