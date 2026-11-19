.PHONY: up infra down migrate revision dev worker agent website-agent run-engine \
	status doctor doctor-wait logs test lint fmt typecheck check

COMPOSE_ENV := $(if $(wildcard ../.env),--env-file ../.env,)
COMPOSE := docker compose $(COMPOSE_ENV)

# Full local stack: postgres, redis, migrate, api, worker and the three agents.
up:
	$(COMPOSE) up -d --build

# Infrastructure only, for running api/agents with `make dev` etc.
infra:
	$(COMPOSE) up -d postgres redis

down:
	$(COMPOSE) down

# Apply migrations through the one-shot compose gate.
migrate:
	$(COMPOSE) run --rm migrate

revision:
	cd api && alembic revision --autogenerate -m "$(m)"

status:
	$(COMPOSE) ps

doctor:
	./scripts/doctor.sh

doctor-wait:
	./scripts/doctor.sh --wait 120

logs:
	$(COMPOSE) logs -f --tail=100

# Run services on the host (requires the infra containers and a local venv).
dev:
	cd api && uvicorn app.main:app --reload --port 8000

worker:
	cd api && arq app.worker.WorkerSettings

agent:
	cd services/branding-agent && uvicorn branding_agent.api.app:app --reload --port 8001

website-agent:
	cd services/website-agent && uvicorn website_agent.api.app:app --reload --port 8002

run-engine:
	cd services/run-engine && PYTHONPATH=src uvicorn run_engine.api.app:app --reload --port 8003

test:
	cd api && python -m pytest
	cd services/branding-agent && PYTHONPATH=src python -m pytest
	cd services/website-agent && PYTHONPATH=src python -m pytest
	cd services/run-engine && PYTHONPATH=src python -m pytest

lint:
	cd api && ruff check . && ruff format --check .
	cd services/branding-agent && ruff check src tests && ruff format --check src tests
	cd services/website-agent && ruff check src tests && ruff format --check src tests
	cd services/run-engine && ruff check src tests && ruff format --check src tests

fmt:
	cd api && ruff format .
	cd services/branding-agent && ruff format src tests
	cd services/website-agent && ruff format src tests
	cd services/run-engine && ruff format src tests

typecheck:
	cd api && pyright app

# Same checks CI runs, in one command.
check: lint test
