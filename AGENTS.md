# AGENTS.md

This file defines how Codex should work in this repo.

## Operating Principles

- Use a stricter workflow: confirm scope, plan before nontrivial work, execute
  stepwise.
- Tests are the primary success criteria; do not claim completion without
  running them.
- Prefer simple solutions over clever ones.
- Minimize cognitive load: favor pure functions and self-contained modules
  whenever possible.
- Update docs on every change to keep context fresh for humans and agents.
- Prefer small, reviewable diffs; avoid speculative refactors.
- Ask clarifying questions when requirements are ambiguous.

## Workflow

1. Clarify scope and acceptance criteria.
2. Make a plan for nontrivial tasks, then execute it step by step.
3. Keep changes minimal and aligned with the requested feature.
4. Report results with what changed, why, tests, risks, and next steps.

## Feature Delivery Loop

- Discuss the feature and implementation approach.
- Write a spec and plan (with checkboxes).
- Implement iteratively.
- Run tests to validate success criteria.
- Iterate based on feedback.

## Testing and Quality Gates

- Always run relevant tests.
- If no tests exist, state that explicitly and propose the smallest useful
  tests to add next.
- If tests fail, report failures and do not present the code as complete.

## Docs

- Update or add docs on every change (README and/or docs/).
- Keep docs in sync with implementation and API changes.

## Tech Defaults

Backend:
- Python with FastAPI and the LangChain/LangGraph ecosystem.
- Postgres with pgvector for storage and semantic search.

Frontend:
- TypeScript with React Native; web support must stay working.

Infra:
- Docker is required.
- Provide a single command that runs backend and client together.

## Dev Runbook (Expected)

- Single command to run everything: `docker compose up --build`.
- If new services or env vars are added, update `docker-compose.yml` and
  `.env.example`.

## PR Etiquette / Response Format

- Always include: what changed, why, tests run (or why not), risks, and next
  steps.
- Call out assumptions and open questions.
