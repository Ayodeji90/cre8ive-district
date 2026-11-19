# Local stack: start, health, and chat-start diagnosis

The local stack runs Postgres, Redis, a one-shot migration gate, the API, the ARQ worker,
and the three agents (Branding Agent, Website Agent, Run Engine).

## Start

```bash
cp .env.example .env          # once; then fill JWT_SECRET and any provider keys
cd platform-web
make up                       # build + start everything in dependency order
make doctor-wait              # wait up to 120s for every check to pass
make doctor                   # PASS/FAIL report per service, dependency, and key
```

`make up` starts services in this order:

```
postgres, redis
      │
      ▼
   migrate            # alembic upgrade head, must exit 0
      │
      ├──────────────► api        (waits for migrate + all agents)
      └──────────────► worker     (waits for migrate + all agents)

branding-agent, website-agent, run-engine   (start in parallel, healthchecked)
```

`api` is held back until every agent is `healthy`, so a request cannot reach a
half-started stack. If `migrate` fails, `api` and `worker` never start.

## Commands

| Command | What it does |
| --- | --- |
| `make up` | Build and start the full stack in the background |
| `make infra` | Postgres + Redis only (for running `make dev` on the host) |
| `make status` | `docker compose ps` table |
| `make doctor` | Full diagnosis: prerequisites, env, container health, endpoints, service keys, `/health/deps` |
| `make doctor-wait` | Same report, polling for up to 120s (CI-like gate) |
| `make logs` | Follow all logs |
| `make down` | Stop and remove containers (keeps the Postgres volume) |
| `docker compose down -v` | Also delete the database volume |

## Health endpoints

| Endpoint | Checks | Use |
| --- | --- | --- |
| `GET :8000/health` | Process is up | Liveness, ALB target |
| `GET :8000/health/db` | Postgres round-trip | API container healthcheck |
| `GET :8000/health/deps` | Postgres, Redis, and the authenticated `/v1/ping` of each agent | Chat-start diagnosis and deploy smoke |
| `GET :8001/health` | Branding Agent process | Compose healthcheck |
| `GET :8002/health` | Website Agent process | Compose healthcheck |
| `GET :8003/health` | Run Engine process | Compose healthcheck |
| `GET :8001/8002/8003 /v1/ping` | Agent process **and** service key | Checked by `/health/deps` |

`/health/deps` returns `503` with a per-dependency body when anything is down:

```bash
curl -s localhost:8000/health/deps | python3 -m json.tool
```

## "Chat does not start" triage

Run `make doctor` first; it checks all of these.

| Symptom | Check | Fix |
| --- | --- | --- |
| `api` never starts | `docker compose ps` shows `migrate` exited non-zero | `docker compose logs migrate`; fix the migration, then `make down && make up` |
| `api` restarts | `docker compose logs api` | Usually bad `DATABASE_URL`/`REDIS_URL` or an import error |
| `branding-agent` unhealthy | `docker compose logs branding-agent` | The container must import cleanly; check the traceback |
| Chat returns 401/502 | `API BRANDING_AGENT_API_KEY` vs `branding-agent SERVICE_API_KEY` | `make doctor` reports a mismatch; make them equal in `.env` |
| `401` from NextAuth callback | `AUTH_SECRET` != `JWT_SECRET` | Set both to the same value; `make doctor` warns |
| Website generation stuck | `docker compose logs website-agent worker` | Check `OPENROUTER_API_KEY` when `AI_STUB=false`; Redis must be up for the worker |
| Run Engine stuck in `starting` | `docker compose logs run-engine` | Check `DATABASE_URL`, `REDIS_URL`, and `PLATFORM_API_URL=http://api:8000` |
| Everything green but chat is silent | `curl localhost:8000/health/deps` | Confirms whether the failure is upstream (agents) or in the LLM provider |

## Notes

- Compose healthchecks use Python's `urllib` because the slim images do not ship `curl`.
- The `api` and `worker` containers mount `./api`, so code changes need no rebuild; the API
  reloads automatically, while the worker needs `docker compose restart worker`. Dependency
  changes require `make up` (it rebuilds) or `docker compose build`.
- `migrate` also mounts `./api`, so it applies the migrations in your working tree.
- The Postgres volume persists across `make down`. Use `docker compose down -v` for a clean
  database.
