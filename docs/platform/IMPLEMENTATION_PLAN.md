# Cre8ive District — AI Platform Implementation Plan

*Technical blueprint for the AI-powered brand launch platform. This document
defines the system architecture, tech stack, core services, data model,
integrations, development phases, and quality gates.*

**Date:** 2026-11-07
**Status:** Draft — pending founder review

---

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CUSTOMER CHANNELS                            │
│   WhatsApp Business API  ·  Web Chat Widget  ·  Email Intake        │
└──────────────┬──────────────────────┬──────────────────┬────────────┘
               │                      │                  │
               ▼                      ▼                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  CONVERSATION SERVICE                                                │
│  Session management · Context tracking · Message normalisation       │
│  { business_id, channel, conversation_id, sender, content, … }      │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  ORCHESTRATOR (AI Agent Loop)                                        │
│  plan → select tool → execute → observe → repeat                     │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ Brand Gen    │  │ Website Gen  │  │ Copy / Strat │               │
│  │ Tool         │  │ Tool         │  │ Tool         │               │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │
│         │                 │                  │                        │
│         ▼                 ▼                  ▼                        │
│  ┌─────────────────────────────────────────────────┐                 │
│  │            OUTPUT PIPELINE                       │                 │
│  │  Asset rendering · PDF export · Site packaging   │                 │
│  └──────────────────────┬──────────────────────────┘                 │
└─────────────────────────┼───────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│  APPROVAL QUEUE                                                      │
│  Designer reviews AI output · approve / refine / reject              │
│  ┌────────────────────┐  ┌─────────────────────┐                     │
│  │  Admin Dashboard   │  │  Notification Bus    │                    │
│  │  (React / Next.js) │  │  (Redis pub/sub)     │                    │
│  └────────────────────┘  └─────────────────────┘                     │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  DELIVERY SERVICE                                                    │
│  Brand kit packaging · WhatsApp file delivery · Email with links     │
│  Website publish trigger → Vercel                                    │
└─────────────────────────────────────────────────────────────────────┘

  ┌──────────────────────────── DATA LAYER ──────────────────────────┐
  │  PostgreSQL (business, brand, website, conversation, order)       │
  │  Redis (session state, queues, pub/sub, rate limiting)            │
  │  S3 / Cloudflare R2 (brand assets, logos, PDFs, site snapshots)  │
  └──────────────────────────────────────────────────────────────────┘

  ┌──────────────────────────── BILLING ─────────────────────────────┐
  │  Paystack (subscriptions, one-time payments, webhooks)            │
  │  Credit ledger (track AI compute usage per business)              │
  └──────────────────────────────────────────────────────────────────┘
