from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter

class BasicChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

    def chunk(self, text: str) -> List[str]:
        """
        Memotong teks menggunakan Langchain RecursiveCharacterTextSplitter.
        """
        if not text:
            return []

        return self.splitter.split_text(text)