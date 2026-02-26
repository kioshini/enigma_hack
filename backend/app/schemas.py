from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class EmailOut(BaseModel):
    id: UUID
    sender: str
    subject: Optional[str] = ""
    body: Optional[str] = ""
    status: str
    complexity: Optional[str] = None
    sentiment: Optional[str] = None
    ai_response: Optional[str] = None
    confidence: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MLAnalysisRequest(BaseModel):
    text: str


class MLAnalysisResponse(BaseModel):
    complexity: str
    sentiment: str
    confidence: float
    suggested_response: str


class EmailListResponse(BaseModel):
    emails: list[EmailOut]
    total: int


class StatsResponse(BaseModel):
    total: int
    new: int
    processed: int
    needs_operator: int
    escalated: int
    closed: int
