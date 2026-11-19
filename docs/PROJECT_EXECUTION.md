# Cre8ive District — Project Execution Tracker

**Canonical record of implementation, gaps, verification, and next actions**

**Reviewed:** 19 November 2026

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

Implementation map: **platform-web/apps/** (web), **platform-web/api/app/** (API), **platform-web/api/app/worker.py** (worker), **platform-web/services/** (agents and Run Engine), **platform-web/contracts/** (shared schemas), **platform-web/docker-compose.yml** (local stack). Local startup and diagnosis: **docs/LOCAL_DEVELOPMENT.md**. Deployment: **docs/DEPLOYMENT.md**.

## Next actions, in priority order

### P0 — Git workflow and CI/CD foundation

**Target release flow:** feature branch → pull request → required CI → merge to `main` →
immutable artifact → staging deploy and smoke check → approved production deployment. A main
branch merge may publish an artifact; it does not itself authorize a production release.

**Current workflow audit:** root `.github/workflows/ci-backend.yml` is the single backend
required workflow. It runs on every pull request and `merge_group` (no path filters, so the
required status always reports) and covers API lint/tests, Alembic migrations (empty database,
idempotent upgrade, `alembic check`), Branding Agent, Website Agent, Run Engine, Docker Compose
validation, and Docker builds for all four images. It needs no repository secrets and finishes
in an aggregate `CI gate` job. `ci-frontend.yml` mirrors that shape with its own `CI gate`. The
stale nested `platform-web/.github/workflows/backend-ci.yml` has been removed.
`deploy-backend.yml` is gated on a successful `CI · Backend` run on `main`, skips when the
commit contains no backend changes, publishes immutable `sha-*` images, and promotes them
through the reusable ECS workflow. Remaining gaps are repository configuration, not workflow
code: branch protection, GitHub Environments, AWS resources, and SHA-pinning of third-party
actions.

**Pipeline design:**

1. For every pull request to `main`, run a stable required CI workflow: frontend lint,
   typecheck, real unit tests, and production builds for marketing, platform, admin, and shared
   packages; API/agent/Run Engine lint, typecheck where configured, tests, and migration checks
   on disposable PostgreSQL; and Docker build checks for every deployable service. Use stubbed
   AI/email/payment/deploy providers. Keep these checks credential-free.
2. Add a required aggregate status job that reports failure if any required lane fails. Avoid
   top-level path filters on required workflows; if later optimizing monorepo execution, use
   change detection inside the workflow and make skipped components report success explicitly.
   Include `merge_group` if GitHub merge queue is enabled.
3. On pull requests, generate Vercel preview deployments for the maintained frontend apps and
   run smoke checks against those previews. The frontend engineer owns app build/preview
   configuration; hosting credentials and project setup must be GitHub/Vercel environment
   secrets, never repository files. Keep production secrets unavailable to PR jobs.
4. After merge to `main`, publish each backend service image only after all required CI
   jobs pass. Tag images with the commit SHA and deploy by immutable digest; do not use `latest`
   as a deployment input. This is implemented: `deploy-backend.yml` runs on `workflow_run`
   completion of `CI · Backend`, refuses failed runs, and pushes `sha-<12>` images.
5. The hosting target is AWS ECS/Fargate. `_deploy-ecs.yml` deploys automatically to staging,
   runs `alembic upgrade head` as a one-off task against the new image before touching any
   service, deploys agents then API, and smoke-tests `/health`, `/health/db`, and
   `/health/deps`. Production is a separate call gated by the `production` GitHub Environment's
   required reviewers; it promotes the exact same image tag. Rollback restores the pre-deploy
   task definition ARNs automatically on failure and is available manually through
   `rollback-backend.yml`. AWS access uses GitHub OIDC, never long-lived keys. Full runbook:
   `docs/DEPLOYMENT.md`.
6. Protect `main`: pull requests required, no force-push or deletion, at least one review,
   required unique CI status checks, conversation resolution, and no bypass for routine
   contributors. Pin third-party Actions to verified full commit SHAs; set minimum workflow
   permissions and add Dependabot for Actions and language dependencies.

**Final frontend engineer deliverable before handoff:** own the frontend CI lane and deployment
readiness: test the auth/idea handoff and mobile menu/switcher behavior with deterministic
provider stubs; add real tests for redirect safety, idea preservation/length limits, and
keyboard/focus behavior; ensure test commands fail when the expected test suite is absent;
make lint, typecheck, tests, and production builds pass for marketing, platform, admin, and
shared packages in GitHub Actions; configure and verify PR preview builds for the currently
maintained frontend apps; document required GitHub status checks, Vercel project/build settings,
and preview smoke steps. The frontend engineer does not own backend service deployment or
production cloud credentials.

**Backend/DevOps follow-up:** the workflow code is in place (CI coverage for every service,
migration checks, immutable publication gated on CI, ECS staging/production promotion,
approval gates, smoke checks, rollback, and a local `make doctor` diagnostic). Still requires
repository/cloud configuration before it is production-ready: create the `staging` and
`production` GitHub Environments with variables from `docs/DEPLOYMENT.md`, require reviewers on
production, add `CI gate` as a required branch-protection check, create the ECS clusters and
services, configure the AWS OIDC role, and decide GHCR pull credentials. Do not declare CI/CD
production-ready until those are verified in a real staging run.

### P0 — Foundation gate: canonical customer state

**Decision recorded in the Blueprint:** preserve `Business.id` as the canonical workspace
identity for now. Treat `ProjectState` as an aggregate/API view. The new `Project` table is
transitional and its copied profile, lifecycle, plan, and credit fields are not authoritative.

Current code evidence: chat and billing use `Business`; existing brands and websites reference
it. `project_bridge.py` copies a subset of business fields and copies `credit_balance` only at
creation. Its sync helper has no caller in the API code found during this review. The projects
API also accepts independent project creation and updates, so those paths can create divergent
state. The project runs table is distinct from the Run Engine's persisted run/task/event state.
The approval decision endpoint records `approved` and `executed_at`, but does not execute an
external action. These project endpoints and tables are not a production-ready unified state
contract.

1. Backend: inventory every foreign key and customer workflow that currently uses
   `Business.id`; retain it as the stable ID through any future migration.
2. Backend: choose and document the physical migration path: evolve `Business`, or make
   `Project` a wrapper without duplicate mutable profile/billing state. Do not dual-write
   mutable fields without a tested conflict policy.
3. Backend: publish one authenticated state endpoint keyed by `business_id`, plus a chat
   resume/start contract that carries that same ID and returns the persisted conversation.
4. Backend/Run Engine: designate the Run Engine run/task/event records as the orchestration
   source of truth; expose them through an API projection or shared run IDs. Approval decisions
   must not be reported as executed until the approved capability completes and persists its
   result.
5. Backend: fix the current database/schema mismatch reported by the frontend verification
   (`GET /api/businesses` selects `businesses.credit_balance`, absent from the connected local
   database). Repository audit found `credit_balance` in the Business ORM but no migration adding
   it to `businesses`; the unified project migration adds that field only to `projects`. Reproduce
   this on disposable Postgres, check current balances against the credit ledger, then add and
   verify a data-preserving Business migration. Do not apply migrations to an unknown/shared DB.
6. Frontend: keep using the existing Business API and do not consume `/api/projects` until the
   state and resume contracts are published and verified.

**Gate to pass before frontend ProjectState wiring:** existing customer IDs and credit history
remain intact; clean and upgraded disposable-database migrations pass; business list/get and
credit balance work against the migrated schema; owner isolation is verified; chat resumes the
same business/conversation after refresh and sign-in; run and approval status accurately reflect
execution; response contracts are typed and exercised end to end.

**Backend Engineer review resolutions (19 November 2026):**
- **Alembic check & schema drift:** Harmonized unique index vs unique constraint on `projects.business_id`. Verified clean DB upgrade (`upgrade head`) and upgrade from existing DB revisions (`f5b8c4d1e234` -> `g6c9d5e2f345`) on disposable PostgreSQL. `alembic check` output: `No new upgrade operations detected.`
- **Safe downgrade & recovery:** Protected `g6c9d5e2f345` downgrade with explicit `RuntimeError` requiring `ALLOW_CREDIT_DOWNGRADE=1` and documenting manual backup/restore steps to safeguard customer payment & credit records.
- **Conversation priority selection:** Updated `workspace.py` to sort with explicit SQL `case()` status priority: `active > idle > closed`, verified via persistent tests.
- **Typed contract & persistent tests:** Created Pydantic `ChatResumeResponse` schema and 12 tests in `tests/test_workspace_chat.py`. The engineer reports 57/57 API tests passing; retain the final CI/run output as evidence.
- **Concurrency protection remains open:** The current `SKIP LOCKED` query returns no row when another request holds the existing conversation lock, then proceeds to create another conversation. When there is no conversation row yet, neither request has a row to lock. The new “concurrent” test is sequential and uses SQLite, so it does not verify concurrent PostgreSQL behavior. Serialize on the existing Business row (or use a transaction-scoped advisory lock keyed by `business_id`) and add a real concurrent PostgreSQL test that proves both requests return the same conversation ID.

**Where the two engineers start:**

- **Backend Engineer — data and API:** migration and schema drift work has been reported as
  verified on disposable Postgres. Close the remaining resume-concurrency issue above, then
  record the passing test run. Keep Business IDs stable, and keep the transitional Project table
  out of frontend flows until the frontend consumes and verifies the Business-keyed state and
  chat-resume contracts.
- **Platform Engineer — delivery and runtime:** first make the GitHub checks reliable and
  credential-free: required PR checks for all services including Run Engine, migration smoke
  checks, least-privilege permissions, and artifact publication gated on successful CI. In
  parallel, make Docker Compose readiness observable for API, PostgreSQL, Redis, Branding Agent,
  Website Agent, and Run Engine so the API/chat smoke path is reproducible. Add staging and
  production deploys only after the hosting target is confirmed.
- **Joint interface:** agree on migration invocation, readiness/health endpoints, image names,
  environment variables, and the stubbed end-to-end smoke command. The Backend Engineer owns
  schema/API correctness; the Platform Engineer owns workflow, runtime, deployment, and rollback
  mechanics. Review the API contract and CI gate together before connecting the frontend.

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

The frontend route inventory, the marketing → sign-in → workspace handoff contract, and the
frontend API contract inventory are recorded in [FRONTEND_ARCHITECTURE.md](./FRONTEND_ARCHITECTURE.md).

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
- From **platform-web**, Docker Compose defines PostgreSQL, Redis, API, worker, the agents, and Run Engine. A one-shot `migrate` service applies Alembic migrations and must succeed before the API and worker start.
- API Python dependencies and developer tools are in **platform-web/api/pyproject.toml**. Run API commands from that directory.
- Each agent and Run Engine has its own **pyproject.toml**. Use its service directory and the required DB/Redis services for persistent-workflow checks.
- Local stub settings are for development only; they do not establish production readiness.

### Common commands

- Frontend setup: from **platform-web**, enable Corepack, activate pnpm 9.15.9, then run **pnpm install**. Start all apps with **pnpm dev**; check with **pnpm lint**, **pnpm typecheck**, **pnpm test**, and **pnpm build**. Node.js 20.9 or newer is required.
- Local services: from **platform-web**, run **make up** to build and start the full stack (PostgreSQL, Redis, migrations, API, worker, Branding Agent, Website Agent, Run Engine); **make status** and **make doctor** show readiness and dependency failures. **make down** stops the Compose services. See [LOCAL_DEVELOPMENT.md](./LOCAL_DEVELOPMENT.md) for host-side alternatives.
- Python setup: from **platform-web/api**, create a Python 3.12 virtual environment and install the project with development extras. API checks are **python -m pytest**, **ruff check .**, and **pyright**.
- Agent checks: run each service's pytest from its directory with its source path configured. The root Makefile's **make test** and **make lint** cover the API, Branding Agent, Website Agent, and Run Engine.
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

