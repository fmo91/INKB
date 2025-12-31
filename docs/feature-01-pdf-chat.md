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

## Implementation Plan

- [x] Define database tables for documents and ingestions.
- [x] Define tables for chunks.
- [ ] Define tables for embeddings and chat.
- [x] Implement PDF upload endpoint (multipart) and local file storage.
- [x] Add ingestion worker to extract text and create chunks.
- [x] Add ingestion status/progress updates with simple polling.
- [ ] Implement chat endpoint with retrieval + citations.
- [ ] Build minimal React Native Web UI (upload, progress, chat).
- [x] Provide Docker compose to run API, worker, and DB in one command.
- [ ] Add web service to Docker compose.
- [x] Add tests for upload and ingestion.
- [ ] Add tests for chat retrieval.
- [x] Update docs with any API or UX changes during implementation.
