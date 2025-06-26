from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response_message: str
    session_id: str
    service_now_ticket: Optional[str] = None
