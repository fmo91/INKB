from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.chat import generate_answer
from app.db import get_session, init_db
from app.models import ChatMessage, Document, Ingestion
from app.retrieval import retrieve_top_chunks
from app.schemas import (
    ChatRequest,
    ChatResponse,
    Citation,
    DocumentResponse,
    IngestionResponse,
)
from app.settings import CHAT_TOP_K, CORS_ALLOWED_ORIGINS
from app.storage import ensure_upload_dir, save_upload_file

app = FastAPI(title="INKB API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS or ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()
    ensure_upload_dir()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/v1/documents", response_model=DocumentResponse)
def create_document(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> Document:
    if file.content_type not in {"application/pdf", "application/x-pdf"}:
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported.")

    storage_path, byte_size = save_upload_file(file, ensure_upload_dir())
    document = Document(
        original_filename=file.filename or "document.pdf",
        content_type=file.content_type or "application/pdf",
        storage_path=storage_path,
        byte_size=byte_size,
        status="uploaded",
    )
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


@app.get("/v1/documents/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    session: Session = Depends(get_session),
) -> Document:
    document = session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return document


@app.post(
    "/v1/documents/{document_id}/ingestions",
    response_model=IngestionResponse,
)
def create_ingestion(
    document_id: str,
    session: Session = Depends(get_session),
) -> Ingestion:
    document = session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    ingestion = Ingestion(document_id=document_id, status="queued", progress=0.0)
    session.add(ingestion)
    session.commit()
    session.refresh(ingestion)

    return ingestion


@app.get("/v1/ingestions/{ingestion_id}", response_model=IngestionResponse)
def get_ingestion(
    ingestion_id: str,
    session: Session = Depends(get_session),
) -> Ingestion:
    ingestion = session.get(Ingestion, ingestion_id)
    if ingestion is None:
        raise HTTPException(status_code=404, detail="Ingestion not found.")
    return ingestion


@app.post("/v1/documents/{document_id}/chat", response_model=ChatResponse)
def chat_with_document(
    document_id: str,
    payload: ChatRequest,
    session: Session = Depends(get_session),
) -> ChatResponse:
    document = session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    query = ""
    for message in reversed(payload.messages):
        if message.role == "user":
            query = message.content
            break
    if not query:
        raise HTTPException(status_code=400, detail="User message is required.")

    # Retrieve relevant chunks, then answer with an LLM (or a fallback).
    top_k = payload.top_k or CHAT_TOP_K
    chunks = retrieve_top_chunks(
        session,
        document_id=document_id,
        query=query,
        top_k=top_k,
    )

    citations = [Citation(chunk_id=chunk.id, quote=chunk.text[:400]) for chunk in chunks]
    answer = generate_answer(query, chunks)

    for message in payload.messages:
        session.add(
            ChatMessage(
                document_id=document_id,
                role=message.role,
                content=message.content,
            )
        )
    session.add(
        ChatMessage(
            document_id=document_id,
            role="assistant",
            content=answer,
        )
    )
    session.commit()

    return ChatResponse(
        answer=answer,
        citations=citations if payload.include_citations else [],
    )
