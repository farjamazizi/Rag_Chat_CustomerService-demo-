from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .models import ChatRequest, ChatResponse, ConfigResponse
from .rag import ask_question, get_vector_store


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/config", response_model=ConfigResponse)
def config() -> ConfigResponse:
    return ConfigResponse(
        app_name=settings.app_name,
        environment=settings.app_env,
        model=settings.ollama_model,
        embedding_model=settings.embedding_model,
        top_k=settings.top_k,
    )


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        return ask_question(request)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat request failed: {exc}") from exc


@app.post("/api/index/rebuild")
def rebuild_index() -> dict[str, str]:
    try:
        get_vector_store.cache_clear()
        get_vector_store()
        return {"status": "rebuilt"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Index rebuild failed: {exc}") from exc
