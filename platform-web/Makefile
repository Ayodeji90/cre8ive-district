.PHONY: dev up down migrate revision test lint typecheck fmt worker agent website-agent

up:
	docker compose up -d postgres redis branding-agent website-agent

down:
	docker compose down

dev:
	cd api && uvicorn app.main:app --reload --port 8000

worker:
	cd api && arq app.worker.WorkerSettings

agent:
	cd services/branding-agent && uvicorn branding_agent.api.app:app --reload --port 8001

website-agent:
	cd services/website-agent && uvicorn website_agent.api.app:app --reload --port 8002

migrate:
	cd api && alembic upgrade head

revision:
	cd api && alembic revision --autogenerate -m "$(m)"

test:
	cd api && python -m pytest
	cd services/branding-agent && PYTHONPATH=src python -m pytest
	cd services/website-agent && PYTHONPATH=src python -m pytest

lint:
	cd api && ruff check .
	cd services/branding-agent && ruff check src tests
	cd services/website-agent && ruff check src tests

fmt:
	cd api && ruff format .
	cd services/branding-agent && ruff format src tests
	cd services/website-agent && ruff format src tests

typecheck:
	cd api && pyright app
