from datetime import date
from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator

class Role(str, Enum):
    viewer="viewer"; analyst="analyst"; administrator="administrator"

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: Role

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    conversation_id: str | None = None

class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    citations: list[str] = []
    activity: list[dict[str, Any]] = []

class SearchFilters(BaseModel):
    department: str | None = None
    document_type: str | None = None
    access_level: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    top_k: int = Field(default=6, ge=1, le=20)
    @field_validator("date_to")
    @classmethod
    def validate_range(cls, v, info):
        start=info.data.get("date_from")
        if start and v and v < start: raise ValueError("date_to must be >= date_from")
        return v

class RetrievedChunk(BaseModel):
    chunk_id: str
    document_id: str
    title: str
    content: str
    source: str
    department: str
    document_type: str
    access_level: str
    created_date: str
    dense_score: float = 0.0
    sparse_score: float = 0.0
    hybrid_score: float = 0.0

class ActivityEvent(BaseModel):
    type: str
    node: str | None = None
    status: str | None = None
    message: str | None = None
    data: dict[str, Any] = {}

class AnalysisRequest(BaseModel):
    operation: Literal["count_by_field","group_by","frequency","date_distribution","severity_summary","root_cause_summary"]
    field: str | None = None
    records: list[dict[str, Any]] = []
