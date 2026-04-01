from __future__ import annotations

from pydantic import BaseModel, Field


class ChatTurn(BaseModel):
    question: str = Field(..., min_length=1, description="Previous user question")
    answer: str = Field(..., min_length=1, description="Assistant answer for the turn")


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Current user question")
    history: list[ChatTurn] = Field(default_factory=list, description="Prior chat turns")


class SourceItem(BaseModel):
    source: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceItem]


class ConfigResponse(BaseModel):
    app_name: str
    environment: str
    model: str
    embedding_model: str
    top_k: int
