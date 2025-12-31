# Feature 01: PDF Upload + Chat

## Summary

Enable a user to upload a single PDF book and ask natural-language questions
about it. Ingestion runs asynchronously with progress updates. Data is stored
locally in Postgres/pgvector.

## Goals

- Upload a PDF (including large books, e.g., 600+ pages).
- Ingest in the background with visible progress.
- Chat over the document with grounded answers.
- Keep the experience minimal and fast to iterate on (web-first UI).

## Non-Goals (for this feature)

- Multi-document library or switching between docs.
- Review/approval workflow for stable knowledge.
- External integrations (Kindle/Readwise/etc.).

## Assumptions

- Answers return citations/snippets by default for trust and traceability.
- Local storage is acceptable for both PDFs and embeddings.

## User Flow

1. User opens the app and sees a single-document upload screen.
2. User uploads a PDF.
3. Ingestion starts automatically and shows progress updates.
4. Once ready, the user can ask questions and receive answers with citations.

## API Requirements (MVP)

- POST /v1/documents
  - Accept multipart file upload for PDF.
  - Returns document ID.
- POST /v1/documents/{id}/ingestions
  - Starts background ingestion.
- GET /v1/ingestions/{id}
  - Returns status + progress.
- POST /v1/documents/{id}/chat
  - Answers questions with citations from the document.

## Data + Storage

- Store the raw PDF on local disk (path referenced in Postgres).
- Store parsed text chunks and embeddings in Postgres + pgvector.
- Keep ingestion state in a single table for simplicity (queued/running/ready).
- Use Ollama for local embeddings and chat when enabled.

## Ingestion Pipeline (Async)

1. Extract text from PDF.
2. Split into sections and chunks (overlap for better retrieval).
3. Create embeddings and index into pgvector.
4. Mark ingestion as ready.

Note: current extraction reads the full document text into memory; streaming
chunking will be added when we optimize for very large PDFs.

## Progress Notifications

- Ingestion status should be pollable via API.
- UI should show a simple progress indicator with step labels.

## UI (React Native Web)

- Upload screen with drag-and-drop and file picker.
- Ingestion progress view with status and percent.
- Chat screen (single document) with citations and “jump to snippet”.

## Acceptance Criteria

- A 600-page PDF can be uploaded without size limits enforced by the app.
- Ingestion runs in the background and exposes progress states.
- Chat answers are grounded in the uploaded PDF with citations.
- Web UI supports upload, progress, and chat end-to-end.
- Local Docker-based setup brings up API, worker, DB, and web with one command.

## Prerequisites (Conceptual)

- Retrieval-Augmented Generation (RAG): fetch relevant chunks and ground the
  answer in those excerpts.
- Embeddings + vector search: convert text to vectors and use pgvector to
  retrieve the nearest chunks by cosine distance.
- Chunking with overlap: split long documents into stable, queryable pieces.
- LangChain + Ollama: LangChain orchestrates prompts and the local LLM; Ollama
  serves the `nomic-embed-text` embeddings and `qwen3:8b` chat model.

## Prerequisites (Runtime)

- Postgres with pgvector enabled (Docker Compose already includes this).
- A worker process running alongside the API for ingestion.
- Ollama running locally if you want real answers (otherwise a fallback returns
  raw excerpts).

## Codebase Flow (Step by Step)

1. **Upload PDF** (`POST /v1/documents`)
   - `backend/app/main.py` accepts the multipart file.
   - `backend/app/storage.py` saves it to `backend/data/uploads/`.
   - A `Document` row is created with filename, MIME type, path, and status.

2. **Start ingestion** (`POST /v1/documents/{id}/ingestions`)
   - `backend/app/main.py` creates an `Ingestion` row with `queued` status.
   - This is the job the worker will pick up.

3. **Worker processes ingestion**
   - `backend/app/worker.py` polls for `queued` ingestions.
   - It loads the PDF (`backend/app/ingestion.py:extract_text_from_pdf`),
     chunking the text (`chunk_text`).
   - Existing chunks/embeddings for that document are cleared (single-document
     focus for now), then new `Chunk` + `Embedding` rows are written.
   - Status is set to `ready` with progress updates along the way.

4. **Embeddings**
   - `backend/app/embedding.py` uses `nomic-embed-text` via Ollama when enabled.
   - If Ollama is off, it falls back to deterministic hash embeddings so the
     pipeline still runs (quality is lower, but tests remain deterministic).

5. **Chat request** (`POST /v1/documents/{id}/chat`)
   - `backend/app/main.py` extracts the last user message.
   - `backend/app/retrieval.py` embeds the query and uses pgvector cosine
     distance to fetch top-k chunks.
   - `backend/app/chat.py` builds the prompt with the retrieved context and
     sends it to the chat model (or returns excerpts in fallback mode).
   - `ChatMessage` records are stored and citations are returned in the
     response.

6. **Frontend flow**
   - `frontend/App.tsx` uploads the PDF, starts ingestion immediately, and
     polls `/v1/ingestions/{id}` for progress.
   - Once ready, it sends messages to `/v1/documents/{id}/chat` and renders the
     answer with inline citations.
