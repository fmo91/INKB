import pytest
from fastapi.testclient import TestClient

from app.db import SessionLocal, init_db
from app.main import app
from app.models import ChatMessage, Chunk, Document, Embedding, Ingestion
from app.storage import ensure_upload_dir


@pytest.fixture(autouse=True)
def clean_db() -> None:
    init_db()
    ensure_upload_dir()
    with SessionLocal() as session:
        session.query(ChatMessage).delete()
        session.query(Embedding).delete()
        session.query(Chunk).delete()
        session.query(Ingestion).delete()
        session.query(Document).delete()
        session.commit()
    yield


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as client:
        yield client
