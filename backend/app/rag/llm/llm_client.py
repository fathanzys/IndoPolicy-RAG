import os
from typing import List
from groq import Groq

class LLMClient:
    def __init__(self, model: str = "llama-3.1-8b-instant"):
        # KOREKSI: Panggil nama variabelnya "GROQ_API_KEY"
        api_key = os.getenv("GROQ_API_KEY") 

        if not api_key:
            raise EnvironmentError("GROQ_API_KEY tidak ditemukan di environment. Cek file .env Anda.")

        self.client = Groq(api_key=api_key)
        self.model = model

    def answer(self, question: str, context_chunks: List[str], chat_history: List[dict] = None) -> str:
        context = "\n\n".join(context_chunks)

        prompt = f"""
Anda adalah asisten yang MENJAWAB HANYA berdasarkan konteks di bawah.
Jika jawaban tidak ada di konteks, jawab:
"Saya tidak menemukan jawabannya di dokumen."

KONTEKS:
{context}

PERTANYAAN:
{question}

JAWABAN:
""".strip()

        messages = []
        
        # Add system prompt with context
        messages.append({"role": "system", "content": prompt})
        
        # Add conversation history
        if chat_history:
            messages.extend(chat_history)
            
        # Add latest user question
        if not chat_history or chat_history[-1].get("role") != "user" or chat_history[-1].get("content") != question:
            messages.append({"role": "user", "content": question})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.0,
        )

        return response.choices[0].message.content.strip()
