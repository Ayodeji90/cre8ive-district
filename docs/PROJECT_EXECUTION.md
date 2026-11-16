# Cre8ive District — Project Execution Tracker

**Canonical record of implementation, gaps, verification, and next actions**

**Reviewed:** 16 November 2026

## Status rules

- **Implemented:** code exists in the current workspace.
- **Partial:** some of the workflow exists, but a required user or operational outcome is missing.
- **Verified:** acceptance behavior has current test or deployed-runtime evidence recorded here.
- **Planned:** documented intention only.

Code presence is not production completion. Do not use “completed” without evidence for the full acceptance path.

## Current snapshot

The repository contains three Next.js apps, a FastAPI platform API, a background worker, and separate Branding Agent, Website Agent, and Run Engine services. Local PostgreSQL and Redis are defined in Docker Compose. The marketing app presents the AI brand-launch product and has a waitlist.

The main product path is partly connected: authenticated chat captures business facts; chat completion queues website generation; the worker can create missing brand data and call the Website Agent; website job state, diagnostics, and retry are persisted and exposed. Billing, review, asset delivery, and autonomous-run foundations also exist.

**Overall: active MVP implementation; not yet demonstrated production-ready.** No capability below is marked Verified without current evidence.

## What is in the code now

| Area | Implementation present | Remaining gap / limit |
|---|---|---|
| Marketing | Next.js marketing site and waitlist submission route. An older static website remains at repo root as reference. | Verify deployed waitlist receipt, domain, claims, metadata, responsive/accessibility behavior. Current “AI employee does all the work” style claims must match actual capability. |
| Customer workspace | Authenticated app, sign-in/sign-up/welcome pages, streamed Abija chat, split preview UI, billing top-up UI, typed API client. | Browser-level end-to-end verification; recheck typecheck/build after recent changes. |
| Authentication | Auth.js providers/backend adapter, backend JWT validation, conversation ownership checks, role/owner protections on key routes. | Verify account lifecycle, expiry/revocation, every customer-owned route, rate limits, production secrets and rotation. |
| Intake/chat | WebSocket chat, stored history, context extraction and business-record updates, website generation trigger. | Verify reconnects, Redis loss, concurrent sessions, model failures, rate limiting, and data consistency. |
| Platform API/data | FastAPI, SQLAlchemy models, Alembic migrations, routes for users, businesses, brands, chat, billing, reviews, assets, delivery, agent runs, waitlist, websites. | Audit authorization and migrations route by route; ensure all current migrations work on a clean and upgraded database. |
| Brand generation | Platform workflow saves strategy, logo references, palette, fonts, copy and validation, creates review records; worker renders assets. Branding Agent has structured intake/strategy/provider/validation code. | Verify complete package contract and user download/revision lifecycle end to end. Uploaded-file parsing and broader collateral are not present. |
| Human review | Backend review list/detail/claim/approve/revise/reject endpoints; approval can enqueue rendering. | Admin app remains a scaffold; build a usable review queue and auditable operator flow. |
| Billing/credits | Paystack initialize/verify/webhook path, order and credit ledger, balances/deductions, UI methods. | Verify sandbox payments, webhook duplicates/replay, refunds/reconciliation, business ownership, and idempotent credit charging. |
| Assets/delivery | Storage abstraction, asset rendering, signed links/email delivery path, delivery job. | Verify provider permissions, link expiry, job retry, delivery success/failure, and recovery. |
| Website Agent | Site specification, AI-copy provider path, template-based rendering, quality checker, persistent repository, Vercel deployer, health/readiness routes. | Validate live generation quality, deployment errors/redeploys/domains, and persistence under restart. Templates provide structure; this is not arbitrary code generation. |
| Website jobs | PostgreSQL job state, tokenized deterministic enqueue, attempt/error metadata, periodic recovery, owner status/retry API, workspace diagnostics. Migration: a09c68f54b21. | Apply migration and test Redis outage, worker crash, stale recovery, duplicate enqueue, retries, owner UI, and no false “live” status. Not tested in this change. |
| Run Engine | Persistent run/task/event state, PostgreSQL advisory locks, active-run recovery, pause/resume/cancel/approval, SSE, budget/permissions. | Non-stub execution currently creates reviewable draft artifacts; real website/social/outreach actions are not implemented. Add external action safety/idempotency if autonomous execution stays in scope. |
| CI/contracts | Backend GitHub Actions lint/typecheck/test workflow; versioned branding intake/strategy JSON schemas. | Frontend and agent/run-engine CI coverage is incomplete or unconfirmed; generated brand package and event lifecycle contracts need definition before broader orchestration. |

