# Customer Support RAG App

This project turns the original notebook prototype into a small full-stack application:

- `backend/`: FastAPI service for retrieval, chat, and index management
- `frontend/`: React + Vite client for the chat experience
- `data/`: Source PDF documents
- `faiss_index/`: Persisted vector index used by the backend
- `rag_chat_bot.ipynb`: Original exploration notebook kept for reference

## Demo video

https://github.com/user-attachments/assets/1d4e9df7-d504-45cd-b22c-1d3ea992776f

## Architecture

The backend:

- loads the FAISS index from local disk
- embeds questions with `thenlper/gte-small`
- queries the vector store for relevant chunks
- sends the retrieved context to Ollama with `gemma3:1b`
- returns an answer plus the source document paths

The frontend:

- provides a React chat UI
- sends questions and conversation history to the backend
- renders the answer and cited sources

## Backend setup

Create or activate a Python environment, then install:

```bash
pip install -r backend/requirements.txt
```

Optional environment variables:

```bash
cp backend/.env.example backend/.env
```

Rebuild the FAISS index from the PDFs:

```bash
python -m backend.scripts.rebuild_index
```

Run the API:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend setup

Install packages:

```bash
cd frontend
npm install
```

Optional environment variables:

```bash
cp .env.example .env
```

Run the React app:

```bash
npm run dev
```

The frontend expects the backend at `http://localhost:8000` by default.

## Make targets

Common commands are available through `Makefile`:

```bash
make install
make dev-backend
make dev-frontend
make rebuild-index
make check
```

## CI

GitHub Actions now runs a CI workflow at `.github/workflows/ci.yml` that:

- installs backend dependencies with the CPU-only PyTorch wheel
- compiles and imports the FastAPI backend
- installs frontend dependencies with `npm ci`
- builds the React frontend

## API endpoints

- `GET /health`
- `GET /api/config`
- `POST /api/chat`

Example chat request:

```json
{
  "question": "What is your refund policy?",
  "history": [
    {
      "question": "How long will shipping take?",
      "answer": "Standard delivery usually takes ..."
    }
  ]
}
```

## Notes

- The backend requires Ollama to be running locally.
- Pull the model before chatting:

```bash
ollama pull gemma3:1b
```

- If `faiss_index/` is missing or stale, rebuild it with the backend script.
