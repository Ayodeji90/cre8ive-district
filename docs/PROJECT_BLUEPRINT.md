# Cre8ive District — Product Blueprint

**Canonical reference for product purpose, requirements, architecture, team, and research**

**Reviewed:** 19 November 2026

## Product direction

Cre8ive District is building an AI-powered brand launch platform for entrepreneurs and small businesses in Nigeria and across Africa. Early businesses often start through WhatsApp and social media without a clear brand identity, credible website, or practical launch materials. The platform aims to guide a customer from a business idea to a coherent, reviewable online presence.

A customer explains their business to **Abija**, an AI creative partner. Abija gathers and clarifies the brief, then helps create brand direction, identity concepts, website content, and launch materials. Customers can review, request changes, and approve outputs. Optional human designer review provides judgment where AI output benefits from it.

**Product promise to build toward:** Describe your business once. Get guided help turning it into a clear brand and credible online launch, with review before anything goes live.

The customer remains in control. The product must not imply generated work is fact-checked, legally cleared, deployed, or commercially successful until those things have actually happened.

The latest founder-provided platform description is the current product direction. Older research also describes a bespoke creative studio. Keep useful studio operating practices as context, but do not let that older direction silently redefine the software product.

The founder has confirmed the [Foundable End-to-End Architecture & Workflow Explorer](https://sites.google.com/view/foundableend-to-endarchitectur/full-page-embed?authuser=1) as a north star for where Cre8ive District should go. Build toward one coherent customer experience, a shared project state, coordinated Build and Run workflows, explicit approval for consequential actions, and a feedback loop that can propose useful next steps. The explorer is a product direction reference, not evidence of Foundable's production internals or a commitment to copy its pricing, credits, integrations, and every capability shown.

## Customers and problems

### Initial customer hypotheses

- Founders preparing to launch who need a clear brand and digital presence.
- Small or growing businesses whose identity, website, and social materials are inconsistent or incomplete.
- African and diaspora entrepreneurs who want an affordable guided workflow and remote creative support.

These are hypotheses. Interviews and early-user behavior must determine the first customer segment. “Nigeria and across Africa” is an intended market, not proof that every country, payment method, language, or regulatory need is supported.

### Problems to solve

- Convert an unstructured idea into a useful, fact-grounded business brief.
- Help customers make coherent brand decisions without coordinating disconnected tools and vendors.
- Create usable identity and website materials at an early-business budget.
- Show what is known, what is inferred, what AI suggested, and what needs approval.
- Deliver a functioning website and assets rather than presenting a preview as a completed deployment.

## Intended customer journey

1. Visitor understands the offer and can join the waitlist.
2. Customer creates an account and workspace.
3. Customer chats with Abija; conversation history and business details are saved, and Abija asks for missing information.
4. The platform generates brand direction and identity outputs from the brief.
5. Customer and, when selected, a human designer review and request revisions.
6. The platform generates and validates a brand-aligned website, deploys it, and reports real deployment state.
7. Customer receives approved assets and a record of what was delivered.

## MVP scope

| Area | MVP requirement |
|---|---|
| Identity and access | Secure sign-in; user-owned businesses, conversations, assets, and jobs; clear authorization at each API boundary. |
| Guided intake | Streaming chat, persistent history, structured business context, clarification, reconnect behavior, and safe handling of provider failures. |
| Brand creation | Strategy and messaging direction, palette, typography, logo concepts, website copy, structured package data, validation, and human/customer review. |
| Website generation | Multi-page site from business facts and brand inputs, quality checks, real deployment, saved deployment result, status, retry, and diagnostics. |
| Review and revisions | Persisted states, clear customer approvals, optional human review, and audit trail of changes. |
| Asset delivery | Render organized files and provide a reliable, access-controlled download or delivery path. |
| Billing | Payment initialization and verification, idempotent webhooks, auditable orders/credits, accurate balance, and clear customer-facing status. |
| Operations | Durable jobs, restart recovery, correlated logs, health/readiness, monitoring, backups, and support procedures. |

### Deferred until justified by evidence

WhatsApp intake; social account OAuth, publishing, scheduling, and analytics; self-serve custom domains and advanced site editing; broad CRM/marketplace integrations; autonomous posting, outreach, or spending; generalized AI consulting; custom software or hardware. Add these only after validating customer need, delivery ownership, privacy/security impact, and ongoing support.

### North-star product direction

- Present marketing discovery and the signed-in workspace as one Cre8ive District experience, with a clear handoff from a visitor's idea to Abija and no confusing brand or navigation break. The target may be one Next.js app with route groups; this is a product experience decision, not a requirement to share one runtime or deployment forever.
- Establish one canonical `ProjectState` for the customer's business brief, brand tokens and versions, site builds and deployment status, approvals, credits, and run progress. In the current schema, `Business` is the natural starting aggregate; evolve it rather than creating a parallel `projects` record without a distinct domain need. Represent state through related, versioned records and an API view rather than one oversized row.
- Make the Run Engine the end-to-end orchestrator for Build and Run workflows. Branding and website capabilities should read from and write through versioned contracts against canonical state. They may remain separate worker services during transition; their internal service boundaries must not create competing customer-visible state.
- Add sandbox preview, version history, and `*.cre8ivedistrict.app` publishing as the Build experience matures. Show a site as live only after deployment succeeds.
- Add approval cards for external actions, with clear scopes, recorded decisions, idempotent execution, and a reliable way to inspect or recover outcomes. Build an undo path for actions that can be safely reversed.
- Close the loop with consented business telemetry and evidence-based recommendations. Abija can propose the next action; execution still follows the configured approval and permission rules.

Treat this as a direction to reach in stages. Keep the MVP centered on the verified brand-to-website journey, and promote north-star capabilities into launch scope only when their implementation, operations, and customer value are validated. Do not import Foundable-specific pricing, credit allowances, Stripe behavior, or market claims as Cre8ive District decisions.

## Product quality requirements

- Ground outputs in customer facts; distinguish facts, extracted data, assumptions, and generated suggestions.
- Never invent company history, awards, customer numbers, guarantees, services, or locations.
- Require clear authorization and recorded approval for external publication, sending, spending, or destructive actions.
- Persist job/run state before enqueueing; handle duplicate delivery; recover after process restart; do not report success before durable completion.
- Keep “generated,” “needs review,” “queued,” “deployed,” and “delivered” as distinct states.
- Validate model output with schemas and deterministic quality checks; use bounded retries and human review where appropriate.
- Support keyboard access, readable contrast, mobile layouts, useful error states, and reduced motion.
- Track model, image, storage, hosting, payment, and support costs per completed customer workflow.
- Define consent, data retention/deletion, provider sharing, and asset/IP terms before public launch.

## Architecture

### Software delivery and release policy

Every change must enter through a pull request and pass required checks before merging to
`main`. CI validates frontend apps/packages, the Platform API, Branding Agent, Website Agent,
and Run Engine; it also validates database migrations and builds deployable artifacts. Pull
request checks use stubbed providers and disposable services, with no production secrets or
deployment permissions. Checks should run for every pull request so a path filter cannot leave a
required status check missing.

Merging to `main` may publish immutable, commit-addressed artifacts after CI succeeds. Staging
deploys automatically and runs health and workflow smoke checks. Production deploys only an
artifact already verified in staging, with an explicit release approval, database migration
gate, health checks, and a documented rollback target. The hosting provider and production
environment are not yet confirmed; GitHub Actions must not imply that image publication alone
deploys a service. Use least-privilege workflow permissions, pin third-party Actions to verified
full commit SHAs, keep fork PRs unprivileged, and use short-lived OIDC credentials if AWS is
selected. Repository branch protection and deployment environments are part of the release
control, not optional workflow comments.

### Foundation decision: canonical customer state

**Decision (19 November 2026):** `Business.id` remains the canonical customer-workspace
identity during the foundation phase. The existing chat, billing, brand, and website flows
already depend on `Business`; changing the identity before those paths are migrated would
split customer state and risk losing ownership and credit history. `ProjectState` is the
customer-facing aggregate/API view over that identity and its related versioned records, not
a second mutable copy of business profile, status, plan, or credit balance.

The new `Project` schema is therefore transitional scaffolding. Do not connect new frontend
flows to it or treat its copied fields as authoritative yet. Before adopting it as the physical
record, the backend owner must either migrate existing `Business` rows and every dependent
foreign key in one compatibility-safe sequence, or remove the duplicated mutable columns and
make `Project` a stable-identity wrapper whose profile and credits resolve through `Business`.
The selected migration path must preserve existing business IDs, ownership, orders, credit
ledger, brands, websites, conversations, and deployment history. No destructive migration is
approved by this decision.

`ProjectState` must compose the existing business profile and credits with versioned brand
kits, site builds, review/approval records, and execution state. The Run Engine remains the
single authority for orchestration runs, tasks, and events; API-facing run state must be a
projection or use a shared stable run ID, not a competing run lifecycle. Approval records may
record a decision, but the state must not imply that an external action executed until a
capability actually performed it and persisted its outcome.

The frontend may begin identity continuity using `business_id` once the backend publishes a
stable state endpoint and chat-resume contract. It must not depend on `/api/projects` until
those contracts and the migration path are settled. See the active verification and backend
actions in [PROJECT_EXECUTION.md](./PROJECT_EXECUTION.md).

### Current code structure

- **Web:** Next.js and TypeScript apps for marketing, customer workspace, and admin; shared UI, tokens, types, and typed API client.
- **Platform API:** Python/FastAPI, async SQLAlchemy, PostgreSQL, Alembic, JWT verification, REST, and WebSockets.
- **Jobs:** Redis and ARQ worker for brand generation, asset rendering, delivery, and website jobs.
- **Branding Agent:** separate Python service for structured intake/strategy, provider abstraction, validation, prompts, and asset rendering.
- **Website Agent:** separate Python service for site specification, AI copy, template rendering, quality checks, persistence, and Vercel deployment.
- **Run Engine:** separate Python service for agent runs, task state, approval controls, event streaming, and restart recovery.
- **Other integrations:** Paystack, object storage abstraction, email delivery, Vercel, and versioned JSON schemas for selected agent contracts.

### Target AWS direction

Founder-stated target: Amazon Bedrock for models; ECS/Fargate for API, workers, and agent containers; RDS for PostgreSQL; ElastiCache for Redis; S3 for generated assets; CloudFront for asset delivery.

This is a target, not a deployed architecture. Current code/configuration still uses provider seams and OpenRouter, Vercel, local Docker PostgreSQL/Redis, and S3-compatible storage configuration. Before AWS migration, document service mapping, secrets, networking, data movement, deployment/rollback, costs, and operations. Keep a provider-neutral seam only where it reduces real switching cost.

### Ownership boundaries

- Platform API owns customer accounts, businesses, authorization, billing, review state, and customer-visible job status.
- Branding Agent owns brand intake normalization and brand-generation operations, not accounts or billing.
- Website Agent owns site specification, rendering, quality, and deployment operations; the Platform API remains the customer-facing job-state source.
- Run Engine owns orchestration state; task capabilities must call authorized services and must not represent drafts as external actions.
- Shared contracts are versioned. Producer and consumer changes must remain compatible or be released together.

These boundaries describe the current implementation and its transition path. The north-star target is a unified customer-visible state and Run Engine orchestration across the journey, while specialized execution workers can remain separate where that keeps generation, rendering, or deployment reliable.

## People and role coverage

Role coverage is required; each row need not mean a separate full-time hire. Name an owner even when roles are combined.

| Role | Responsibility |
|---|---|
| Founder / Product lead | Customer discovery, priorities, scope, budget, acceptance, release approval. |
| Product designer / Brand UX | Intake, workspace interaction, brand quality, review flow, accessibility, customer-facing language. |
| Frontend engineer | Next.js apps, API integration, streaming/status UI, responsive behavior, auth handoff. |
| Backend engineer | API, database/migrations, authorization, billing/reviews, job reliability, service contracts. |
| AI/ML engineer | Model/provider setup, prompts, structured output, grounding, evaluation, safety, inference cost. |
| Platform/DevOps engineer | Containers, AWS or chosen host, CI/CD, secrets, networking, backups, alerting, recovery. |
| QA engineer | Test strategy, cross-service workflows, failure injection, browser regression, release evidence. |
| Creative reviewer / operations | Human review, revisions, asset acceptance, customer support, delivery. |

A lean MVP likely needs **4–6 people worth of responsibility coverage**, with some part-time or combined roles: founder/product, frontend, backend/platform, AI, design/review, and QA/operations. Confirm headcount against budget and existing skills. Older studio staffing estimates are not approved hiring commitments.

## Research conclusions and limits

Existing desk research suggests the category is crowded; “AI-powered,” “full service,” and “global” alone do not differentiate. The product must prove a useful guided workflow, truthful output, Nigerian/African context, accessible value, and optional human judgment.

The research supports starting with a narrow customer group, interviewing buyers about recent real behavior, testing the workflow with early users, and measuring completion, revision, deployment success, cost, time-to-value, and willingness to pay before broadening features or marketing channels.

Most research is desk research from public competitor pages, platform guidance, and dated third-party claims. It is directional, not representative. Earlier reports recorded no primary customer interviews. Competitor offers, prices, platform policies, provider features, and legal requirements can change; check them before making decisions or public claims.

## Open product decisions

Track these in the execution file until the founder decides:

1. Is the software platform the primary business, a studio service, or a product supported by a studio?
2. Which customer segment and geography are first?
3. Is the initial model a one-off brand package, subscription, credits, paid human review, or combination?
4. What does human review include, cost, and turnaround?
5. Which outputs are downloadable before payment or approval?
6. Is AWS the immediate launch target or a later migration?
7. Which domain and public product claims are approved?
8. What are the retention/deletion, AI disclosure, privacy, and asset/IP rules?

## Document ownership

This is the durable reference for product purpose, requirements, architecture, team coverage, and research conclusions. Keep transient bugs, sprint status, and test results in the execution tracker. Update this file when product scope, architecture, requirements, or ownership decisions change.

