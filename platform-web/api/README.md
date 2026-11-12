# Cre8ive District API

FastAPI backend for the Cre8ive District brand-launch platform: conversations with
Abija, Paystack billing, designer approval queue, Branding Agent integration and delivery.

## Quickstart

```bash
cd api
cp .env.example .env
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"

cd ..
docker compose up -d postgres redis branding-agent website-agent
cd api && .venv/bin/alembic upgrade head
.venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Branding Agent health: http://localhost:8001/health
- Website Agent health: http://localhost:8002/health
- Worker (brand generation, rendering, delivery): `.venv/bin/arq app.worker.WorkerSettings`

## Layout

```
app/
├── main.py         middleware, lifespan, error handling, router mounting
├── config.py       environment settings
├── db.py           async engine + session
├── auth.py         NextAuth JWT verification + role checks
├── deps.py         injectable Redis / storage / Paystack / AI dependencies
├── models/         8 SQLAlchemy tables
├── schemas/        request/response contracts, including the AI output contract
├── routers/        HTTP + WebSocket endpoints
├── services/       billing, chat transport, reviews, assets, delivery, jobs
├── llm/            Branding Agent HTTP client and response contracts
├── templates/      delivery email
└── worker.py       arq background jobs
```

## AI integration seam

The platform API and worker call the independently deployable Branding Agent
over HTTP. Configure `BRANDING_AGENT_URL` and `BRANDING_AGENT_API_KEY` in the
API environment; provider keys and `AI_STUB` belong to the Branding Agent.
For local development, the agent uses `AI_STUB=true` and the Compose
development key unless overridden with `BRANDING_AGENT_API_KEY`.
The Website Agent is a separate service and is not yet connected to a website
generation workflow.

## Payment flow

1. `POST /api/billing/initialize` creates a pending order and a Paystack transaction.
2. Paystack calls `POST /api/webhooks/paystack` (HMAC SHA512 verified, idempotent).
3. Paid orders enqueue brand generation.
4. Designer approves in `/api/admin/reviews/{id}/approve`, which enqueues asset
   rendering; the worker delivers the signed kit link by email.

## Commands

```bash
make up          # postgres + redis + both agent services
make migrate     # alembic upgrade head
make dev         # uvicorn --reload
make worker      # arq worker
make test        # pytest
make lint        # ruff
make typecheck   # pyright
```
