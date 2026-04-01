from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / "backend" / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Customer Support RAG API")
    app_env: str = os.getenv("APP_ENV", "development")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "gemma3:1b")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "thenlper/gte-small")
    top_k: int = int(os.getenv("TOP_K", "8"))
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "300"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "30"))
    allow_origins: list[str] = field(
        default_factory=lambda: _split_csv(os.getenv("ALLOW_ORIGINS", "http://localhost:5173"))
    )
    data_dir: Path = PROJECT_ROOT / os.getenv("DATA_DIR", "data")
    index_dir: Path = PROJECT_ROOT / os.getenv("INDEX_DIR", "faiss_index")


settings = Settings()
