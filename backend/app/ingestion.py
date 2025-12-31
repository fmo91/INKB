from pathlib import Path
from typing import List

from pypdf import PdfReader


def extract_text_from_pdf(path: str) -> str:
    # TODO: This loads the full extracted text into memory; switch to streaming
    # chunking when we optimize for very large PDFs.
    reader = PdfReader(Path(path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n\n".join(pages).strip()


def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and less than chunk_size.")

    normalized = " ".join(text.split())
    if not normalized:
        return []

    chunks: List[str] = []
    start = 0
    length = len(normalized)
    while start < length:
        end = min(length, start + chunk_size)
        chunks.append(normalized[start:end])
        if end == length:
            break
        start = end - overlap
    return chunks
