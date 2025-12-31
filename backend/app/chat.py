from functools import lru_cache
from typing import Iterable

from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

from app.models import Chunk
from app.settings import (
    CHAT_TEMPERATURE,
    OLLAMA_BASE_URL,
    OLLAMA_CHAT_MODEL,
    OLLAMA_ENABLED,
)


SYSTEM_PROMPT = (
    "You are a reading copilot. Answer the user's question using only the "
    "provided context. If the context is insufficient, say you don't know."
)


@lru_cache(maxsize=1)
def _ollama_llm() -> ChatOllama | None:
    if not OLLAMA_ENABLED:
        return None
    if not OLLAMA_BASE_URL or not OLLAMA_CHAT_MODEL:
        return None
    return ChatOllama(
        model=OLLAMA_CHAT_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=CHAT_TEMPERATURE,
    )


def _format_context(chunks: Iterable[Chunk]) -> str:
    lines = []
    for chunk in chunks:
        lines.append(f"[{chunk.id}] {chunk.text}")
    return "\n\n".join(lines)


def generate_answer(query: str, chunks: list[Chunk]) -> str:
    llm = _ollama_llm()
    if llm is None:
        # Fallback for local/dev when Ollama is not configured.
        if not chunks:
            return "No relevant content found in this document yet."
        lines = ["Relevant excerpts:"]
        lines.extend(f"- {chunk.text[:400]}" for chunk in chunks)
        return "\n".join(lines)

    context = _format_context(chunks)
    message = (
        f"Question:\n{query}\n\n"
        f"Context:\n{context}\n\n"
        "Answer:"
    )
    response = llm.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=message),
        ]
    )
    return response.content.strip()
