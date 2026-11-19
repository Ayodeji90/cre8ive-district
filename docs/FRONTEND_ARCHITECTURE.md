# Frontend architecture and contract map

**Status:** Sprint 1 working document. The route map, journey and API inventory describe the
code as it stands after sprint 1 on `feat/platform-waitlist-vercel`, including the workspace
truthful-state changes; §2.2 records which consolidation phase has actually shipped. Product requirements stay in [MVP_REQUIREMENTS.md](./MVP_REQUIREMENTS.md),
scope and status stay in [PROJECT_EXECUTION.md](./PROJECT_EXECUTION.md), and the canonical
record decision is recorded in [PROJECT_BLUEPRINT.md](./PROJECT_BLUEPRINT.md).

**Why this file exists:** the frontend now spans three Next.js apps and two packages that
each declare their own API types. This document is the single place that records the route
inventory, how the public site hands a customer to the workspace, which backend contract each
screen actually consumes, and the order in which the apps can safely become one.

---

## 1. Customer journey and route map

### 1.1 Routes now

| App | Port | Route | Access | Notes |
| --- | --- | --- | --- | --- |
| marketing | 3000 | `/` | public | Marketing page + waitlist form. Header links to platform `/sign-in` (desktop and mobile); a successful waitlist submit with a description offers `/sign-in?idea=<description>`. |
| marketing | 3000 | `/api/waitlist` (POST) | public | Same-origin proxy; forwards `name`, `email`, `business_description` to the API. |
| marketing | 3000 | `/opengraph-image` | public | Generated OG image. |
| platform | 3001 | `/` | public | Compatibility entry. Signed-in → `/workspace?idea=…`; anonymous → `/sign-in?next=/workspace&idea=…`. Old links and magic links keep working. |
| platform | 3001 | `/workspace` | session | The workspace (`(workspace)` route group; layout owns the full-screen shell). Reads `?idea=` to seed the first conversation; without a session redirects to `/sign-in?next=/workspace&idea=…`. |
| platform | 3001 | `/sign-in` | public | `(auth)` group. Reads `idea`/`next`; authenticated visitors redirect to the resolved destination (default `/workspace`). Passes a sanitised `callbackUrl` to `AuthForm` and a switch link that carries the same params. |
| platform | 3001 | `/sign-up` | public | Same behaviour as `/sign-in`. |
| platform | 3001 | `/welcome` | session | `(auth)` group. New-account landing from Auth.js. Forwards `callbackUrl`/`idea` to the resolved destination (default `/workspace`) instead of redirecting to a bare `/`. |
| platform | 3001 | `/api/auth/[...nextauth]` | public | Auth.js handlers (Resend magic link + Google). |
| admin | 3002 | `/` | public (scaffold) | Internal review/ops shell; no auth or data yet. Deliberately not part of the customer app. |

### 1.2 Journey now

```
marketing /  ──waitlist POST──▶  /api/waitlist  ──▶  waitlist table
     ├─ header "Sign in" ──────────────────────────▶  platform /sign-in
     └─ waitlist success ──▶  platform /sign-in?idea=<description>

platform /  ──session──▶  /workspace?idea=…
platform /  ──no session──▶  /sign-in?next=/workspace&idea=…
platform /sign-in?idea=…  ──magic link / Google──▶  /workspace?idea=…   (sanitised callbackUrl)
                          └─ brand-new account ──▶  /welcome?callbackUrl=…&idea=…  ──▶  /workspace?idea=…
platform /workspace  ──mount──▶  new conversation, seeded with `idea` + (optional) new business
```

What that fixes: a visitor who describes their business can enter the platform from the
waitlist confirmation or the header, and the text they wrote arrives as `idea` through every
auth hop instead of being dropped.

What is still true (unchanged by sprint 1):

- The workspace starts a **new** conversation on every mount. There is no resume path and no
  project identity, so "the same project in the workspace" is not true yet. A `Business` is
  only created when the customer explicitly names one; the project bridge creates the
  `Project` from that `Business`, so a returning visitor does not necessarily return to the
  same record.
