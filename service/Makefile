# Makefile for DDD FastAPI Service using uv

PY=uv run python
UV=uv
APP=app.main

.PHONY: help setup dev run test lint format typecheck clean build freeze

help:
	@echo "Common tasks:"
	@echo "  make setup      - create venv and install deps (uv sync)"
	@echo "  make dev        - run app with auto-reload"
	@echo "  make run        - run app"
	@echo "  make test       - run pytest"
	@echo "  make lint       - run ruff"
	@echo "  make format     - run ruff format"
	@echo "  make typecheck  - run mypy"
	@echo "  make clean      - remove caches"
	@echo "  make build      - build wheel"
	@echo "  make freeze     - export lock file"

setup:
	$(UV) sync --all-groups

# Development server with reload
dev:
	PYTHONPATH=src uv run uvicorn app.main:app --reload --host 0.0.0.0 --port $${PORT:-8000}

run:
	PYTHONPATH=src uv run uvicorn app.main:app --host 0.0.0.0 --port $${PORT:-8000}

test:
	PYTHONPATH=src uv run pytest

lint:
	uv run ruff check src

format:
	uv run ruff format src

typecheck:
	PYTHONPATH=src uv run mypy src/app

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache build dist __pycache__ src/**/__pycache__

build:
	uv build

freeze:
	uv export --format requirements-txt > requirements.txt