```

---

## 2. Tech Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Backend** | Python 3.12 + FastAPI + async SQLAlchemy | Proven in our prior AI product work; strong async support; large AI/ML ecosystem |
| **Database** | PostgreSQL 16 | Relational integrity, JSONB for flexible config, pgvector if RAG is needed later |
| **Cache / Queue** | Redis 7 | Session state, pub/sub for notifications, job queues for async generation tasks |
| **Admin Dashboard** | Next.js 15 (App Router) | React ecosystem, deployable on Vercel alongside generated sites, SSR for the review interface |
| **AI — Copy & Strategy** | Claude API (Sonnet for speed, Opus for quality) | Best instruction-following for brand voice, structured JSON output |
| **AI — Logo / Image** | Ideogram 3 API (primary), DALL-E 3 (fallback) | Ideogram leads on typography-in-image (critical for logos); DALL-E as backup |
| **AI — Website Code** | Claude API (Sonnet / Opus) | Generates clean HTML/CSS/JS from brand spec + business description |
| **Website Hosting** | Vercel | Zero-config static deploys via API; global CDN; custom domain support |
| **Platform Hosting** | Hetzner CX32 (€12/mo) or Railway | Cost-effective for a Python backend; Docker-native |
| **Asset Storage** | Cloudflare R2 (S3-compatible, zero egress fees) | Logos, PDFs, brand kits — served via Cloudflare CDN |
| **Messaging** | WhatsApp Business API via 360dialog or Twilio | 360dialog is cheaper; Twilio has broader docs. BSP handles Meta verification. |
| **Payments** | Paystack | Nigerian market standard; supports subscriptions, one-time charges, Naira billing |
| **Email** | Amazon SES or SendGrid | Transactional emails (brand kit delivery, receipts, notifications) |
| **PDF Rendering** | WeasyPrint or Puppeteer | Brand guidelines PDF generation from HTML template |
| **Containerisation** | Docker + Docker Compose | Consistent dev/prod environments |

---

## 3. Core Services

### 3.1 Conversation Service

**Purpose:** Handle all inbound/outbound messaging across channels, maintain
session context, and route customer intent to the orchestrator.

**Responsibilities:**
- Receive WhatsApp webhook events (text, image, voice note, document)
- Transcribe voice notes (Whisper API or equivalent)
- Maintain conversation state in Redis (TTL: 24h idle)
- Persist conversation history to PostgreSQL
- Detect customer intent: new brand request, revision, question, payment
- Route to the orchestrator with full context

**Key endpoints:**
```
POST /api/webhooks/whatsapp      — inbound from BSP
POST /api/webhooks/webchat       — inbound from web widget
POST /api/conversations/{id}/send — outbound message
GET  /api/conversations/{id}      — conversation + messages
```

### 3.2 Brand Generation Service

**Purpose:** Orchestrate logo creation, colour palette, typography selection,
and brand guidelines document from a business description.

**Responsibilities:**
- Accept a `BrandRequest` (business name, description, industry, preferences)
- Generate 3 logo concepts via image generation API (Ideogram/DALL-E)
- Derive a 5-colour palette (primary, secondary, accent, neutral, background) using the LLM + colour theory rules
- Select font pairings (heading + body) from a curated library of 20 Google Fonts combinations
- Compose a brand guidelines document (HTML → PDF via WeasyPrint)
- Store all assets in R2 with structured paths: `/{business_id}/brand/{version}/`
- Create `Brand` record with status `draft`

**Key endpoints:**
```
POST /api/brands/generate        — trigger generation
GET  /api/brands/{id}            — brand record + asset URLs
POST /api/brands/{id}/regenerate — request new concepts
PATCH /api/brands/{id}/approve   — designer approves → status: approved
```

### 3.3 Website Generation Service

**Purpose:** Generate a responsive, production-quality 3–5 page website from the
approved brand identity and business information, then deploy it to Vercel.

**Responsibilities:**
- Accept an approved `Brand` + business description + page requirements
- Generate HTML/CSS/JS for each page using the LLM, applying the brand's colours, fonts, and logo
- Validate output: valid HTML, responsive meta tags, image references resolve, no broken links
- Run Lighthouse CI check (target: performance > 90, accessibility > 90)
- Deploy to Vercel via their REST API (`POST /v13/deployments`)
- Configure custom subdomain: `{business-slug}.cre8ivedistrict.com`
- Allow custom domain connection later (Vercel domain API)
- Store generated code in R2 and website metadata in PostgreSQL

**Key endpoints:**
```
POST /api/websites/generate           — trigger generation
GET  /api/websites/{id}               — website record + preview URL
POST /api/websites/{id}/deploy        — deploy to Vercel
POST /api/websites/{id}/pages         — add/edit a page
PATCH /api/websites/{id}/approve      — designer approves
```

### 3.4 Asset Pipeline

**Purpose:** Render, format, and package all brand deliverables into a
downloadable kit.

**Responsibilities:**
- Render logo to multiple formats: SVG (vector), PNG (transparent, 1024px, 512px, 256px, 128px, 64px), favicon ICO
- Generate social media avatar crops (square, circle)
- Build brand guidelines PDF (cover page, logo usage, colour specs with hex/RGB/CMYK, typography, do's & don'ts)
- Package everything into a ZIP: `{BusinessName}_BrandKit.zip`
- Upload ZIP to R2, generate a signed download URL (expires: 7 days)

**Key endpoints:**
```
POST /api/assets/{brand_id}/render    — trigger rendering pipeline
GET  /api/assets/{brand_id}/download  — signed ZIP URL
GET  /api/assets/{brand_id}/files     — list individual assets
```

### 3.5 Billing Service

**Purpose:** Manage Paystack subscriptions, one-time brand package purchases,
and credit-based usage tracking.

**Responsibilities:**
- Create Paystack customer on business signup
- Handle plan selection: one-time brand package or monthly subscription
- Process Paystack webhooks (payment success, subscription renewal, failure)
- Maintain a credit ledger: each AI generation task deducts credits
- Enforce plan limits before triggering generation (check credits → proceed or prompt upgrade)
- Generate receipts (Paystack handles this, we store references)

**Key endpoints:**
```
POST /api/billing/initialize         — create payment session
POST /api/webhooks/paystack          — Paystack webhook handler
GET  /api/billing/{business_id}      — current plan, credits, history
POST /api/billing/verify/{reference} — verify payment
```

### 3.6 Approval Queue

**Purpose:** Route all AI-generated output through human review before customer
delivery. This is the quality layer that separates Cre8ive District from pure
AI tools.

**Responsibilities:**
- Queue every generated brand, website, and asset package for designer review
- Assign reviewers (round-robin or manual)
- Provide side-by-side view: AI output + business brief + customer conversation
- Allow actions: approve, request AI revision (with notes), manual edit, reject
- Track review metrics: time-to-review, revision rate, rejection rate
- Notify customer via WhatsApp when their brand is ready
- Publish SSE events to the admin dashboard for real-time updates

**Key endpoints:**
```
GET  /api/reviews/queue              — pending reviews (filterable)
GET  /api/reviews/{id}               — review detail + assets
POST /api/reviews/{id}/approve       — approve and trigger delivery
POST /api/reviews/{id}/revise        — request AI revision with notes
POST /api/reviews/{id}/reject        — reject with reason
```

### 3.7 Delivery Service

**Purpose:** Package approved deliverables and send them to the customer.

**Responsibilities:**
- Assemble final brand kit (ZIP with all approved assets)
- Send WhatsApp message with download link + summary
- Send email with brand kit attached / linked
- If website was generated: send live URL
- Track delivery status (sent, downloaded, opened)

**Key endpoints:**
```
POST /api/delivery/{order_id}/send   — trigger delivery
GET  /api/delivery/{order_id}/status — delivery tracking
```

---

## 4. Data Model

### `businesses`
```
id              uuid PK
name            varchar(200)
slug            varchar(100) UNIQUE
description     text
industry        varchar(80)
location        varchar(120)
contact_phone   varchar(20)        -- WhatsApp number
contact_email   varchar(200) NULL
plan            varchar(24)        -- free | starter | pro | studio
status          varchar(16)        -- onboarding | active | suspended
preferences     jsonb {}           -- style preferences, colours, industry keywords
created_at / updated_at
```

### `brands`
```
id              uuid PK
business_id     uuid FK → businesses (CASCADE)
version         int default 1
logo_url        varchar(500) NULL
logo_svg_url    varchar(500) NULL
colors          jsonb {}           -- {primary, secondary, accent, neutral, background}
fonts           jsonb {}           -- {heading: {family, weight}, body: {family, weight}}
guidelines_pdf  varchar(500) NULL  -- R2 URL
kit_zip_url     varchar(500) NULL  -- R2 URL
status          varchar(24)        -- generating | draft | in_review | approved | delivered
created_at / updated_at
```

### `websites`
```
id              uuid PK
business_id     uuid FK → businesses (CASCADE)
brand_id        uuid FK → brands NULL
deployment_url  varchar(500) NULL  -- Vercel URL
custom_domain   varchar(200) NULL
vercel_id       varchar(100) NULL  -- Vercel deployment ID
pages           jsonb []           -- [{slug, title, content_hash}]
lighthouse      jsonb NULL         -- {performance, accessibility, seo, best_practices}
status          varchar(24)        -- generating | draft | in_review | approved | live
created_at / updated_at
```

### `conversations`
```
id              uuid PK
business_id     uuid FK → businesses NULL  -- NULL until business is created
channel         varchar(16)        -- whatsapp | webchat | email
external_id     varchar(200)       -- WhatsApp conversation ID or equivalent
phone_number    varchar(20) NULL
status          varchar(16)        -- active | idle | closed
context         jsonb {}           -- accumulated business description, preferences
created_at / updated_at
```

### `messages`
```
id              uuid PK
conversation_id uuid FK → conversations (CASCADE)
direction       varchar(8)         -- inbound | outbound
content         text
media_url       varchar(500) NULL
media_type      varchar(40) NULL   -- image | audio | document
role            varchar(16)        -- customer | assistant | system
created_at
```

### `orders`
```
id              uuid PK
business_id     uuid FK → businesses (CASCADE)
plan            varchar(24)        -- brand_starter | brand_pro | brand_studio
amount          numeric(12,2)
currency        varchar(8) default 'NGN'
paystack_ref    varchar(120) NULL
status          varchar(24)        -- pending | paid | fulfilled | refunded
deliverables    jsonb {}           -- {brand_id, website_id, kit_url}
paid_at         timestamptz NULL
fulfilled_at    timestamptz NULL
created_at / updated_at
```

### `reviews`
```
id              uuid PK
order_id        uuid FK → orders NULL
brand_id        uuid FK → brands NULL
website_id      uuid FK → websites NULL
reviewer_id     uuid FK → users NULL    -- designer assigned
status          varchar(16)        -- pending | in_progress | approved | revision_requested | rejected
notes           text NULL
reviewed_at     timestamptz NULL
created_at / updated_at
```

### `users` (internal team)
```
id              uuid PK
email           varchar(200) UNIQUE
name            varchar(120)
role            varchar(24)        -- admin | designer | support
created_at / updated_at
```

---

## 5. Integration Map

```
┌─────────────────────┐       ┌────────────────────────┐
│ WhatsApp Business   │◄─────►│ Conversation Service   │
│ API (via BSP)       │       │ POST /api/webhooks/wa  │
└─────────────────────┘       └────────────────────────┘