- `idea` is input to the first message, not an identifier: it is not persisted by the auth
  flow, and a reload of `/workspace?idea=…` only seeds the (already-started) conversation once.
- The waitlist row is still not migrated into the workspace. The description reaches Abija
  only when the customer takes the deep link from the success state; an invite-only signup
  still has no server-side bridge to `business_description` (see §6).

### 1.3 Intended journey

```
marketing /  ──"Start with Abija" / waitlist success──▶
  platform /sign-in?idea=<brief>&next=/workspace  ──magic link / Google──▶
  platform /workspace?idea=<brief>  ──▶  workspace seeded with the brief
       └─ customer creates/selects a business → Project bridge → same project next visit
```

Handoff contract (frontend-owned, backend-neutral):

| Param | Where | Rules |
| --- | --- | --- |
| `idea` | marketing CTA → `/sign-in`, `/sign-up`, `/welcome`, `/workspace` | One URL-encoded string, trimmed, max 2 000 characters. Never required; an empty value is omitted. It is *input to the first conversation*, not an identifier. |
| `next` | auth pages | Same-origin absolute path only (`/` or `/...`, not `//host`). Anything else falls back to `/`; the auth pages then use `/workspace` as the default destination. `idea` is appended to `next` when `next` does not already carry one. |
| `callbackUrl` | Auth.js internal, `/welcome` | Reduced to a path on this app by `toSafePath`; a host in the value is discarded, so it cannot act as an open redirect. |

Auth pages now compute the post-auth destination once
(`apps/platform/lib/auth-redirect.ts`) and pass it to `AuthForm`. The email magic link and the
Google button both use that value, so the returned session lands on the workspace with the
idea intact. `/welcome` forwards the same params for brand-new accounts instead of redirecting
to a bare `/`.

**Still missing (blocked on the backend decision):** resolving "the idea I typed" to the same
`Project` on the next visit. That needs the canonical record plus a stable identifier the
frontend can carry (project id or business id) — see §3.4.

### 1.4 Access and error routes

| Situation | Behaviour now |
| --- | --- |
| Unauthenticated `/` | redirect to `/sign-in?next=/workspace&idea=…` (idea preserved) |
| Unauthenticated `/workspace` | redirect to `/sign-in?next=/workspace&idea=…` |
| Authenticated `/` | redirect to `/workspace?idea=…` |
| Authenticated `/sign-in` or `/sign-up` | redirect to the resolved `next`, defaulting to `/workspace`; idea appended |
| Unsafe `next` / `callbackUrl` (`//host`, absolute URL, protocol-relative) | reduced to a same-origin path; a rejected value falls back to `/` and then to the `/workspace` default; the idea is still appended |
| No business yet | workspace offers creation |
| Businesses/credits/website-status load failure | visible alert banner with **Try again**, which re-runs the fetches |
| Website status polling failure | inline status error line; polling keeps trying |
| Unknown workspace URL | 404 |

---

## 2. Proposed customer-app consolidation

### 2.1 Target shape

One customer-facing Next.js app (`apps/web`), route groups inside one deployment. Admin stays
a separate app because its audience, auth posture and release cadence differ.

```
apps/web/app
├── (marketing)/
│   ├── page.tsx                 # /
│   ├── pricing/, about/, blog/  # only once those pages exist
│   └── layout.tsx               # marketing chrome + metadata
├── (auth)/
│   ├── sign-in/, sign-up/, welcome/
│   └── layout.tsx               # centred auth shell
├── (workspace)/
│   ├── layout.tsx               # session guard + AppShell
│   └── workspace/page.tsx       # former platform /
├── api/auth/[...nextauth]/route.ts
├── api/waitlist/route.ts
└── opengraph-image.tsx
```

Phase 1 already created the `(auth)` and `(workspace)` groups inside `apps/platform`, with the
URLs above unchanged for auth; `(marketing)` and the final `apps/web` rename remain phases 2–4.
The workspace layout currently owns only the full-screen shell — the session check stays in the
page so a failed auth lookup produces a redirect, not a broken shell.

Decisions to make explicit before moving files:

