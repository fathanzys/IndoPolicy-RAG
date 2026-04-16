"""
AgentService — Inti dari Agentic RAG IndoPolicy.

Mengimplementasikan pola ReAct (Reasoning + Acting) menggunakan:
- Groq API (LLaMA 3.1-8B) dengan native Function Calling
- 2 Tools: retrieve_policy_documents + check_context_quality
- Multi-step reasoning loop (max 5 steps)
"""

import json
import os
from typing import List, Optional
from groq import Groq

from app.rag.agent.tools import TOOLS, AGENT_SYSTEM_PROMPT


class AgentService:
    def __init__(self, vector_store, max_steps: int = 5):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY tidak ditemukan di environment.")

        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"
        self.vector_store = vector_store
        self.max_steps = max_steps

    # ──────────────────────────────────────────────
    # TOOL EXECUTION
    # ──────────────────────────────────────────────

    def _exec_retrieve(self, query: str, accumulated_context: list) -> tuple[str, dict]:
        chunks = self.vector_store.search(query, k=5)

        for chunk in chunks:
            if chunk not in accumulated_context:
                accumulated_context.append(chunk)

        if chunks:
            result = (
                f"✅ Ditemukan {len(chunks)} potongan dokumen untuk query: '{query}'\n\n"
                + "\n\n---\n\n".join(chunks)
            )
        else:
            result = f"❌ Tidak ditemukan dokumen relevan untuk query: '{query}'"

        step = {
            "type": "action",
            "tool": "retrieve_policy_documents",
            "query": query,
            "chunks_found": len(chunks),
        }
        return result, step

    def _exec_check_quality(
        self, question: str, context_summary: str, accumulated_context: list
    ) -> tuple[str, dict, bool, bool]:
        """
        Returns: (result_str, step_info, is_sufficient, needs_clarification)
        is_sufficient digunakan di agent loop untuk memutuskan apakah harus stop.
        Gunakan LLM sebagai Juri untuk validasi konteks terhadap halusinasi.
        """
        total_chunks = len(accumulated_context)

        if total_chunks == 0:
            is_sufficient = False
            needs_clarification = True
            reason = "Belum ada dokumen yang relevan ditemukan."
            suggestion = "Segera minta klarifikasi kepada pengguna jika dokumen benar-benar kosong."
        else:
            # Panggil LLM Judge
            judge_prompt = f"""Anda adalah evaluator ketat untuk menghindari halusinasi AI.
Tugas Anda: Evaluasi apakah dokumen berikut cukup dan RELEVAN secara spesifik untuk menjawab pertanyaan pengguna. Perhatikan khusus jika pengguna menanyakan nama entitas (misal: entitas orang) yang tidak disebutkan di dokumen.
JANGAN MENGARANG JAWABAN.
            
Pertanyaan: {question}
Konteks:
{chr(10).join(accumulated_context)}

Berikan output murni format JSON:
{{
    "is_sufficient": true/false,
    "needs_clarification": true/false, // Set true jika entitas yang ditanya pengguna benar-benar tidak ada di dokumen dan berpotensi memicu halusinasi, sehingga agen harus segera stop dan meminta klarifikasi.
    "reason": "alasan singkat mengapa divalidasi cukup atau perlunya klarifikasi",
    "suggestion": "saran query baru jika false"
}}
"""
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": judge_prompt}],
                    temperature=0.0,
                    response_format={"type": "json_object"}
                )
                judge_result = json.loads(response.choices[0].message.content)
                is_sufficient = judge_result.get("is_sufficient", False)
                needs_clarification = judge_result.get("needs_clarification", False)
                reason = judge_result.get("reason", "Tidak dapat divalidasi")
                suggestion = judge_result.get("suggestion", "Coba kata kunci spesifik")
            except Exception as e:
                is_sufficient = False
                needs_clarification = False
                reason = f"Gagal mengevaluasi dengan LLM: {str(e)}"
                suggestion = "Ulangi proses retrieval"

        quality_result = {
            "is_sufficient": is_sufficient,
            "needs_clarification": needs_clarification,
            "total_chunks_collected": total_chunks,
            "reason": reason,
            "suggested_action": suggestion,
        }
        result_str = json.dumps(quality_result, ensure_ascii=False)

        step = {
            "type": "action",
            "tool": "check_context_quality",
            "question": question,
            "context_summary": context_summary,
            "is_sufficient": is_sufficient,
            "needs_clarification": needs_clarification,
            "total_chunks": total_chunks,
        }
        return result_str, step, is_sufficient, needs_clarification

    # ──────────────────────────────────────────────
    # FORCE FINAL ANSWER
    # ──────────────────────────────────────────────

    def _force_final_answer(self, messages: list, question: str) -> str:
        """
        Setelah konteks cukup, paksa LLM menghasilkan jawaban teks
        tanpa memanggil tool lagi (tool_choice='none').
        """
        # Inject instruksi eksplisit agar LLM menulis jawaban sekarang
        messages_for_answer = messages + [
            {
                "role": "user",
                "content": (
                    "Konteks sudah CUKUP dan telah diverifikasi. "
                    "Sekarang tulis jawaban FINAL yang komprehensif, terstruktur, "
                    "dan informatif dalam Bahasa Indonesia berdasarkan semua dokumen "
                    "yang sudah ditemukan. Jawablah pertanyaan: " + question
                ),
            }
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages_for_answer,
            tool_choice="none",   # ← Paksa teks saja, tanpa tool call
            temperature=0.0,
        )
        return response.choices[0].message.content or "Maaf, tidak dapat menghasilkan jawaban."

    def _force_final_answer_stream(self, messages: list, question: str):
        messages_for_answer = messages + [
            {
                "role": "user",
                "content": (
                    "Konteks sudah CUKUP dan telah diverifikasi. "
                    "Sekarang tulis jawaban FINAL yang komprehensif, terstruktur, "
                    "dan informatif dalam Bahasa Indonesia berdasarkan semua dokumen "
                    "yang sudah ditemukan. Jawablah pertanyaan: " + question
                ),
            }
        ]

        response_stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages_for_answer,
            tool_choice="none",
            temperature=0.0,
            stream=True
        )
        for chunk in response_stream:
            token = chunk.choices[0].delta.content
            if token is not None:
                yield json.dumps({"type": "token", "content": token}) + "\n"

    def _generate_follow_ups(self, answer: str, context: list) -> List[str]:
        """Menghasilkan 3 pertanyaan lanjutan berdasarkan jawaban dan konteks."""
        prompt = f"""Berdasarkan jawaban dan konteks dokumen berikut, buatkan 3 pertanyaan lanjutan yang singkat, padat, dan relevan untuk membantu pengguna memahami kebijakan lebih dalam.
        
Jawaban: {answer}
---
Konteks populer:
{chr(10).join(context[:3])}

Output harus dalam format JSON list of strings: ["pertanyaan 1?", "pertanyaan 2?", "pertanyaan 3?"]
JANGAN ada teks selain JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            # Kadang model bungkus dalam key "questions" atau sejenisnya
            if isinstance(data, list):
                return data[:3]
            if isinstance(data, dict):
                for val in data.values():
                    if isinstance(val, list):
                        return val[:3]
            return []
        except Exception:
            return []

    # ──────────────────────────────────────────────
    # MAIN AGENT LOOP
    # ──────────────────────────────────────────────

    def run(self, question: str, chat_history: Optional[List[dict]] = None) -> dict:
        accumulated_context: list = []
        steps: list = []

        messages = [{"role": "system", "content": AGENT_SYSTEM_PROMPT}]

        if chat_history:
            # Batasi history maksimal 4 pesan terakhir untuk menghemat token Groq (Limit 6000 TPM)
            for msg in chat_history[-4:]:
                if isinstance(msg, dict) and msg.get("role") in ("user", "assistant"):
                    messages.append({"role": msg["role"], "content": msg.get("content", "")})

        messages.append({"role": "user", "content": question})

        for _ in range(self.max_steps):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.0,
            )

            msg = response.choices[0].message

            # Tangkap thought kalau ada teks sebelum tool call
            if msg.content and msg.tool_calls:
                steps.append({"type": "thought", "content": msg.content})

            # ── Tidak ada tool call = final answer ──
            if not msg.tool_calls:
                final_answer = msg.content or "Maaf, agen tidak dapat menghasilkan jawaban."
                action_count = sum(1 for s in steps if s["type"] == "action")
                follow_ups = self._generate_follow_ups(final_answer, accumulated_context)
                return {
                    "answer": final_answer, 
                    "steps": steps, 
                    "total_steps": action_count,
                    "sources": accumulated_context,
                    "follow_ups": follow_ups
                }

            # ── Tambah assistant msg ke history ──
            messages.append({
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in msg.tool_calls
                ],
            })

            # ── Eksekusi setiap tool call ──
            should_finalize = False
            should_clarify = False

            for tool_call in msg.tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    tool_args = {}

                if tool_name == "retrieve_policy_documents":
                    tool_result, step_info = self._exec_retrieve(
                        tool_args.get("query", ""), accumulated_context
                    )
                    steps.append(step_info)

                elif tool_name == "check_context_quality":
                    tool_result, step_info, is_sufficient, needs_clarification = self._exec_check_quality(
                        tool_args.get("question", question),
                        tool_args.get("context_summary", ""),
                        accumulated_context,
                    )
                    steps.append(step_info)

                    # ← KUNCI: Kalau sudah cukup, tandai untuk finalisasi
                    if is_sufficient:
                        should_finalize = True
                    elif needs_clarification:
                        should_clarify = True
                else:
                    tool_result = "Tool tidak dikenal."
                    steps.append({"type": "action", "tool": tool_name})

                # Tambah tool result ke messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result,
                })

            # ── Kalau quality check bilang sufficient → paksa final answer sekarang ──
            if should_finalize:
                final_answer = self._force_final_answer(messages, question)
                action_count = sum(1 for s in steps if s["type"] == "action")
                follow_ups = self._generate_follow_ups(final_answer, accumulated_context)
                return {
                    "answer": final_answer, 
                    "steps": steps, 
                    "total_steps": action_count,
                    "sources": accumulated_context,
                    "follow_ups": follow_ups
                }
                
            # ── Kalau quality check bilang butuh klarifikasi → stop awal ──
            if should_clarify:
                action_count = sum(1 for s in steps if s["type"] == "action")
                clarification_text = "Saya tidak dapat menemukan referensi tentang hal tersebut dalam regulasi saat ini. Apakah ada spesifik dokumen atau tahun yang ingin difokuskan?"
                steps.append({"type": "clarification", "content": clarification_text})
                return {
                    "answer": clarification_text, 
                    "steps": steps, 
                    "total_steps": action_count,
                    "sources": accumulated_context,
                    "follow_ups": []
                }

        # Fallback - Clarification
        action_count = sum(1 for s in steps if s["type"] == "action")
        clarification_text = "Saya tidak dapat menemukan referensi spesifik mengenai hal tersebut di dalam kebijakan. Apakah ada detail atau kata kunci lain yang ingin Anda cari?"
        
        # Tambahkan step clarification
        steps.append({"type": "clarification", "content": clarification_text})
        
        return {
            "answer": clarification_text,
            "steps": steps,
            "total_steps": action_count,
            "sources": accumulated_context,
            "follow_ups": []
        }

    def run_stream(self, question: str, chat_history: Optional[List[dict]] = None):
        """
        Versi Streaming dari agent loop.
        Meng-yield event metadata (thought, action, chunks) atau partial answer token.
        """
        accumulated_context: list = []
        steps: list = []
        messages = [{"role": "system", "content": AGENT_SYSTEM_PROMPT}]

        if chat_history:
            # Batasi history maksimal 4 pesan terakhir
            for msg in chat_history[-4:]:
                if isinstance(msg, dict) and msg.get("role") in ("user", "assistant"):
                    messages.append({"role": msg["role"], "content": msg.get("content", "")})

        messages.append({"role": "user", "content": question})

        for _ in range(self.max_steps):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.0,
            )
            msg = response.choices[0].message

            if msg.content and msg.tool_calls:
                step_thought = {"type": "thought", "content": msg.content}
                yield json.dumps(step_thought) + "\n"
                steps.append(step_thought)

            if not msg.tool_calls:
                yield json.dumps({"type": "token", "content": msg.content or "Maaf, agen tidak dapat menghasilkan jawaban."}) + "\n"
                return

            messages.append({
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in msg.tool_calls
                ],
            })

            should_finalize = False
            should_clarify = False
            for tool_call in msg.tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    tool_args = {}

                if tool_name == "retrieve_policy_documents":
                    tool_result, step_info = self._exec_retrieve(
                        tool_args.get("query", ""), accumulated_context
                    )
                    yield json.dumps(step_info) + "\n"
                    steps.append(step_info)

                elif tool_name == "check_context_quality":
                    tool_result, step_info, is_sufficient, needs_clarification = self._exec_check_quality(
                        tool_args.get("question", question),
                        tool_args.get("context_summary", ""),
                        accumulated_context,
                    )
                    yield json.dumps(step_info) + "\n"
                    steps.append(step_info)

                    if is_sufficient:
                        should_finalize = True
                    elif needs_clarification:
                        should_clarify = True
                else:
                    tool_result = "Tool tidak dikenal."
                    step_info = {"type": "action", "tool": tool_name}
                    yield json.dumps(step_info) + "\n"
                    steps.append(step_info)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result,
                })

            if should_finalize:
                yield from self._force_final_answer_stream(messages, question)
                return
            
            if should_clarify:
                clarification_text = "Saya tidak dapat menemukan referensi tentang hal tersebut dalam regulasi saat ini. Apakah ada spesifik dokumen atau tahun yang ingin difokuskan?"
                yield json.dumps({"type": "clarification", "content": clarification_text}) + "\n"
                yield json.dumps({"type": "token", "content": clarification_text}) + "\n"
                return

        # Clarification step if max steps reached without sufficient context
        clarification_text = "Mohon maaf, saya belum menemukan jawaban di dalam dokumen dalam batas waktu. Apakah ada detail spesifik yang bisa ditambahkan?"
        yield json.dumps({"type": "clarification", "content": clarification_text}) + "\n"
        yield json.dumps({"type": "token", "content": clarification_text}) + "\n"