┌─────────────────────┐       ┌────────────────────────┐
│ Claude API          │◄─────►│ Brand Gen Service      │
│ (Sonnet / Opus)     │       │ Website Gen Service    │
│                     │       │ Copy & Strategy Tool   │
└─────────────────────┘       └────────────────────────┘

┌─────────────────────┐       ┌────────────────────────┐
│ Ideogram 3 API      │◄─────►│ Brand Gen Service      │
│ (logo generation)   │       │ (logo concepts)        │
│ DALL-E 3 (fallback) │       │                        │
└─────────────────────┘       └────────────────────────┘

┌─────────────────────┐       ┌────────────────────────┐
│ Vercel REST API     │◄─────►│ Website Gen Service    │
│ (deployments, DNS)  │       │ POST deployments       │
└─────────────────────┘       └────────────────────────┘

┌─────────────────────┐       ┌────────────────────────┐
│ Paystack API        │◄─────►│ Billing Service        │
│ (payments, subs)    │       │ POST /api/webhooks/ps  │
└─────────────────────┘       └────────────────────────┘

┌─────────────────────┐       ┌────────────────────────┐
│ Cloudflare R2       │◄─────►│ Asset Pipeline         │
│ (S3-compatible)     │       │ (logos, PDFs, ZIPs)    │
└─────────────────────┘       └────────────────────────┘

