from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.embedding import embed_text
from app.models import Chunk, Embedding


def retrieve_top_chunks(
    session: Session,
    document_id: str,
    query: str,
    top_k: int,
) -> List[Chunk]:
    if top_k <= 0:
        return []

    # pgvector cosine distance provides approximate relevance ordering.
    # See https://www.pinecone.io/learn/vector-search-basics/ for a quick intro.
    query_vector = embed_text(query)
    stmt = (
        select(Chunk)
        .join(Embedding, Embedding.chunk_id == Chunk.id)
        .where(Embedding.document_id == document_id)
        .order_by(Embedding.vector.cosine_distance(query_vector))
        .limit(top_k)
    )
    result = session.execute(stmt).scalars().all()
    return result
