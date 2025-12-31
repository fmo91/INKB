from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db import get_session, init_db
from app.models import Document, Ingestion
from app.schemas import DocumentResponse, IngestionResponse
from app.storage import ensure_upload_dir, save_upload_file

app = FastAPI(title="INKB API", version="0.1.0")


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
