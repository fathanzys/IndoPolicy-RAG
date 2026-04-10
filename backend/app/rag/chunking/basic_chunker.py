from typing import List

class BasicChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str) -> List[str]:
        """
        Memotong teks berdasarkan paragraf ganda (\n\n) agar konteks terjaga.
        Jika paragraf terlalu panjang, baru dipotong paksa.
        """
        if not text:
            return []

        # 1. Pisahkan berdasarkan blok paragraf (double newline)
        # Ini penting agar header "=== JUDUL ===" tidak terpisah dari isinya
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Jika menambahkan paragraf ini masih muat di chunk_size
            if len(current_chunk) + len(para) < self.chunk_size:
                current_chunk += "\n\n" + para
            else:
                # Jika chunk sudah penuh, simpan dan mulai chunk baru
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Jika paragraf itu sendiri sangat panjang (lebih dari chunk_size)
                if len(para) > self.chunk_size:
                    # Potong paksa paragraf raksasa
                    for i in range(0, len(para), self.chunk_size - self.chunk_overlap):
                        chunks.append(para[i : i + self.chunk_size])
                    current_chunk = "" # Reset
                else:
                    # Mulai chunk baru dengan overlap dari akhir chunk sebelumnya (opsional)
                    # Di sini kita simple start baru
                    current_chunk = para

        # Sisa chunk terakhir
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks