import os
import time

from app.db import SessionLocal, init_db
from app.embedding import embed_text
from app.ingestion import chunk_text, extract_text_from_pdf
from app.models import Chunk, Document, Embedding, Ingestion


POLL_INTERVAL_SECONDS = 1.0
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1200"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))


def process_next_ingestion() -> bool:
    with SessionLocal() as session:
        ingestion = (
            session.query(Ingestion)
            .filter(Ingestion.status == "queued")
            .order_by(Ingestion.created_at.asc())
            .first()
        )
        if ingestion is None:
            return False

        ingestion.status = "running"
        ingestion.progress = 0.1
        session.commit()

        document = session.get(Document, ingestion.document_id)
        if document is None:
            ingestion.status = "failed"
            ingestion.progress = 0.0
            session.commit()
            return True

        try:
            text = extract_text_from_pdf(document.storage_path)
        except Exception:
            ingestion.status = "failed"
            ingestion.progress = 0.0
            session.commit()
            return True

        # Progress is coarse-grained (extract -> chunk/embed -> ready).
        ingestion.progress = 0.6
        session.commit()

        # Single-document focus: replace previous chunks/embeddings on re-ingest.
        session.query(Embedding).filter(Embedding.document_id == document.id).delete()
        session.query(Chunk).filter(Chunk.document_id == document.id).delete()
        chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
        for index, chunk in enumerate(chunks):
            chunk_record = Chunk(
                document_id=document.id,
                ingestion_id=ingestion.id,
                index=index,
                text=chunk,
            )
            session.add(chunk_record)
            session.flush()
            session.add(
                Embedding(
                    document_id=document.id,
                    chunk_id=chunk_record.id,
                    vector=embed_text(chunk),
                )
            )

        ingestion.status = "ready"
        ingestion.progress = 1.0
        session.commit()
        return True


def main() -> None:
    init_db()
    while True:
        processed = process_next_ingestion()
        if not processed:
            time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
