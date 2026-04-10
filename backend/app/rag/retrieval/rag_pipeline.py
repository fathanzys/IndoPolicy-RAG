from typing import List
import numpy as np

from app.rag.embedding.embedder import TextEmbedder
from app.rag.vectorstore.faiss_store import FAISSVectorStore
from app.rag.llm.llm_client import LLMClient


class RAGPipeline:
    """
    Menggabungkan retrieval + LLM untuk QA berbasis dokumen.
    """

    def __init__(
        self,
        embedder: TextEmbedder,
        vector_store: FAISSVectorStore,
        llm: LLMClient,
        top_k: int = 3,
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.llm = llm
        self.top_k = top_k

    def answer(self, question: str) -> str:
        # 1) Embed query
        q_emb = self.embedder.embed([question])
        q_emb = np.array(q_emb)

        # 2) Retrieve top-k chunks
        contexts: List[str] = self.vector_store.search(q_emb, top_k=self.top_k)

        # 3) Generate answer via LLM
        return self.llm.answer(question, contexts)
