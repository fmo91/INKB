from fpdf import FPDF

from app.db import SessionLocal
from app.models import Chunk
from app.worker import process_next_ingestion


def _sample_pdf() -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 10, "Hello world. " * 20)
    data = pdf.output()
    if isinstance(data, str):
        return data.encode("latin-1")
    return bytes(data)


def test_upload_pdf_creates_document(client) -> None:
    response = client.post(
        "/v1/documents",
        files={"file": ("book.pdf", _sample_pdf(), "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"]
    assert body["original_filename"] == "book.pdf"
    assert body["status"] == "uploaded"
    assert body["byte_size"] > 0


def test_upload_rejects_non_pdf(client) -> None:
    response = client.post(
        "/v1/documents",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400


def test_ingestion_queue_and_process(client) -> None:
    upload = client.post(
        "/v1/documents",
        files={"file": ("book.pdf", _sample_pdf(), "application/pdf")},
    )
    document_id = upload.json()["id"]

    create_ingestion = client.post(f"/v1/documents/{document_id}/ingestions")
    assert create_ingestion.status_code == 200
    ingestion_id = create_ingestion.json()["id"]

    process_next_ingestion()

    status = client.get(f"/v1/ingestions/{ingestion_id}")
    assert status.status_code == 200
    body = status.json()
    assert body["status"] == "ready"
    assert body["progress"] == 1.0

    with SessionLocal() as session:
        chunks = session.query(Chunk).all()
    assert len(chunks) > 0
