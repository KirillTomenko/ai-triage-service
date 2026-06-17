from typing import Literal
from pydantic import BaseModel, Field


class TriageRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)
    channel: Literal["email", "form", "chat"] = "form"
    client_id: str = Field(..., min_length=1, max_length=100)


class TriageResponse(BaseModel):
    category: Literal["billing", "support", "complaint", "other"]
    draft_reply: str
    confidence: Literal["high", "medium", "low"]
    escalate: bool
    ticket_id: int