- **`/` stays marketing.** The workspace moves to `/workspace`; `/` redirects to `/workspace`
  only for an active session via middleware, never for anonymous visitors.
- **One auth origin.** Auth.js cookies are host-scoped today. Moving the workspace under the
  marketing host means every emailed magic link and every `AUTH_URL` must be reissued against
  the new host; keep the old platform host answering `/api/auth/*` (proxy) until the last
  outstanding link expires (24 h) after cutover.
- **Deep links.** Existing links to `platform.cre8ivedistrict.com/*` get a permanent redirect
  to the corresponding web route, preserving `idea`/`next` query params.
- **No data-layer change in this step.** The move is a routing and deployment change only;
  API URLs, `ApiSessionBridge`, and the WebSocket hook are untouched.

### 2.2 Phases, each independently shippable

| Phase | Change | Gate before starting | Rollback |
| --- | --- | --- | --- |
| 0 (this sprint) | Shared types single-sourced; idea/next handoff contract implemented in the current platform app; marketing links to sign-in. | none | revert commits |
| 1 (done) | Route groups and the auth layout are in the platform app: `sign-in`/`sign-up`/`welcome` sit in `(auth)` with a shared centred shell (URLs unchanged); `/workspace` renders the current workspace in `(workspace)`; `/` redirects sessions to `/workspace` and anonymous visitors to sign-in with `next=/workspace`. Deep links keep `idea`; unsafe `next`/`callbackUrl` still collapse. | handoff verified on preview — done locally, see §5 | route revert, URLs unchanged |
| 2 | Copy marketing pages into `(marketing)` and the waitlist route into the web app; deploy a second Vercel project from the same repo. | marketing content frozen; waitlist table unaffected | keep the old marketing project serving |
| 3 | Point the apex domain at the web project; add host redirects from the old platform project; set `AUTH_URL` and `NEXT_PUBLIC_*` to the new host. | one full release on phase 2 + magic-link smoke test | DNS back to the previous project |
| 4 | Delete the old marketing/platform Vercel projects and the duplicate app directories; keep `apps/admin`. | one week with no rollback | git revert + redeploy previous build |

Not in scope for consolidation: splitting `abija-workspace.tsx`. That decomposition should
follow the canonical-record decision, one responsibility per PR (business selection, credits,
website lifecycle, chat), each behind unchanged props so the customer flow is never in flight.

### 2.3 Deployment and environment plan

| Concern | Today | Target |
| --- | --- | --- |
| Vercel projects | marketing, platform, admin | web, admin (marketing retired) |
| Build command | per app via turbo | `pnpm turbo build --filter=@cre8ive/web` |
| Public URL vars | `NEXT_PUBLIC_MARKETING_URL`, `NEXT_PUBLIC_PLATFORM_URL`, `NEXT_PUBLIC_API_URL` | single `NEXT_PUBLIC_APP_URL`; keep the old two during phase 2/3 for redirect origin |
| Auth | `AUTH_URL=http://localhost:3001`, `JWT_SECRET`, `AUTH_SECRET` | `AUTH_URL=https://cre8ivedistrict.com` |
| API origin | `NEXT_PUBLIC_API_URL` / `API_INTERNAL_URL` | unchanged |
| Root env loading | each app calls `loadEnvConfig` on the repo root | unchanged |
| Redirects | none | host-level `/sign-in`, `/sign-up`, `/welcome`, `/` → web equivalents |

Checks required on the phase 3 preview before the domain moves: magic-link round trip from a
cold inbox, Google round trip, `idea` survives both, `/workspace` loads for a returning
account, waitlist POST still writes, OG image and canonical URLs resolve on the new host.

---

## 3. Frontend API contract inventory

All frontend traffic goes through `packages/api-client`. Auth is a bearer token supplied by
`ApiSessionBridge` (`session.accessToken`), so every call below is authenticated unless noted.
`businessId`/`projectId` in paths is a UUID string.

### 3.1 Modules actually used by screens