Implementation map: **platform-web/apps/** (web), **platform-web/api/app/** (API), **platform-web/api/app/worker.py** (worker), **platform-web/services/** (agents and Run Engine), **platform-web/contracts/** (shared schemas), **platform-web/docker-compose.yml** (local stack).

## Next actions, in priority order

### P0 — Restore confidence in verification

1. Run the current API suite and resolve any collection errors. Earlier checks found ModuleNotFoundError for tests in four modules; test setup changed afterward, so confirm current state.
2. Diagnose the Run Engine repository lifecycle test that previously hung beyond 30 seconds. Bound the failure and verify Postgres-backed run recovery and locking.
3. Diagnose the Website Agent suite that previously stalled at its health test; confirm persistence tests run.
4. Run relevant backend, agent, Run Engine, and frontend checks and record exact command, result, date, and revision.
5. Add cross-service tests for ownership, retries, restart recovery, and the customer-visible status path. Passing isolated tests alone does not prove the product workflow.

**Previous test evidence, not reverified:** ten original Run Engine tests were reported passing before a new lifecycle test hung; the Website Agent suite stalled after eight tests; API collection failed in four modules; platform typecheck was reported passing. Later code/setup may have changed these results.

### P0 — Verify website job recovery

1. Apply migration a09c68f54b21 to a disposable/test database, then validate the intended production migration procedure.
2. Verify a queued job survives Redis being down and is recovered when Redis returns.
3. Restart a worker during generation; prove the stale job is recovered, and an old token cannot overwrite a newer retry.
4. Verify retry limit, failure details, owner authorization, status display, and manual retry.
5. Confirm a customer sees a live URL only after Vercel deployment succeeds.
6. Add tests for concurrent recovery, duplicate enqueue, database/queue failures, and all state transitions.

### P0 — Verify one full customer journey

On a clean environment, exercise: account creation → business creation → Abija intake/clarification → saved business facts → brand generation → review/revision/approval → asset rendering/download → website queue/deployment → real status and URL. Include the intended payment/credit gate.

At each stage check persisted state, owner isolation, page refresh/relogin, duplicate requests, retries, and customer-visible failures.

### P1 — Complete operational product workflows

1. Build the admin review queue using existing review endpoints.
2. Complete and version the brand package contract and customer-facing render/download/revision flow.
3. Decide whether Run Engine autonomy is MVP. If yes, implement real task-specific capabilities; never display a generated draft as published or sent.
4. For external actions, add explicit scopes/permissions, approvals, idempotency, persisted outcomes, and recovery tests for interruption between action and state write.
5. Make credit charging idempotent and auditable, and confirm business authorization for billing/credit routes.

### P1 — Production readiness and deployment

1. Choose a current-provider launch or an AWS migration. AWS is only a target until deployment and smoke-test evidence exists.
2. Configure production PostgreSQL/Redis, storage, email, AI, payment and deployment credentials via managed secrets; remove development defaults and verify rotation.
3. Define database/asset backups and restore tests, migration rollback, queue monitoring/replay, alerts, support ownership, and incident handling.
4. Extend CI to frontend and all services; provide independent build/deploy, smoke test, and rollback steps.
5. Complete privacy/data retention/deletion, AI disclosure, terms, payment reconciliation, accessibility, rate/size limits, and security review.

### P2 — Deferred scope

WhatsApp intake, social OAuth/publishing/scheduling, analytics integrations, self-serve site editing/custom domains, paid acquisition automation, and generalized software/hardware work remain deferred until validated demand, implementation ownership, and support capacity exist.

## Open founder decisions

Keep unresolved decisions visible rather than silently choosing:

- Software platform, service studio, or product supported by studio?
- First customer group and geography?
- One-off package, subscription, credits, human-review add-on, or a mix?
- Human review scope, price, turnaround, and accountable reviewer?
- Which outputs require payment or approval before download/publication?
- AWS now or after MVP?
- Launch domain and approved public claims?
- Data retention/deletion, AI disclosure, privacy, and asset/IP policy?

## Local development notes

- Frontend workspace lives in **platform-web**. It uses Corepack/pnpm; local apps are marketing, customer platform, and admin. Root environment configuration should be copied from the example file and filled locally; never commit the real environment file.
- From **platform-web**, Docker Compose defines PostgreSQL, Redis, API, worker, and agent containers. The API startup command applies Alembic migrations before serving.
- API Python dependencies and developer tools are in **platform-web/api/pyproject.toml**. Run API commands from that directory.
- Each agent and Run Engine has its own **pyproject.toml**. Use its service directory and the required DB/Redis services for persistent-workflow checks.
- Local stub settings are for development only; they do not establish production readiness.

### Common commands

- Frontend setup: from **platform-web**, enable Corepack, activate pnpm 9.15.9, then run **pnpm install**. Start all apps with **pnpm dev**; check with **pnpm lint**, **pnpm typecheck**, **pnpm test**, and **pnpm build**. Node.js 20.9 or newer is required.
- Local services: from **platform-web**, run **make up** to start PostgreSQL, Redis, and agent containers; **make migrate** applies platform API migrations; **make dev** starts the API; **make worker** starts the ARQ worker. **make down** stops the Compose services.
- Python setup: from **platform-web/api**, create a Python 3.12 virtual environment and install the project with development extras. API checks are **python -m pytest**, **ruff check .**, and **pyright**.
- Agent checks: run each service's pytest from its directory with its source path configured. The root Makefile's test target covers the API, Branding Agent, and Website Agent; it does not currently include the Run Engine, so test that service separately.
- Local API docs are served at **http://localhost:8000/docs**. Local health endpoints and ports are declared in **platform-web/docker-compose.yml** and each service app.

No code, tests, builds, or runtime checks were performed during this documentation consolidation.

## How these two documents stay current

- This tracker owns implementation state, bugs, verification evidence, and next actions.
- The Blueprint owns durable product definition, requirements, architecture, roles, and research conclusions.
- Update this tracker alongside code when status or next action changes. “Implemented” means code exists; “Verified” requires evidence.
- Record the command, date, result, and revision for checks. Keep failures and skipped checks visible.
- Move durable decisions to the Blueprint and record rationale here.
- Do not create a duplicate project plan, sprint plan, engineer brief, or service README. Add durable information to one of these two files.

This tracker and the Blueprint replace the scattered project strategy, research, requirements, engineer briefs, implementation plans, roadmaps, sprint notes, duplicated platform plans, and service setup notes. Older example pricing, speculative schedules, unverified case studies, and dated provider claims were not retained as facts.

