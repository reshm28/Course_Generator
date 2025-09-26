# Course Generator Agent

Production-ready FastAPI backend following Domain-Driven Design (DDD) and Clean Architecture, with LangGraph for Course Generator Agent AI workflow orchestration.

## Structure

- `src/app/domain/` — Entities, Value Objects, Domain Services, Events, Repository interfaces
- `src/app/application/` — Use Cases (Application Services) and AI Workflows (LangGraph)
- `src/app/infrastructure/` — Implementations: repositories, db models, external clients
- `src/app/interfaces/` — FastAPI routes, controllers, schemas, dependencies, middleware

## Getting Started

1. Install uv (if not installed): https://docs.astral.sh/uv/getting-started/installation/
2. Setup environment and dependencies:

```bash
make setup
```

3. Copy env template and edit as needed:

```bash
cp .env.example .env
```

4. Run dev server with reload:

```bash
make dev
```

FastAPI docs at http://localhost:8000/docs

## Tests

```bash
make test
```

## Lint & Format

```bash
make lint
make format
```

## Notes

- LangGraph sample workflow is implemented in `src/app/application/workflows/ai_graph.py` and exposed at `GET /ai/echo?text=...`.
- Replace the placeholder model in `ai_graph.py` with a real LLM integration and provider when ready.
