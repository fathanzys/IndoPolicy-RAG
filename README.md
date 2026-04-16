# IndoPolicy-RAG 🤖🏛️

IndoPolicy-RAG adalah asisten cerdas berbasis AI yang dirancang untuk membantu pegawai Bank Indonesia dalam memahami dan mencari informasi terkait kebijakan internal, regulasi, dan prosedur tata kelola (SGO - Self Governance Observation). 

Sistem ini menggunakan pendekatan **Agentic RAG** (Retrieval-Augmented Generation) dengan pola reasoning **ReAct** (Reasoning + Acting) untuk memastikan jawaban yang akurat, transparan, dan bebas halusinasi.

## 🚀 Fitur Utama

- **Agentic Reasoning (ReAct):** Agen melakukan proses berpikir multi-step sebelum menjawab. Anda dapat melihat proses berpikir ini di UI.
- **Anti-Hallucination Guardrails:** Menggunakan LLM Judge untuk memvalidasi relevansi dokumen sebelum memberikan jawaban.
- **Hybrid Retrieval:** Menggabungkan pencarian semantik (FAISS) dan kata kunci (BM25) untuk akurasi maksimal.
- **Sumber Referensi Transparan:** Menampilkan potongan dokumen asli yang digunakan sebagai dasar jawaban.
- **Saran Pertanyaan Lanjutan:** Memberikan rekomendasi pertanyaan terkait secara otomatis berdasarkan konteks.
- **Feedback Mechanism:** Fitur Thumbs Up/Down untuk meningkatkan kualitas jawaban di masa depan.
- **Premium Dark UI:** Antarmuka modern dengan glassmorphism dan micro-animations.

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI, Groq SDK, Sentence Transformers, FAISS, Rank-BM25.
- **Frontend:** Next.js (TypeScript), React, CSS Modules, Lucide React icons.

## 📋 Prasyarat

- Node.js & npm
- Python 3.10+
- Groq API Key (Dapatkan di [Groq Console](https://console.groq.com/))

## ⚙️ Instalasi

### 1. Persiapan Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # atau .venv\Scripts\activate di Windows
pip install -r requirements.txt
```
Buat file `.env` di dalam folder `backend/`:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 2. Persiapan Frontend
```bash
cd frontend
npm install
```
Buat file `.env.local` di dalam folder `frontend/`:
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api
```

## 🏃 Menjalankan Aplikasi

1. **Jalankan Backend:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```
2. **Jalankan Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```
Akses aplikasi di `http://localhost:3000`.

## 📂 Struktur Data
Sistem akan memuat dokumen kebijakan dari folder `backend/data/`. Saat ini sistem dikonfigurasi untuk membaca `data/contoh.txt`. Anda dapat menambahkan file kebijakan baru di folder tersebut untuk memperluas basis pengetahuan agen.

---
**Disclaimer:** Informasi yang dihasilkan oleh AI bersifat asistif. Harap verifikasi kembali dengan dokumen regulasi resmi Bank Indonesia.
