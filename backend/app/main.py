import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router

# --- 1. KONFIGURASI ENVIRONMENT (JANGAN DIUBAH) ---
# Kita cari path absolut ke file .env secara eksplisit
env_path = Path(__file__).resolve().parent.parent / '.env'

print(f"Mencoba memuat .env dari: {env_path}") 
load_status = load_dotenv(dotenv_path=env_path)
print(f"Status memuat .env: {load_status}") 

# Validasi API Key saat startup
if not os.getenv("GROQ_API_KEY"):
    print("FATAL: GROQ_API_KEY masih belum terbaca! Cek file .env Anda.")
else:
    print("SUKSES: GROQ_API_KEY berhasil dibaca.")

# --- 2. INISIALISASI APP ---
app = FastAPI(
    title="IndoPolicy RAG API",
    version="1.0.0",
    description="API untuk Tanya Jawab Kebijakan Internal Bank Indonesia"
)

# --- 3. KONFIGURASI CORS (INI SOLUSINYA) ---
# Mengizinkan Frontend (port 3000) untuk bicara dengan Backend (port 8000)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # Izinkan asal request dari list di atas
    allow_credentials=True,
    allow_methods=["*"],        # Izinkan semua method (GET, POST, OPTIONS, dll)
    allow_headers=["*"],        # Izinkan semua header
)

# --- 4. ROUTING ---
app.include_router(api_router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "IndoPolicy Backend is running correctly"}