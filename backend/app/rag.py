from __future__ import annotations

import glob
from functools import lru_cache
from pathlib import Path

from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.llms import Ollama
from langchain_community.vectorstores import FAISS

from .config import settings
from .models import ChatRequest, ChatResponse, SourceItem
from .prompts import SYSTEM_TEMPLATE


def _index_files_exist(index_dir: Path) -> bool:
    return (index_dir / "index.faiss").exists() and (index_dir / "index.pkl").exists()


def load_documents() -> list:
    pdf_pattern = str(settings.data_dir / "Everstorm_*.pdf")
    pdf_paths = sorted(glob.glob(pdf_pattern))
    raw_docs = []
    for path in pdf_paths:
        raw_docs.extend(PyPDFLoader(path).load())
    return raw_docs


def build_vector_store() -> FAISS:
    raw_docs = load_documents()
    if not raw_docs:
        raise FileNotFoundError(f"No PDF documents found in {settings.data_dir}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    chunks = splitter.split_documents(raw_docs)
    embeddings = SentenceTransformerEmbeddings(model_name=settings.embedding_model)
    vectordb = FAISS.from_documents(chunks, embeddings)
    settings.index_dir.mkdir(parents=True, exist_ok=True)
    vectordb.save_local(str(settings.index_dir))
    return vectordb


@lru_cache(maxsize=1)
def get_embeddings() -> SentenceTransformerEmbeddings:
    return SentenceTransformerEmbeddings(model_name=settings.embedding_model)


@lru_cache(maxsize=1)
def get_vector_store() -> FAISS:
    if not _index_files_exist(settings.index_dir):
        return build_vector_store()

    return FAISS.load_local(
        str(settings.index_dir),
        get_embeddings(),
        allow_dangerous_deserialization=True,
    )


@lru_cache(maxsize=1)
def get_chain() -> ConversationalRetrievalChain:
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=SYSTEM_TEMPLATE,
    )
    llm = Ollama(model=settings.ollama_model, temperature=0.1)
    retriever = get_vector_store().as_retriever(search_kwargs={"k": settings.top_k})
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        combine_docs_chain_kwargs={"prompt": prompt},
        return_source_documents=True,
    )


def ask_question(request: ChatRequest) -> ChatResponse:
    chat_history = [(turn.question, turn.answer) for turn in request.history]
    result = get_chain()({"question": request.question, "chat_history": chat_history})
    source_items = []
    seen = set()

    for document in result.get("source_documents", []):
        source = str(document.metadata.get("source", "unknown"))
        if source not in seen:
            seen.add(source)
            source_items.append(SourceItem(source=source))

    return ChatResponse(answer=result["answer"], sources=source_items)
