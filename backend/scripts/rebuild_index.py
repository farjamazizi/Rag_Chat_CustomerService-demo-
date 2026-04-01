from __future__ import annotations

from backend.app.config import settings
from backend.app.rag import build_vector_store


def main() -> None:
    vectordb = build_vector_store()
    print(f"Rebuilt index at {settings.index_dir} with {vectordb.index.ntotal} vectors.")


if __name__ == "__main__":
    main()
