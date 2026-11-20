# Cre8ive District — Project Execution Tracker

**Canonical record of implementation, gaps, verification, and next actions**

**Reviewed:** 20 November 2026

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
| CI/contracts | Root GitHub Actions workflows define frontend lint/typecheck/test/build and backend API/agent/Run Engine/migration/Compose/Docker checks. Versioned branding intake/strategy schemas exist. | PR #2 checks are running; GitHub rules and environments are unverified; frontend test scripts allow empty suites; release workflow has open safety defects listed below. |

Implementation map: **platform-web/apps/** (web), **platform-web/api/app/** (API), **platform-web/api/app/worker.py** (worker), **platform-web/services/** (agents and Run Engine), **platform-web/contracts/** (shared schemas), **platform-web/docker-compose.yml** (local stack). Local startup and diagnosis: **docs/LOCAL_DEVELOPMENT.md**. Deployment: **docs/DEPLOYMENT.md**.

## Next actions, in priority order

### P0 — Integrate the pushed feature branch

Live GitHub review on 20 November 2026:
- `main` is at `4ad2bbe` after merging Branding Agent [PR #1](https://github.com/Ayodeji90/cre8ive-district/pull/1).
- The remote feature branch was at `301efc2`, 10 commits ahead and 4 behind `main`. It is now integrated locally at `4fbd3d2` (11 commits ahead, 0 behind); the merge preserved the Branding Agent intake files and the feature branch's provider safeguards and tests.
- Draft [PR #2](https://github.com/Ayodeji90/cre8ive-district/pull/2) is open against `main` at `ba057be`. At review, Compose config passed, frontend checks were running, backend checks were queued/running, and both Vercel preview statuses were pending.
- Merged PR #1 reports a failed Vercel check for `app.cre8ivedistrict` and a successful check for `cre8ive_dist`; confirm the intended app deploy separately.
- The merge conflicts in `.gitignore` and six Branding Agent files (`Dockerfile`, `pyproject.toml`, API app, config, stub provider, and provider factory test) have been resolved and reviewed. The Docker build now includes the merged service README.

1. Review the complete feature diff for behavior that should be split or removed before merge.
2. Keep PR #2 in draft until the scope and CI failures are reviewed; then require frontend and backend CI gates and review every status check before merge.

### P0 — Make CI and release workflows safe to merge

The PR workflows now cover frontend and backend checks, all backend services, migration checks, Compose validation, and Docker build checks. This is implementation evidence only: GitHub has not run these workflows against the feature branch.

Close these code-level gaps before production deployment:
1. In `_deploy-ecs.yml`, add `preflight` as a direct dependency of the smoke job; it reads `needs.preflight.outputs.public_base_url`.
2. Remove the manual production path that can build an arbitrary ref and skip staging. Production must promote the same artifact that passed CI and staging.
3. Deploy by image digest or enforce immutable registry tags. The current workflow publishes `sha-<12>` tags and deploys by tag; the tag alone is mutable.
4. Pin third-party Actions to verified full commit SHAs and keep permissions scoped to the jobs that need them.
5. The frontend apps declare `vitest run --passWithNoTests`; add real tests and make missing expected suites fail CI. Verify all PR checks on GitHub after opening the PR.
6. Configure and verify the required CI gate checks and protected main settings. These repository settings are not proven by workflow YAML.

AWS ECS/Fargate remains a proposed host, not an approved immediate launch target. Keep provider-specific deployment disabled until the founder confirms AWS for this release and the required GitHub Environments, OIDC role, ECS services, networking, and GHCR pull access are configured.

### P0 — Close workspace continuity and data correctness

Backend work reported and code-reviewed:
- The Business credit migration and `alembic check` passed on disposable PostgreSQL according to the engineer report.
- Workspace state and chat resume routes, typed response models, ownership tests, and conversation-priority tests exist.
- Resume concurrency is still unsafe: `FOR UPDATE SKIP LOCKED` can fall through to create a second conversation. The added SQLite test is sequential, not a concurrent PostgreSQL test.

1. Serialize resume/start on the Business row or a transaction-scoped advisory lock. Add a real concurrent PostgreSQL test proving both requests return one conversation ID.
2. Record the final API test output and make the GitHub backend CI gate pass after branch integration.
3. Connect the frontend to the Business-keyed workspace-state and chat-resume contracts. The current workspace still calls `/api/chat/start`; no frontend consumer of the new routes was found.
4. Preserve the marketing idea through account creation into the first persisted conversation. The resume endpoint currently starts without an initial_idea field.
5. Keep Project-backed fields transitional. Do not present approval counts or project-run state as authoritative until their consistency and execution semantics are resolved.

### P0 — Verify the complete MVP customer journey

Run this on the integrated branch with stubbed external providers, then repeat against staging providers:
1. Marketing waitlist/idea → sign-in or account creation → same idea in Abija.
2. Create/select a Business → refresh/relogin → same Business and conversation resume.
3. Intake → persisted facts → brand generation → customer review/revision → asset delivery.
4. Website generation → quality/status reporting → real deployment URL only after successful deployment.
5. Exercise provider failure, retry, duplicate request, owner isolation, and mobile/keyboard paths.

Record the command, environment, commit SHA, result, and any failures. A green unit suite alone does not verify this cross-service journey.

### P1 — Prepare a controlled pilot and production release

1. Decide whether AWS ECS is the launch host or a later migration; update the deployment plan to match.
2. If AWS is selected now, complete staging infrastructure and GitHub Environment configuration, deploy the tested artifact, run health and customer-flow smoke checks, and verify rollback.
3. Configure production email, Google OAuth, AI, payment, object storage, and deployment providers; the latest frontend report showed missing/invalid Google and Resend credentials.
4. Complete rate limits, account recovery, data deletion/retention, privacy and AI disclosures, terms, payment reconciliation, backup/restore, monitoring, and support ownership.
5. Run a small customer pilot; measure completion, revision rate, deployment success, time-to-value, support load, and per-customer cost before expanding scope.

### P2 — Keep the north-star expansion staged

Admin review tooling, deeper brand-package delivery, autonomous external actions, social publishing, WhatsApp, analytics integrations, and self-serve domains remain subsequent work. Add external actions only with explicit approval, idempotent execution, persisted outcomes, and recovery.

## Open founder decisions

Keep unresolved decisions visible rather than silently choosing:

- First customer group and geography?
- One-off package, subscription, credits, human-review add-on, or a mix?
- Human review scope, price, turnaround, and accountable reviewer?
- Which outputs require payment or approval before download/publication?
- AWS ECS for the first MVP pilot or after it?
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
