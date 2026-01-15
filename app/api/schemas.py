from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    text: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    history: List[ChatTurn] = Field(default_factory=list)

class Citation(BaseModel):
    source: str 
    locator: str | None = None
    doc_type: str | None = None
    page: int | None = None
    chunk_id: str | None = None
    snippet: str | None = None

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation] = Field(default_factory=list)