| Module | Call | Backend route | Response type | Used by | Contract state |
| --- | --- | --- | --- | --- | --- |
| `businessesApi` | `list()` | `GET /api/businesses` | `Business[]` | workspace | wire shape, now single-sourced |
| `businessesApi` | `create()` | `POST /api/businesses` | `Business` | workspace | matches `BusinessCreate` (`extra="forbid"`) |
| `businessesApi` | `get()`, `update()` | `GET/PATCH /api/businesses/{id}` | `Business` | none | typed, untested in UI |
| `billingApi` | `credits(businessId)` | `GET /api/billing/{id}/credits` | `CreditBalanceResponse` (`balance`) | workspace | used; a failure surfaces in the workspace banner (§4) |
| `billingApi` | `topupCredits()` → `initialize` | `POST /api/billing/initialize` | `BillingInitializeResponse` | top-up modal | used, Paystack redirect |
| `billingApi` | `verify()`, `history()`, `ledger()`, `deductCredits()` | `/api/billing/*` | `Order`, credit ledger types | none | unexercised; ledger shape unverified |
| `websitesApi` | `generateAndDeploy()` | `POST /api/websites/generate-and-deploy` | `GenerateWebsiteResponse` | workspace | **response body declared locally, not verified against `website_gen.queue_website_generation`** |
| `websitesApi` | `retry()` | `POST /api/websites/{id}/retry` | same | workspace | 404/409 semantics match UI copy |
| `websitesApi` | `getStatus()` | `GET /api/websites/{id}/status` | `WebsiteStatusResponse` | workspace polling | matches `WebsiteStatusResponse` |
| `chatApi` | `start()` | `POST /api/chat/start` | `StartChatResponse` | chat hook | `initial_idea` + `business_id` accepted |
| `chatApi` | `history()` | `GET /api/chat/{id}/history` | `ChatHistoryResponse` | chat hook (resume path) | `context` is `Record<string, unknown>`; hook casts it |
| WebSocket | `/api/chat/{conversationId}?token=` | chat socket | ad-hoc events | chat hook | not in the client package; payload types are hand-declared |

### 3.2 Modules with no consumer

| Module | Calls | Problem |
| --- | --- | --- |
| `brandsApi` | `GET /api/brands/{id}`, `.../preview` | Typed with the shared **camelCase** `Brand` (`businessId`, `logoUrls`, `fonts`, `strategy`). The API returns `BrandResponse` in **snake_case** with `logo_urls`, `colors`, `fonts`, `copy`, `guidelines_pdf`, `kit_zip_url`. Any screen built on this type would read `undefined` at runtime. |
| `adminApi` | `/api/admin/reviews*`, `/api/admin/businesses*` | Same camelCase/snake_case mismatch for `Review` and `Business`; review list returns `ReviewListItem`, detail returns `ReviewDetail` with nested `brand`/`business`/`order`/`website`. Admin app does not call it yet. |

### 3.3 Duplicate and divergent types

| Resource | Where declared | Divergence |
| --- | --- | --- |
| `Business` | `packages/types/src/business.ts` **and** `packages/api-client/src/businesses.ts` | Two shapes: camelCase product shape (`targetAudience`, `websiteUrl`, `createdAt`) vs wire `BusinessResponse`. **Fixed in this sprint:** one definition in `@cre8ive/types`, matching the API, re-exported by the client. |
| `Brand` | `packages/types/src/brand.ts` only | camelCase, no wire equivalent; `BrandStatus` is a guessed union. Needs a real adapter or a backend-shaped type. |
| `Order` | `packages/types/src/order.ts` | camelCase, API is snake_case with `paystack_ref`, `deliverables`. |
| `Review` | `packages/types/src/review.ts` | Single flat shape; API has three (`ReviewResponse`, `ReviewListItem`, `ReviewDetail`). |
| `Conversation`, `User` | `packages/types/src` | No matching backend schema consumed by the frontend today. |
| Chat `context` | `chatApi` + `ExtractedBrandContext` in the hook | Unvalidated cast from `Record<string, unknown>`; a backend field rename silently breaks the preview pane. |

### 3.4 Project contract — do not wire yet

