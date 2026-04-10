from pydantic import BaseModel
from typing import List, Dict, Optional


class AskRequest(BaseModel):
    question: str
    chat_history: Optional[List[Dict[str, str]]] = None


class AskResponse(BaseModel):
    answer: str
