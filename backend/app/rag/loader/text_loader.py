import os

class TextLoader:
    """
    Loader sederhana untuk membaca file .txt
    """
    def load(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            print(f"ERROR: File tidak ditemukan di {file_path}")
            return ""
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"ERROR: Gagal membaca file {file_path}. Error: {e}")
            return ""