The backend now exposes `app/schemas/project.py` (`ProjectResponse` with brand kit, site build,
approval items, agent runs, run events) plus `GET/POST /api/projects`, and
`app/services/project_bridge.py` creates a project from a business. **No frontend module or
screen consumes it**, and `chatApi.start` still takes `business_id`, not `project_id`.

Foundation decision: `Business.id` remains the canonical workspace identity and `ProjectState`
is an aggregate/API view. The schema migration path and stable state/chat-resume contracts are
still open, so no new screen connects to `ProjectState` or `/api/projects` yet. The backend
must publish (a) a state response keyed by `business_id`, (b) persisted chat resume behavior,
and (c) a documented migration path before frontend integration. Until then:

- keep the workspace on `Business` + conversation,
- treat `Project` as an internal backend detail,
- do not add a `projectsApi` module against an unsettled shape.

### 3.5 Contract rules going forward

1. One definition per API resource, in `@cre8ive/types`, written in the **wire** shape the API
   serialises. Components may map to a view model locally but must not redeclare the resource.
2. `api-client` only adds request/response helpers and imports those types; it must not declare
   a second copy.
3. Any response that has not been exercised against a running API is marked `// unverified` in
   the client until it is.
4. No casts from `Record<string, unknown>` into a hand-written interface; parse or narrow.
5. A new backend route is not "available to the frontend" until its response model is published
   and typed here.

---

## 4. Truthful states audit

Status of the findings recorded before sprint 1, plus what is still open.

| Surface | Finding | Status |
| --- | --- | --- |
| Workspace business list | `businessesApi.list().catch(() => {})` left an empty switcher with no explanation. | **Fixed.** `loadError` sets an alert banner with **Try again**; retry bumps `reloadKey` and refetches. |
| Workspace credits | `billingApi.credits(...).catch(() => {})` left the balance at `—` forever. | **Fixed.** Same banner; the `—` value is now explained by the failure message. |
| Website status | `websitesApi.getStatus(...).catch(() => {})` and polling failures were silent; the pane could claim "Drafting in Chat" while the API was down. | **Fixed.** Load failure uses the banner; a polling failure sets the inline `websiteError` line and polling continues. |
| Agent pill | Always read "Abija Agent Active", even while the socket was reconnecting or closed. | **Fixed.** Text, colour and dot derive from `isConnected`: "Abija connected" / "Abija reconnecting", with a matching `title`. |
| Business switcher a11y | Trigger did not expose its state; the click-away overlay was exposed to assistive tech. | **Fixed.** `aria-haspopup`, `aria-expanded`, `aria-controls`; overlay is `aria-hidden`. |
| Preview pane | "Website Deployed & Live ✓" is driven by `status === "deployed"`, which is truthful; "Autonomous Run Engine … outreach, competitor scan & marketing loop" is not backed by a shipped capability. | Open — flagged, not changed this sprint. |
| Typography | Preview pane hardcodes "Plus Jakarta Sans" instead of the brand's chosen fonts. | Open — belongs to the brand contract work. |
| Connection pill on mobile | The pill used `hidden sm:inline-flex`, so phone-sized viewports showed no connection state at all. | **Fixed.** Always rendered; the label is visually hidden below `sm` and announced via `role="status"` + `aria-label`, leaving the status dot visible at 390 px without header overflow. |
| Business switcher keyboard | Enter/Space opened the menu, but Escape did not close it, including with focus inside the menu. | **Fixed.** Escape closes from the trigger or any menu item and returns focus to the trigger; focus outline remains visible. |
| Mobile | Workspace is desktop-first with a mobile tab switch; dropdown, banner and top-up dialogs need a mobile/keyboard pass. | Partly open — at 390×844 the banner, retry button, header and switcher were verified (no horizontal overflow, retry reachable in the viewport); the top-up dialog still needs the same pass. |
| Low bandwidth | No request timeouts in `ApiClient`; a stalled fetch leaves a perpetual loading state. | Open — needs backend/contract work, listed as follow-up. |

---

## 5. What changed in sprint 1

Code:

- `apps/platform/lib/auth-redirect.ts` — safe `next`/`idea` resolution; post-auth default is
  now `/workspace`, so an auth round trip no longer relies on a redirect through `/`.
