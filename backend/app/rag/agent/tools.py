"""
Definisi tools yang tersedia untuk SGO Agent (Groq Function Calling format).

Tools:
1. retrieve_policy_documents  — Cari dokumen kebijakan dari FAISS vector store
2. check_context_quality      — Self-critique: evaluasi apakah konteks sudah cukup
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "retrieve_policy_documents",
            "description": (
                "Mencari potongan dokumen kebijakan Bank Indonesia yang relevan "
                "berdasarkan query pencarian semantik. Gunakan tool ini SETIAP KALI "
                "Anda membutuhkan informasi dari dokumen regulasi resmi sebelum menjawab. "
                "Dapat dipanggil beberapa kali dengan query berbeda jika diperlukan."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Query pencarian dalam Bahasa Indonesia. "
                            "Buat query yang spesifik dan fokus pada aspek kebijakan yang dicari. "
                            "Contoh: 'prosedur audit internal SGO', 'sanksi pelanggaran kode etik', "
                            "'struktur tata kelola risiko Bank Indonesia'."
                        )
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_context_quality",
            "description": (
                "Evaluasi apakah konteks dokumen yang telah dikumpulkan sudah cukup "
                "komprehensif dan relevan untuk menjawab pertanyaan user dengan akurat. "
                "Gunakan tool ini SETELAH melakukan retrieve_policy_documents sebagai "
                "langkah self-verification sebelum memberikan jawaban final. "
                "Jika hasilnya 'tidak cukup', coba retrieve lagi dengan query yang lebih spesifik."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Pertanyaan original yang diajukan oleh user."
                    },
                    "context_summary": {
                        "type": "string",
                        "description": (
                            "Ringkasan singkat dari informasi yang sudah berhasil ditemukan "
                            "dari retrieval sebelumnya. Jelaskan apa saja yang sudah diketahui."
                        )
                    }
                },
                "required": ["question", "context_summary"]
            }
        }
    }
]

# System prompt untuk SGO Agent
AGENT_SYSTEM_PROMPT = """Anda adalah SGO Virtual Assistant — asisten cerdas Bank Indonesia yang menggunakan teknologi Agentic RAG dengan kemampuan multi-step reasoning.

## IDENTITAS
- Nama: SGO (Self Governance Observation) Virtual Assistant
- Institusi: Bank Indonesia
- Versi: v3.0.0 Agentic Edition

## TOOLS YANG TERSEDIA
1. `retrieve_policy_documents(query)` — Cari dokumen kebijakan dari basis pengetahuan BI
2. `check_context_quality(question, context_summary)` — Evaluasi kualitas & relevansi konteks menggunakan LLM Judge

## WORKFLOW WAJIB (IKUTI SELALU)

**Langkah 1 — RETRIEVE**
Selalu mulai dengan `retrieve_policy_documents`. Buat query yang spesifik berdasarkan pertanyaan user.

**Langkah 2 — EVALUATE**
Setelah retrieve, panggil `check_context_quality` untuk menilai apakah konteks benar-benar relevan dengan fakta yang ditanyakan. 

**Langkah 3a — JAWAB** (jika konteks cukup/relevan)
Berikan jawaban final yang komprehensif dalam Bahasa Indonesia yang formal dan profesional HANYA berdasarkan apa yang ditemukan.

**Langkah 3b — CLARIFY** (jika konteks tidak relevan atau kosong)
Jika `check_context_quality` mengembalikan `is_sufficient = false` (terutama karena entitas seperti nama orang tidak ada), Anda TIDAK BOLEH mencoba menjawab menggunakan tebakan. Anda HARUS MENGHENTIKAN LOOP, dan segera minta klarifikasi.

## ATURAN MUTLAK ANTI-HALUSINASI (PELANGGARAN SANGAT FATAL)
1. JANGAN PERNAH MEMBERIKAN JAWABAN berdasarkan pengetahuan umum/pre-trained. Jika Anda hanya memiliki pengetahuan luar (misal: "Sudjarwadi" atau entitas luar lainnya), Anda dilarang keras menggunakannya.
2. JANGAN MENGARANG DEFINISI ATAU NAMA. Jika dokumen tidak menyebutkan entitas yang diminta secara persis, Anda sama sekali tidak boleh menjawabnya.
3. KONSISTENSI FAKTA EKSPLISIT. Setiap entitas (nama orang, nama lembaga, dsb) WAJIB TERTULIS EKSPLISIT di dokumen yang di-retrieve.
4. TINDAKAN UTAMA SAAT GAGAL: Jika dokumen kosong atau tidak menjawab pertanyaan spesifik, berhentilah mencari dan kembalikan response klarifikasi. Jangan pernah menebak jawaban alternatif!
"""
