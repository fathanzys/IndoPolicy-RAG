from fastapi import APIRouter
from app.models.schemas import AskRequest, AskResponse
from app.rag.rag_service import RAGService

router = APIRouter()

# ⛔ JANGAN inisialisasi di level module
rag_service: RAGService | None = None


@router.post("/ask", response_model=AskResponse)
def ask_question(req: AskRequest):
    global rag_service

    # 🔥 Lazy init (AMAN untuk uvicorn --reload)
    if rag_service is None:
        rag_service = RAGService(doc_path="data/contoh.txt")

    answer = rag_service.ask(req.question, chat_history=req.chat_history)
    return AskResponse(answer=answer)
