import os
import uuid
from pathlib import Path
from typing import Tuple

from fastapi import UploadFile


def upload_dir() -> Path:
    return Path(os.getenv("UPLOAD_DIR", "./data/uploads")).resolve()


def ensure_upload_dir() -> Path:
    path = upload_dir()
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_upload_file(upload: UploadFile, dest_dir: Path) -> Tuple[str, int]:
    filename = upload.filename or "document.pdf"
    safe_name = f"{uuid.uuid4()}_{filename}"
    destination = dest_dir / safe_name

    size = 0
    with destination.open("wb") as buffer:
        while True:
            chunk = upload.file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            buffer.write(chunk)

    upload.file.close()
    return str(destination), size
