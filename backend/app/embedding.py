import hashlib
import math
import re
from functools import lru_cache
from typing import List, Optional

from langchain_community.embeddings import OllamaEmbeddings

from app.settings import (
    EMBEDDING_DIM,
    OLLAMA_BASE_URL,
    OLLAMA_EMBED_MODEL,
    OLLAMA_ENABLED,
)


def _hash_embed(text: str, dimension: int) -> List[float]:
    tokens = re.findall(r"\w+", text.lower())
    vector = [0.0] * dimension
    for token in tokens:
        digest = hashlib.sha1(token.encode("utf-8")).hexdigest()
        index = int(digest, 16) % dimension
        vector[index] += 1.0

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0.0:
        return vector
    return [value / norm for value in vector]


@lru_cache(maxsize=1)
def _ollama_embedder() -> Optional[OllamaEmbeddings]:
    if not OLLAMA_ENABLED:
        return None
    if not OLLAMA_BASE_URL or not OLLAMA_EMBED_MODEL:
        return None
    return OllamaEmbeddings(
        model=OLLAMA_EMBED_MODEL,
        base_url=OLLAMA_BASE_URL,
    )


def embed_text(text: str) -> List[float]:
    if EMBEDDING_DIM <= 0:
        raise ValueError("EMBEDDING_DIM must be positive.")

    # Use Ollama embeddings when enabled, otherwise fall back to a deterministic hash.
    embedder = _ollama_embedder()
    if embedder is None:
        return _hash_embed(text, EMBEDDING_DIM)

    vector = embedder.embed_query(text)
    if len(vector) != EMBEDDING_DIM:
        raise ValueError(
            "Embedding dimension mismatch. Update EMBEDDING_DIM to match "
            f"{OLLAMA_EMBED_MODEL} (got {len(vector)})."
        )
    return vector
