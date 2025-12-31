# INKB API Surface (MVP)

This document captures the first-pass API surface for the reading flow:
document ingest -> auto notes/glossary/summaries -> chat. Review endpoints are
included as stubs for the next phase.

## Conventions

- Base path: /v1
- Auth: Authorization: Bearer <token>
- Pagination: limit, cursor
- Status: staged | stable | rejected
- Error shape:

```json
{
  "error": {
    "code": "...",
    "message": "...",
    "details": {}
  }
}
```

## Documents

- POST /v1/documents
  - Create a document from a PDF file upload (multipart/form-data).
- GET /v1/documents
  - List documents.
- GET /v1/documents/{id}
  - Fetch document metadata and status.
- DELETE /v1/documents/{id}
  - Delete document.

## Ingestion

- POST /v1/documents/{id}/ingestions
  - Start the ingestion pipeline.
- GET /v1/ingestions/{id}
  - Ingestion status/progress.
- GET /v1/documents/{id}/ingestions
  - List ingestions for a document.

## Reader Data

- GET /v1/documents/{id}/sections
- GET /v1/sections/{id}/chunks
- GET /v1/documents/{id}/summaries?level=document|section&status=...
- GET /v1/documents/{id}/notes?kind=auto|user&status=...
- POST /v1/documents/{id}/notes
  - Add a user note (optionally anchored to a chunk/offset).
- GET /v1/documents/{id}/glossary?status=...
- GET /v1/glossary/{term_id}
  - Term detail + occurrences.
- GET /v1/documents/{id}/concept-graph?status=...
  - Nodes + edges for diagrams.

## Search & Chat

- GET /v1/documents/{id}/search?q=...&top_k=...
- POST /v1/documents/{id}/chat
  - Non-stream response.
- POST /v1/documents/{id}/chat/stream
  - Server-sent events (SSE) stream.

## Review (Phase 2 stub)

- GET /v1/review/queue?document_id&entity_type=...&status=staged
- POST /v1/review/decisions
  - Approve/reject/merge staged items.
- GET /v1/knowledge/terms
  - List stable terms.

## Request/Response Shapes (MVP)

### Create document

POST /v1/documents

Request (multipart/form-data)

- file: PDF file

Response

```json
{
  "id": "doc_123",
  "original_filename": "book.pdf",
  "content_type": "application/pdf",
  "byte_size": 123456,
  "status": "uploaded",
  "created_at": "2025-01-01T12:00:00Z"
}
```

### Start ingestion

POST /v1/documents/{id}/ingestions

```json
{
  "options": {
    "summaries": true,
    "glossary": true,
    "concept_graph": true
  }
}
```

Response

```json
{
  "ingestion_id": "ing_456",
  "status": "queued",
  "progress": 0.0
}
```

### Chat with document

POST /v1/documents/{id}/chat

```json
{
  "messages": [
    {
      "role": "user",
      "content": "What is eventual consistency?"
    }
  ],
  "top_k": 5,
  "include_citations": true
}
```

Response

```json
{
  "answer": "Relevant excerpts:\n- ...",
  "citations": [
    {
      "chunk_id": "chk_789",
      "quote": "..."
    }
  ]
}
```

### Review decisions (phase 2)

POST /v1/review/decisions

```json
{
  "decisions": [
    {
      "entity_type": "glossary_term",
      "entity_id": "term_42",
      "decision": "approve",
      "merge_target_id": null
    }
  ]
}
```
