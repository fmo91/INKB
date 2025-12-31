import time

from app.db import SessionLocal, init_db
from app.models import Ingestion


POLL_INTERVAL_SECONDS = 1.0


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
        ingestion.progress = 0.2
        session.commit()

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
