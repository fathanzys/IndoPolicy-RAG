import os
from dotenv import load_dotenv

# 1. Cek di folder mana script ini dijalankan
print(f"1. Terminal berjalan di: {os.getcwd()}")

# 2. Coba load .env
load_status = load_status = load_dotenv() # Mencari di folder os.getcwd()
print(f"2. Apakah .env ditemukan di situ? {'YA' if load_status else 'TIDAK'}")

# 3. Cek apakah key terbaca
key = os.getenv("GROQ_API_KEY")
print(f"3. Nilai API KEY: {key if key else 'KOSONG (None)'}")