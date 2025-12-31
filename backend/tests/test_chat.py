from fpdf import FPDF

from app.worker import process_next_ingestion


def _sample_pdf() -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 10, "Distributed systems rely on replication.")
    data = pdf.output()
    if isinstance(data, str):
        return data.encode("latin-1")
    return bytes(data)


def test_chat_returns_citations(client) -> None:
    upload = client.post(
        "/v1/documents",
        files={"file": ("book.pdf", _sample_pdf(), "application/pdf")},
    )
    document_id = upload.json()["id"]

    create_ingestion = client.post(f"/v1/documents/{document_id}/ingestions")
    ingestion_id = create_ingestion.json()["id"]

    process_next_ingestion()

    status = client.get(f"/v1/ingestions/{ingestion_id}")
    assert status.json()["status"] == "ready"

    response = client.post(
        f"/v1/documents/{document_id}/chat",
        json={
            "messages": [{"role": "user", "content": "What is this about?"}],
            "top_k": 3,
            "include_citations": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"]
    assert len(body["citations"]) > 0
    assert body["citations"][0]["chunk_id"]
