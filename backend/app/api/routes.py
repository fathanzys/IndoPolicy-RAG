from fastapi import APIRouter
from app.models.schemas import AskRequest, AskResponse, ReasoningStep, FeedbackRequest
from app.rag.rag_service import RAGService
from app.rag.agent.agent_service import AgentService
from fastapi.responses import StreamingResponse

router = APIRouter()

# Lazy-init: aman untuk uvicorn --reload
rag_service: RAGService | None = None
agent_service: AgentService | None = None


@router.post("/ask", response_model=AskResponse)
def ask_question(req: AskRequest):
    global rag_service, agent_service

    # Inisialisasi saat pertama kali dipanggil
    if rag_service is None:
        rag_service = RAGService(doc_path="data/contoh.txt")

    if agent_service is None:
        agent_service = AgentService(vector_store=rag_service.retriever)

    # Jalankan Agentic RAG loop
    result = agent_service.run(
        question=req.question,
        chat_history=req.chat_history,
    )

    # Konversi steps ke ReasoningStep schema
    steps = [ReasoningStep(**s) for s in result.get("steps", [])]

    return AskResponse(
        answer=result["answer"],
        steps=steps,
        total_steps=result.get("total_steps", 0),
        sources=result.get("sources", []),
        follow_ups=result.get("follow_ups", [])
    )

@router.post("/feedback")
def submit_feedback(req: FeedbackRequest):
    # Untuk sementara kita log saja ke console/file
    print(f"FEEDBACK RECEIVED: [{req.rating.upper()}] untuk pertanyaan: '{req.question}'")
    
    with open("feedback.log", "a", encoding="utf-8") as f:
        f.write(f"{req.rating.upper()} | {req.question} | {req.answer[:50]} | {req.comment or ''}\n")
        
    return {"status": "success", "message": "Feedback berhasil disimpan"}

@router.get("/stats")
def get_stats():
    # Parsing feedback.log untuk statistik
    file_path = "feedback.log"
    total_chats = 0
    positive = 0
    negative = 0
    history = []

    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                total_chats = len(lines)
                for line in lines:
                    parts = line.split(" | ")
                    if len(parts) >= 1:
                        rating = parts[0].strip()
                        if rating == "UP":
                            positive += 1
                        elif rating == "DOWN":
                            negative += 1
                        
                        # Ambil 10 terakhir untuk history
                        if len(history) < 10:
                            history.append({
                                "rating": rating,
                                "question": parts[1] if len(parts) > 1 else "",
                                "comment": parts[3].strip() if len(parts) > 3 else ""
                            })
        except Exception as e:
            print(f"Error reading stats: {e}")

    return {
        "total_chats": total_chats,
        "positive_feedback": positive,
        "negative_feedback": negative,
        "satisfaction_rate": round((positive / total_chats * 100), 1) if total_chats > 0 else 0,
        "recent_feedback": history[::-1]
    }

@router.post("/ask/stream")
def ask_question_stream(req: AskRequest):
    global rag_service, agent_service

    if rag_service is None:
        rag_service = RAGService(doc_path="data/contoh.txt")

    if agent_service is None:
        agent_service = AgentService(vector_store=rag_service.retriever)

    return StreamingResponse(
        agent_service.run_stream(
            question=req.question,
            chat_history=req.chat_history,
        ),
        media_type="text/event-stream"
    )