- `apps/platform/lib/root-env.ts` — loads the repo-root `.env` with `forceReload` before the
  Auth.js secret is read. Without it the dev server had no `JWT_SECRET`, so every callback and
  email send failed with `Configuration`.
- Route groups in `apps/platform`: `(auth)` (`sign-in`, `sign-up`, `welcome` + shared shell),
  `(workspace)` (`/workspace` + full-screen layout). `/` is now a redirect entry point.
- `sign-in`, `sign-up`, `welcome`, `/workspace` and `/` accept and preserve `idea` + `next`.
- `AuthForm` takes `callbackUrl` and a param-preserving switch link; magic link and Google both
  return to the workspace with the idea.
- Marketing header gains a "Sign in" link to the platform; the waitlist success state offers
  "Start your workspace with this idea" when a business description was submitted.
- `Business` is declared once in `@cre8ive/types` in the API's wire shape; `api-client`
  re-exports it.
- Workspace load failures (businesses, credits, website status/polling) are visible with retry;
  the agent pill reflects the live socket state.

Verification (local stack: Postgres + Redis, API on `:8000`, marketing `:3000`, platform `:3001`):

- Marketing header → `http://localhost:3001/sign-in`; waitlist success → `/sign-in?idea=<description>`.
- With a real verification token inserted for a test user, the Auth.js callback landed on
  `/workspace?idea=…` and rendered the workspace.
- The magic-link POST carried `callbackUrl=%2Fworkspace%3Fidea%3D…`; with
  `?idea=Safe&next=//evil.example/phish` the unsafe `next` was dropped and the idea survived.
- Signed-in `/`, `/sign-in`, `/welcome`, `/workspace` all end on `/workspace` with the idea;
  anonymous `/` and `/workspace` redirect to `/sign-in?next=/workspace&idea=…`.
- Workspace at 390×844: alert banner visible, **Try again** inside the viewport, no horizontal
  overflow, status dot visible; at 1280 the pill reads "Abija reconnecting" against the failing
  businesses request.
- Keyboard: Tab reaches the switcher, Enter/Space open it, Escape closes it from the trigger and
  from a menu item, returning focus to the trigger.
- `pnpm turbo typecheck --filter=@cre8ive/platform` passes; ESLint passes on every touched file
  (the repo-wide `pnpm lint` still fails on a pre-existing unescaped apostrophe in
  `topup-modal.tsx`).

Could not verify locally: Google completes only up to the consent redirect (no
`GOOGLE_CLIENT_ID` in the root env, so Google returns "Missing required parameter: client_id");
the magic-link **email** is not delivered (`RESEND_API_KEY` returns 401), so delivery was proven
only through a token inserted directly in Postgres. `GET /api/businesses` fails with
`column businesses.credit_balance does not exist`, which is why the banner and the reconnecting
pill are what the workspace truthfully shows.

Not changed, deliberately: no `Project` wiring, no workspace decomposition, no brand/admin type
rewrites, no move of marketing into the platform app (phase 2).

Later documentation pass, 19 November 2026: the handoff helper was re-read and
`toSafePath` was confirmed to reject values whose parsed pathname is not app-relative, in
addition to protocol-relative and backslash-prefixed ones. That pass added no runtime evidence:
the stack had already been shut down, so nothing was re-exercised in a browser.
The browser, provider and keyboard results above were collected earlier the same day with
Postgres, the API, marketing and platform all running; they stand as the Sprint 1 evidence.
`git diff --check` passes for the documentation edits.

---

## 6. Remaining backend contract decisions

1. Publish the state response and route keyed by the canonical `business_id`, including brand,
   site-build, review, approval, and run projections with truthful lifecycle states.
2. Make chat start/resume accept `business_id` and return the existing persisted conversation
   for that business when appropriate.
3. Does the waitlist entry become an account/business on invite, or is the idea handoff purely
   client-side? This determines whether `business_description` needs a migration into the chat.
4. Ownership of the snake_case → view-model mapping for `Brand`, `Order`, and `Review` — client
   adapter or backend-friendly shape?
