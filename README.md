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

Backend and Postgres can be started with:

```sh
docker compose up --build
```

Then hit the health check:

```sh
curl http://localhost:8000/health
```

The frontend is not scaffolded yet; this command currently starts the backend
and database only.

To run backend tests in Docker:

```sh
docker compose run --rm backend sh -c "pip install -r requirements-dev.txt && pytest"
```

## Status

This repo is in early planning with an initial backend scaffold. The API draft
and feature spec live in `docs/` and will evolve as implementation proceeds.
