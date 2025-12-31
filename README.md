# INKB (Invisible Knowledge Base)

INKB is a reading copilot that captures and organizes learnings from books,
articles, podcasts, and talks. The MVP focuses on automatically generating
notes, a glossary with citations, and chat-based Q&A over a document.

## Vision

- Read a document and get auto-generated notes, glossary, and summaries.
- Ask questions and receive answers with citations.
- Review and approve staged knowledge into a stable, merged knowledge base.

## MVP Scope

- Document ingestion and parsing.
- Auto notes, summaries, glossary, and concept relations.
- Chat over the active document with citations.
- Review workflow stubbed for later consolidation.

## Docs

- API surface: `docs/api.md`
- Feature spec: `docs/feature-01-pdf-chat.md`
- Agent workflow: `AGENTS.md`

## Development

Backend, worker, Postgres, and the web UI can be started with:

```sh
docker compose up --build
```

Then hit the health check:

```sh
curl http://localhost:8000/health
```

Open the web app at:

```sh
http://localhost:19006
```

If the web app is blocked by CORS, set `CORS_ALLOWED_ORIGINS` in `.env` to
include the frontend origin (comma-separated).

To run backend tests in Docker:

```sh
docker compose run --rm backend sh -c "pip install -r requirements-dev.txt && pytest"
```

Frontend (Expo Web) local dev:

```sh
cd frontend
npm install
npm run web
```

If the API is not on `http://localhost:8000`, set
`EXPO_PUBLIC_API_BASE_URL` in `frontend/.env` (copy from
`frontend/.env.example`).

Frontend tests:

```sh
cd frontend
npm test
npx playwright install --with-deps chromium
npm run test:e2e
```

### Ollama (Local LLM)

To enable local embeddings + chat via Ollama:

- Set `OLLAMA_ENABLED=true` and `OLLAMA_BASE_URL` in `.env`.
- Ensure models are available locally:
  - `ollama pull nomic-embed-text`
  - `ollama pull qwen3:8b`
- `EMBEDDING_DIM` defaults to `768` for `nomic-embed-text`.
- Re-ingest documents if you change embedding models or dimensions.
- If the database was created with a different `EMBEDDING_DIM`, reset the DB
  (or drop the `embeddings` table) before re-ingesting.

## CI

- GitHub Actions runs backend tests plus frontend Jest + Playwright on push
  and PRs targeting `main` using Docker Compose.

## API Testing (Bruno)

- Bruno collection lives in `bruno/`.
- Set `baseUrl` in `bruno/environments/local.bru`.
- Use the Upload request first and select a PDF file in the request body.
- Paste the returned IDs into `documentId` and `ingestionId` in the environment.
- Use the Chat request after ingestion is ready to validate retrieval output.

## Status

This repo is in early planning with an initial backend scaffold. The API draft
and feature spec live in `docs/` and will evolve as implementation proceeds.
