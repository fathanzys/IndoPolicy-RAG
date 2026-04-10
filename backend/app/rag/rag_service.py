import os
from app.rag.loader.text_loader import TextLoader
from app.rag.chunking.basic_chunker import BasicChunker
from app.rag.embedding.embedder import Embedder
from app.rag.vectorstore.faiss_store import FaissVectorStore
from app.rag.llm.llm_client import LLMClient

class RAGService:
    def __init__(self, doc_path: str):
        self.doc_path = doc_path
        
        # 1. Load Document
        loader = TextLoader()
        text = loader.load(doc_path)
        print(f"Total karakter dokumen: {len(text)}") # DEBUG 1
        
        # 2. Chunking
        chunker = BasicChunker(chunk_size=1000, chunk_overlap=200)
        chunks = chunker.chunk(text)
        print(f"Total chunks dibuat: {len(chunks)}") # DEBUG 2
        
        if not chunks:
            print("WARNING: Dokumen kosong atau gagal di-chunk!")
            
        # 3. Embedding & Vector Store
        index_folder = "faiss_index"
        if not os.path.exists(index_folder):
            os.makedirs(index_folder)
            
        self.vector_store = FaissVectorStore(index_path=index_folder)
        self.vector_store.create_index(chunks)
            
        # 4. LLM
        self.llm = LLMClient()

    def ask(self, question: str, chat_history: list = None) -> str:
        # 1. Cari potongan dokumen yang relevan
        related_chunks = self.vector_store.search(question, k=5)

        # --- DEBUGGING START (Lihat apa yang AI baca) ---
        print("\n" + "="*30)
        print(f"[RAG] Pertanyaan: {question}")
        print(f"[RAG] Menemukan {len(related_chunks)} potongan.")
        print("-" * 10)
        for i, chunk in enumerate(related_chunks):
            # Print 100 karakter pertama dari setiap chunk untuk dicek
            clean_chunk = chunk.replace('\n', ' ')
            print(f"Chunk #{i+1}: {clean_chunk[:150]}...")
        print("="*30 + "\n")
        # --- DEBUGGING END ---
        
        if not related_chunks:
            return "Maaf, sistem tidak menemukan referensi terkait di dokumen."

        # 2. Kirim ke LLM
        return self.llm.answer(question, related_chunks, chat_history=chat_history)