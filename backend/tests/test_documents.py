from app.worker import process_next_ingestion


def _sample_pdf() -> bytes:
    return b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"


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
