from pydantic import BaseModel
from typing import Any, Dict, List, Literal, Optional


class AskRequest(BaseModel):
    question: str
    chat_history: Optional[List[Dict[str, str]]] = None


class FeedbackRequest(BaseModel):
    """Request body untuk feedback thumbs up/down."""
    question: str
    answer: str
    rating: Literal["up", "down"]
    comment: Optional[str] = None


class ReasoningStep(BaseModel):
    """
    Satu langkah dalam proses berpikir agent (ReAct trace).

    type bisa:
      - "thought"     : Agent sedang berpikir / merencanakan
      - "action"      : Agent memanggil sebuah tool
      - "observation" : Hasil dari eksekusi tool
    """
    type: Literal["thought", "action", "observation", "clarification"]
    # Field dinamis tergantung jenis step (tool name, query, chunks_found, dll)
    content: Optional[str] = None
    tool: Optional[str] = None
    query: Optional[str] = None
    chunks_found: Optional[int] = None
    preview: Optional[str] = None
    is_sufficient: Optional[bool] = None
    total_chunks: Optional[int] = None
    clarification_text: Optional[str] = None
    question: Optional[str] = None
    context_summary: Optional[str] = None


class AskResponse(BaseModel):
    answer: str
    steps: Optional[List[ReasoningStep]] = None
    total_steps: Optional[int] = None
    sources: Optional[List[str]] = None          # Poin 2: Chunk sumber yang digunakan
    follow_ups: Optional[List[str]] = None        # Poin 6: Pertanyaan lanjutan yang disarankan