┌─────────────────────┐       ┌────────────────────────┐
│ Amazon SES /        │◄─────►│ Delivery Service       │
│ SendGrid            │       │ (brand kit emails)     │
└─────────────────────┘       └────────────────────────┘
```

---

## 6. Development Phases

### Phase 1 — Parallel Workstreams (Weeks 1–6)

All four workstreams build independently against shared interfaces
(`BrandRequest`, `WebsiteRequest`, `ConversationContext`, `PaymentSession`).

| Stream | Scope | Owner |
|--------|-------|-------|
| **1A — Brand Generation Pipeline** | Logo gen + palette + fonts + guidelines PDF + asset rendering | See `BRAND_GENERATION_PLAN.md` |
| **1B — Website Generation** | LLM site gen + Vercel deploy + Lighthouse validation | See `WEBSITE_GENERATION_PLAN.md` |
| **1C — WhatsApp Intake Flow** | BSP setup + conversation service + orchestrator + context extraction | See `WHATSAPP_INTAKE_PLAN.md` |
| **1D — Paystack Billing** | Plans + payment flow + webhooks + credit ledger | See `PAYSTACK_BILLING_PLAN.md` |

### Phase 2 — Integration Sprint (Weeks 7–8)

Wire all four workstreams together:
- Conversation service triggers brand generation on confirmed order
- Brand generation completion triggers website generation
- Billing gates generation (paid → generate; unpaid → prompt payment)
- Approval queue receives all generated output
- Delivery service fires on approval
- End-to-end test: WhatsApp message → payment → brand + site generated → designer approved → delivered via WhatsApp

### Phase 3 — Polish Sprint (Weeks 9–10)

- Admin dashboard: review queue, business list, analytics (orders, revenue, generation times)
- Designer review workflow: side-by-side comparison, inline editing, revision notes
- Edge cases: voice note transcription, image uploads from customer, multi-language support
- Error handling: generation failures, payment failures, Vercel deploy failures
- Monitoring: Sentry for errors, basic analytics dashboard, cost tracking per generation

### Phase 4 — Launch (Week 11–12)

- Soft launch: 10 businesses through the full flow (friends, network, early interest list)
- Measure: generation quality, review time, customer satisfaction, cost per brand
- Iterate on prompts, templates, and review workflow based on real output
- Public launch on Cre8ive District website with updated messaging and pricing

---

## 7. Quality Gates

| Gate | Trigger | Criteria | Failure action |
|------|---------|----------|----------------|
| **Logo quality** | After image generation | Min resolution 1024px; no text artefacts; valid SVG trace; colour contrast ≥ 4.5:1 (WCAG AA) | Regenerate with adjusted prompt |
| **Palette validation** | After colour derivation | All 5 colours distinct; primary↔background contrast ≥ 7:1; no pure black/white unless intentional | LLM re-derives with contrast constraint |
| **Font validation** | After font selection | Both fonts available on Google Fonts CDN; heading ≠ body; weights exist | Fallback to curated safe pairs |
| **Website quality** | After code generation | Valid HTML5; responsive meta; all images resolve; no JS errors; Lighthouse perf > 90, a11y > 90 | Regenerate failing pages; fall back to template |
| **Brand kit integrity** | After asset rendering | ZIP contains: logo (SVG + 5 PNG sizes + ICO), palette (JSON + image swatch), guidelines (PDF ≥ 4 pages), fonts (list + CSS snippet) | Block delivery; flag for manual fix |
| **Designer review** | Before delivery | At least one approve action from a team member with `designer` or `admin` role | Stays in queue; escalation after 4h |
| **Response latency** | Every WhatsApp exchange | Assistant reply within 30s of customer message | Alert; degrade to simpler/faster model |

---

## 8. Risk Register

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| **AI logo quality inconsistent** | High | Medium | Human designer review on every output; curated prompt library per industry; style-reference images; regeneration with feedback loop |
| **WhatsApp Business API approval delay** | Medium | High | Launch with web chat widget first (zero approval needed); apply for WhatsApp API immediately; add WhatsApp when approved |
| **Image generation cost overruns** | Medium | Low | Credit-based pricing covers compute; monitor cost per brand; cache common patterns; batch generation during off-peak |
| **Website generation produces broken output** | High | Medium | Template-based fallback library (12 industry templates); Lighthouse CI gate; manual fix path for designers |
| **Paystack integration edge cases** | Low | Medium | Idempotent webhook handler; manual verification fallback; reconciliation job |
| **Voice note transcription quality** | Low | Medium | Whisper API handles most languages; fallback: ask customer to type; flag low-confidence transcriptions |
| **Customer expects unlimited revisions** | Medium | Medium | Plans define revision count (e.g. starter: 2, pro: 5, studio: unlimited); clear in onboarding flow |
| **Designer review bottleneck at scale** | Medium | Low (at launch) | Automated quality gates reduce review burden; tiered review (AI-passed brands get lighter review); hire reviewers at ~50 orders/week |
| **Single point of failure on AI provider** | Medium | Low | Provider-agnostic seam: swap LLM (Claude ↔ GPT-4) and image gen (Ideogram ↔ DALL-E) via config |

---

## 9. Cost Projections (Per Brand Package)

| Cost line | Estimate | Source |
|-----------|----------|--------|
| LLM — brand strategy + copy (Claude Sonnet, ~5 calls) | ~₦800 | ~$0.50 at ₦1,600/$ |
| Image generation — 3 logo concepts (Ideogram) | ~₦1,600 | ~$1.00 (3 × $0.08/image at scale + iterations) |
| LLM — website generation (Claude Opus, ~3 calls) | ~₦2,400 | ~$1.50 |
| PDF rendering (compute) | ~₦50 | negligible |
| Vercel deployment | ₦0 | free tier (100 deploys/day) |
| R2 storage (assets) | ~₦30 | ~$0.015/GB, <100MB per brand |
| WhatsApp messages (~20 messages) | ₦0 | service conversations are free |
| Paystack fee (on ₦50k order) | ₦1,600 | 1.5% + ₦100, capped ₦2,000 |
| **Total marginal COGS** | **~₦6,500** | |
| **Gross margin at ₦50,000 price** | **~87%** | |
| **Gross margin at ₦100,000 price** | **~93%** | |

Designer review time (~15 min per brand at ₦3,000/hr equivalent) adds ~₦750,
keeping margins above 85% even at the lowest price point.

---

## 10. File Structure (Proposed)

```
cre8ive-platform/
├── api/                          # FastAPI backend
│   ├── app/
│   │   ├── main.py               # FastAPI app, middleware, lifespan
│   │   ├── config.py             # Settings (env-based)
│   │   ├── db.py                 # async SQLAlchemy engine + session
│   │   ├── models/               # SQLAlchemy ORM models
│   │   │   ├── business.py
│   │   │   ├── brand.py
│   │   │   ├── website.py
│   │   │   ├── conversation.py
│   │   │   ├── order.py
│   │   │   └── review.py
│   │   ├── services/             # Business logic
│   │   │   ├── conversation.py
│   │   │   ├── brand_gen.py
│   │   │   ├── website_gen.py
│   │   │   ├── asset_pipeline.py
│   │   │   ├── billing.py
│   │   │   ├── approval.py
│   │   │   └── delivery.py
│   │   ├── llm/                  # Provider-agnostic LLM layer
│   │   │   ├── service.py
│   │   │   ├── providers/
│   │   │   │   ├── anthropic.py
│   │   │   │   └── openai_compat.py
│   │   │   └── image_gen/
│   │   │       ├── ideogram.py
│   │   │       └── dalle.py
│   │   ├── routers/              # API endpoints
│   │   │   ├── webhooks.py
│   │   │   ├── brands.py
│   │   │   ├── websites.py
│   │   │   ├── conversations.py
│   │   │   ├── billing.py
│   │   │   ├── reviews.py
│   │   │   └── delivery.py
│   │   └── templates/            # Brand guidelines HTML template, email templates
│   ├── alembic/                  # Database migrations
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
├── dashboard/                    # Next.js admin dashboard
│   ├── app/
│   │   ├── reviews/              # Designer review queue
│   │   ├── businesses/           # Business list + detail
│   │   ├── analytics/            # Orders, revenue, generation stats
│   │   └── settings/
│   └── package.json
├── site-templates/               # Curated website component library
│   ├── components/               # Reusable HTML/CSS blocks
│   ├── layouts/                  # Full page layouts by industry
│   └── themes/                   # Colour/font application presets
├── brand-templates/              # Font pairings, colour theory rules, style refs
│   ├── fonts.json                # 20 curated Google Fonts pairings
│   ├── palettes/                 # Industry-specific palette seeds
│   └── style-refs/               # Reference images for logo generation prompts
├── docs/
│   └── platform/                 # This file and related plans
├── docker-compose.yml
└── .env.example
```

---

## Next Steps

1. Founder reviews and approves this plan
2. Finalise pricing tiers (see roadmap doc)
3. Begin Phase 1 workstreams in parallel — each has its own detailed plan
4. Set up the shared infrastructure: PostgreSQL, Redis, R2 bucket, Vercel team, Paystack test keys
