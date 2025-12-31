import os


# Centralized settings for embeddings + chat behavior.
def _bool_env(name: str, default: str = "false") -> bool:
    value = os.getenv(name, default).strip().lower()
    return value in {"1", "true", "yes", "on"}


EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "768"))

OLLAMA_ENABLED = _bool_env("OLLAMA_ENABLED")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "qwen3:8b")

CHAT_TOP_K = int(os.getenv("CHAT_TOP_K", "5"))
CHAT_TEMPERATURE = float(os.getenv("CHAT_TEMPERATURE", "0"))
