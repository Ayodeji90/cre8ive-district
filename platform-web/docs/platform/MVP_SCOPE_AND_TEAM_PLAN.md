# Cre8ive District Platform — MVP Scope, Feature Map and Team Plan

**Date:** 2026-11-07
**Inputs:** `PROJECT_ROADMAP.md`, `IMPLEMENTATION_PLAN.md`, `IMPL_BRAND_GENERATION.md`,
`IMPL_WEBSITE_GENERATION.md`, `IMPL_WHATSAPP_INTAKE.md`, `IMPL_PAYSTACK_BILLING.md`,
`IMPL_SOCIAL_MEDIA_INTEGRATION.md`
**Purpose:** Cut the plan down to what must ship first, and size the team and
calendar time to build it.

---

## 1. The decision in one page

**MVP:** a customer describes their business on WhatsApp, receives AI-generated
brand concepts, approves them, pays in Naira, and gets a downloadable brand kit
plus a live 3 to 5 page website. Nothing else.

**Build time:** **12 weeks** of calendar time after kickoff, with **4 engineers
and 1 brand designer** working full time. First real end-to-end brand in week 7.
Ten beta businesses in weeks 10 to 11. Public launch in week 12.

**First paying customer:** week 10 to 11 realistically, not week 6. The
roadmap's "first paying customer week 6" assumes brand generation is production
ready by then; integration and payment edge cases eat two to three weeks.

**No machine learning engineer is needed for the MVP.** Nothing is trained,
fine-tuned, or self-hosted. Every model is an API call (Claude, Ideogram,
Whisper). What the team needs is an engineer who is good at prompt design,
structured model output, and image post-processing, not someone who builds
models.

**External lead time, start this week:** Meta business verification and WhatsApp
template approval (1 to 3 weeks), Paystack business account, the `cre8ive.ng`
domain and wildcard DNS, Vercel team, Cloudflare R2 bucket. These are not
engineering tasks and they are the most likely reason launch slips.

---

## 2. What is in the MVP, what is not

### In scope (must ship)

| # | Capability | Why it is MVP |
|---|---|---|
| 1 | WhatsApp intake with AI consultant and 11-state conversation machine | It is the product's front door and the reason the offer is different |
| 2 | AI brand generation: brief, palette, fonts, 3 logo concepts + refinement, guidelines PDF | The core deliverable customers pay for |
| 3 | Asset packaging: SVG, PNG set, favicon, social avatars, ZIP | Without files there is no product |
| 4 | AI website generation: 3 to 5 pages from a component library, deployed to a subdomain | The second half of the promise |
| 5 | Paystack one-time payment in Naira, payment link sent in chat, webhook confirmation | No payment, no business |
| 6 | Delivery in chat plus a permanent download page | WhatsApp media limits and expired links make chat-only delivery fragile |
| 7 | Internal review queue and quality gate before delivery | Protects the brand promise at low volume |
| 8 | Minimal admin: businesses, orders, generations, revenue, failure logs | Needed to run the beta without engineering involvement |
| 9 | Cost and failure tracking per generation | The unit economics only work if measured |

### Out of scope for the MVP (deferred, deliberately)

- Social media account connection and auto-posting. Phase 2, and it carries a
  2 to 8 week app review per platform.
- Monthly subscriptions and recurring billing. Phase 3. One-time sales first.
- Customer self-serve dashboard. Phase 3. The customer lives in WhatsApp.
- E-commerce, booking systems, blog/CMS, custom software. Quoted custom work,
  not platform features.
- Self-serve custom domain purchase. Premium tier, manual setup at launch.
- Referral credits, promo codes, multi-language, mobile app, AI video.

The roadmap and the implementation plans already agree on this split; the
`IMPL_SOCIAL_MEDIA_INTEGRATION.md` timeline (weeks 9 to 20) belongs to Phase 2
and 3 and must not be pulled into the MVP.

---

## 3. Feature map

Priority: **P0** = launch blocker, **P1** = needed during beta, **P2** = after
launch. Owner codes: **BE-AI** (AI/backend engineer), **BE-CONV** (conversation
engineer), **BE-INT** (integrations/backend engineer), **FE** (frontend/full
stack engineer), **DES** (brand designer), **TL** (tech lead).

### 3.1 Platform foundation

| Feature | P | Done means | Owner |
|---|---|---|---|
| Repo, Docker Compose, environments (dev/staging/prod) | P0 | One command boots API, Postgres, Redis, worker | TL |
| Postgres schema and Alembic migrations for 7 core tables | P0 | Businesses, brands, websites, conversations, messages, orders, reviews | TL |
| Redis sessions, job queue, rate limiting | P0 | Conversation state survives restarts; jobs retry | TL |
| R2 asset storage with signed URLs | P0 | Uploads and 7-day signed downloads work | BE-INT |
| Internal auth (admin/designer roles) | P0 | Only team members reach `/admin` | FE |
| Structured logging, Sentry, uptime check | P0 | A failed generation is visible within minutes | BE-INT |
| Cost ledger per generation | P0 | Every brand and site records its API cost | BE-AI |
| Backups and restore drill | P0 | Database restores into staging | TL |

### 3.2 Conversation and intake

| Feature | P | Done means | Owner |
|---|---|---|---|
| WhatsApp Cloud API webhook with signature verification | P0 | Real message from a real phone creates a session | BE-CONV |
| Send text, image, document, interactive buttons and lists | P0 | All five message types verified on device | BE-CONV |
| 11-state machine with deterministic transitions | P0 | Happy path and every back edge tested | BE-CONV |
| AI consultant persona, short replies, Pidgin tolerance | P0 | 20 scripted conversations pass review | BE-CONV |
| Structured intake extraction after every message | P0 | Fields populate without re-asking | BE-CONV |
| Session persistence (Redis hot, Postgres permanent) and resume | P0 | Closing WhatsApp and returning after a day continues the thread | BE-CONV |
| Timeouts, nudges, abandoned conversation handling | P1 | No session hangs silently | BE-CONV |
| Voice note transcription (Whisper) | P1 | 30-second voice note becomes usable intake text | BE-CONV |
| Reference image upload from customer | P2 | Stored and passed to the brand prompt | BE-CONV |
| Human handoff to the team phone | P0 | Escalation reaches a person, not a void | BE-CONV |
| Approved template messages (follow-up, reminder, delivery) | P0 | Meta approves all three | BE-CONV |

Note: build the conversation layer transport-agnostic. A web chat widget is a
P1 fallback only if Meta verification is delayed, not a parallel product.

### 3.3 Brand generation

| Feature | P | Done means | Owner |
|---|---|---|---|
| Brand brief from description (strict JSON, one retry) | P0 | 10 diverse businesses produce usable briefs | BE-AI |
| Palette generation with WCAG contrast and distinctness checks | P0 | Zero failing palettes in 20 runs, auto-repair works | BE-AI |
| Typography selection from curated pairing library (40 pairs) | P0 | Every output pair exists on Google Fonts | DES / BE-AI |
| Logo concepts: 3 directions x 2 variants | P0 | 6 usable candidates per brand, under 3 minutes | BE-AI |
| Multimodal selection of the best concept | P0 | Top pick acceptable to the designer 8 of 10 times | BE-AI |
| Refinement pass on the winner | P1 | Winner improves measurably, not just differently | BE-AI |
| Background removal, SVG trace, PNG sizes, favicon | P0 | Vector file opens cleanly in Illustrator/Figma | BE-AI |
| Icon mark and wordmark variants | P0 | Both exist and are used in the kit | BE-AI |
| Social avatars (Instagram, WhatsApp, X sizes) | P0 | Correct dimensions, circular crop | BE-AI |
| Guidelines PDF (8 to 12 pages, brand-styled) | P0 | PDF under 16 MB, no overflow, real numbers | DES / BE-AI |
| Quality gate: contrast, completeness, file validity | P0 | Blocks incomplete packages from reaching review | BE-AI |
| Revision rounds (max 3) with notes | P0 | Customer-requested changes re-run without losing intake | BE-AI / BE-CONV |

### 3.4 Website generation

| Feature | P | Done means | Owner |
|---|---|---|---|
| Component library: ~25 sections, 5 themes | P0 | Every component renders with test props on mobile and desktop | FE / DES |
| Brand tokens injected as CSS variables | P0 | Changing the palette restyles the whole site | FE |
| SiteSpec generation and Pydantic validation | P0 | Valid spec for 10 business types, retry on invalid JSON | FE |
| Assembler: pages, nav, footer, sitemap, robots, meta, JSON-LD | P0 | Complete static file tree from one spec | FE |
| Imagery strategy (owner photos + curated stock) | P0 | No invented products, no broken image links | FE / DES |
| Favicon, Open Graph image, image optimisation, critical CSS | P0 | Lighthouse mobile performance 90+ | FE |
| Quality checks: valid HTML, links resolve, no horizontal scroll | P0 | Broken output is rejected before deploy | FE |
| Vercel deploy, subdomain assignment, redeploy flow | P0 | New site live in under 60 seconds after render | FE / BE-INT |
| Custom domain (manual, premium) | P2 | Documented runbook, not self-serve | BE-INT |
| Site edit request after delivery | P1 | One page can be regenerated without rebuilding the site | FE |

Open gap in the source docs: the SiteSpec examples use placeholder images but no
plan says where real imagery comes from. Recommendation in section 7.

### 3.5 Billing

| Feature | P | Done means | Owner |
|---|---|---|---|
| Paystack client: initialise, verify, plan, refund | P0 | Test-mode payment completes end to end | BE-INT |
| Order model with status machine and idempotency | P0 | Duplicate `charge.success` cannot double-deliver | BE-INT |
| Webhook with HMAC verification, async processing | P0 | Forged webhook rejected, valid one processed once | BE-INT |
| Payment link delivered in WhatsApp | P0 | Link opens Paystack checkout on a phone | BE-CONV |
| Bank transfer waiting state and "I've paid" verification | P0 | Never trusts the customer's claim, always verifies | BE-INT |
| Reminders at 2h / 24h / 72h, order expiry | P1 | Abandoned orders stop cleanly | BE-CONV |
| Receipt message and order history | P0 | Customer and admin can both see what was paid | BE-INT |
| Reconciliation job (Paystack vs orders) | P1 | Daily mismatch report is empty | BE-INT |
| Refund path | P1 | One documented, logged manual process | BE-INT |

### 3.6 Review, delivery, admin

| Feature | P | Done means | Owner |
|---|---|---|---|
| Review queue with side-by-side brand, brief, conversation | P0 | Designer can judge a package without leaving the page | FE |
| Approve / request AI revision / manual fix / reject | P0 | Each action changes status and notifies the customer | FE |
| Delivery: ZIP, signed link, PDF and logo in chat, live URL | P0 | Customer receives everything in one conversation | BE-INT |
| Permanent asset page (magic link, re-downloadable) | P0 | Link still works after 30 days | FE / BE-INT |
| Admin: businesses, orders, generations, failures, revenue | P0 | Founder runs a week of beta without SQL | FE |
| Review SLA/escalation timer | P1 | Nothing sits unreviewed over 4 hours | FE |
| Team notification on handoff or failed generation | P0 | Someone is pinged, with context | BE-CONV |

### 3.7 Marketing site and legal

| Feature | P | Done means | Owner |
|---|---|---|---|
| Platform pricing page aligned with real packages | P0 | No conflicting prices anywhere on the site | DES / founder |
| Click-to-WhatsApp entry point with prefilled message | P0 | Tap opens chat in GREETING | FE |
| Privacy policy, terms, AI disclosure, refund policy | P0 | Reviewed, published, linked in chat | founder |
| NDPR handling for phone numbers, conversations, uploaded photos | P0 | Documented retention and deletion path | TL |
| Logo/trademark caution in the customer flow | P0 | Customer told to check the mark before commercial use | DES |

### Effort summary

| Workstream | Engineering weeks | Source doc estimate | Notes |
|---|---|---|---|
| Platform foundation and infra | 3 | not stated | Underestimated in all source docs |
| Conversation and intake | 6 | 5 weeks | Plus Meta approval lead time |
| Brand generation | 7 | 4 weeks + 1 buffer | Logo quality is the biggest unknown |
| Website generation | 6 | 4 weeks | Component library is front-loaded |
| Billing | 2.5 | 2 weeks | Bumped for reconciliation and refunds |
| Review, delivery, admin | 6 | 2 weeks (polish) | Dashboard is real work, not polish |
| Integration, QA, beta fixes | 4 | 4 weeks | Assumes two rounds of real feedback |
| **Total** | **~34.5** | | 4 engineers x 12 weeks = 48 available |

That leaves roughly 28 percent slack, which is the right amount for prompt
tuning, API surprises, and WhatsApp review delays.

---

## 4. Team

### Recommended: 5 people, 12 weeks

| Role | Count | Owns | Needed | Profile |
|---|---|---|---|---|
| **Tech lead / backend** | 1 | Architecture, database, infra, auth, release process, code review, billing integration | Weeks 1 to 12 | 6+ years, Python/FastAPI, Postgres, has shipped a paid product |
| **AI / backend engineer** | 1 | Brand brief, palette, fonts, logo generation, asset pipeline, guidelines PDF, quality gates, cost tracking | Weeks 1 to 12 | Strong prompt engineering with structured output, comfortable with Pillow/vtracer/cairosvg, pragmatic about model quality |
| **Conversation engineer (backend)** | 1 | WhatsApp Cloud API, state machine, session management, extraction, delivery messages, handoff, follow-ups | Weeks 1 to 12 | Backend generalist with webhook/queue experience; no ML background needed |
| **Full-stack / frontend engineer** | 1 | Component library, themes, assembler, Vercel deploy, admin dashboard, download page, web fallback | Weeks 1 to 10 | Strong CSS and HTML semantics, Jinja or templating, plus Next.js/React for the dashboard |
| **Brand designer (not an engineer)** | 1 | Prompt and style standards, component and theme design, guidelines PDF template, logo and output QA, review queue | Weeks 1 to 12 | Senior identity designer who can articulate rules, not just make artefacts |

**Variable, not full time:** a QA/support person from week 8 (0.5 FTE) to run
beta conversations and regression passes; a copywriter for site and legal copy
(contract, 1 week); a lawyer or compliance reviewer for terms and NDPR (contract,
2 days).

**Founder role:** product owner, pricing, beta recruitment, review escalation,
and the person who talks to every one of the first 10 customers. Do not delegate
this in the beta.

### What each engineer actually builds, week by week

| Engineer | Weeks 1 to 4 | Weeks 5 to 8 | Weeks 9 to 12 |
|---|---|---|---|
| Tech lead | Schema, infra, auth, CI, cost ledger | Billing, webhooks, reconciliation, security pass | Observability, load test, launch runbook, fixes |
| AI engineer | Brief, palette, typography, logo generation | Asset pipeline, guidelines PDF, quality gate, prompt tuning | Beta prompt fixes, cost reduction, revision quality |
| Conversation engineer | WhatsApp client, webhook, sessions, state machine | Extraction, templates, payment and delivery messages, handoff | Edge cases, Pidgin tests, follow-ups, support tooling |
| Frontend | Component library (25 sections), 5 themes, assembler | Dashboard: review queue, businesses, orders, asset page | Website quality checks, Lighthouse, beta UI fixes |
| Designer | Brand prompt library, component visual design, PDF template | QA on first 20 outputs, review queue live, imagery direction | Polish, marketing assets, standards document |

### Smaller and larger configurations

| Team | Realistic timeline | Consequence |
|---|---|---|
| 4 engineers + 1 designer | **12 weeks** | Recommended. Slack for prompt iteration and review delays |
| 3 engineers + 1 designer | 16 to 18 weeks | Cut the admin dashboard to read-only and do reviews in a spreadsheet |
| 2 engineers + 1 designer | 22 to 26 weeks | Only viable if the WhatsApp flow launches with a manual payment link and manual asset delivery |
| 1 engineer + designer | 6+ months | Not a platform launch, a prototype |

Adding a fifth engineer past this point does not compress the 12 weeks much.
Brand quality and review, not code volume, set the pace in the second half.

### Skills that are explicitly not needed

- **No ML engineer or data scientist.** No training, no fine-tuning, no model
  hosting, no ranking model. If the team later trains a brand-style model, that
  is a Phase 4 hire.
- **No dedicated DevOps.** One backend engineer owns Docker, CI and a single
  Hetzner or Railway instance. This is a small system.
- **No mobile developer.** WhatsApp is the client.
- **No dedicated product manager** at this size. The founder plus tech lead
  cover it.

---

## 5. Twelve-week schedule

### Week 0 (start now, before engineering)

Meta Business account and verification, WhatsApp Business number, three message
templates submitted, Paystack business account and test keys, `cre8ive.ng`
purchased with wildcard DNS, Vercel team, R2 bucket, Anthropic and Ideogram API
keys, designer hired, beta list of 20 businesses started.

### Weeks 1 to 2 — Foundations and first vertical slices

Repo and infra, schema and migrations, auth, WhatsApp send/receive, session
store, state machine skeleton, brand brief and palette, component base template
plus 5 components, 5 themes drafted, Paystack client, dashboard shell.

**Checkpoint:** a hardcoded brand renders to a real PDF; a real WhatsApp message
gets a real reply.

### Weeks 3 to 4 — The four pillars in parallel

Logo generation and selection, asset pipeline, guidelines PDF; full component
library and assembler; all 11 states with extraction; orders and webhooks;
review queue first version.

**Checkpoint:** brand package generated from an API call; website tree rendered
from a SiteSpec.

### Weeks 5 to 6 — Integration

Orchestrator triggers brand generation, brand completion triggers the site,
payment gates delivery, review queue receives everything, Vercel deploy works,
ZIP delivery works, permanent asset page works.

**Checkpoint (gate 1, end of week 6):** one phone, one real business, one real
WhatsApp conversation, one live site, one real payment. If this is not true at
week 6, launch moves to week 14 and the scope gets cut, not the timeline.

### Weeks 7 to 9 — Hardening and quality

Lighthouse 90+ enforced, retries and fallbacks for every API, generation failure
paths, quality gates tightened, review SLA, cost per brand measured, load test
of 20 sequential generations, security review, templates approved.

**Checkpoint (gate 2, end of week 9):** 10 brands generated end to end with
fewer than 2 manual interventions, average cost per brand under ₦3,000, average
generation time under 10 minutes.

### Weeks 10 to 11 — Private beta

10 real businesses through the full flow. Founder watches every conversation.
One engineer on rotation for live fixes, one on prompt tuning, designer reviews
every package. Instrument everything: drop-off state, revision rate, review
time, delivery failures, willingness to pay.

**Checkpoint (gate 3):** 5 paying customers, satisfaction above 70 percent
without human redesign, no unresolved payment or delivery failures.

### Week 12 — Public launch

Pricing page live, WhatsApp entry point on the marketing site, support runbook,
refund process, on-call rota, public launch.

**Post-launch weeks 13 to 20:** Phase 2 begins, starting with Instagram and
Facebook connection only after Meta app review is submitted, plus monthly plans
and the customer dashboard.

---

## 6. What will actually go wrong

| Risk | Where it bites | Mitigation |
|---|---|---|
| Logo quality is inconsistent | Brand pipeline, week 5 onward | Designer builds a prompt library per industry in week 1; 20-output QA before beta; human review gate stays until quality is proven |
| SVG tracing produces messy vectors | Asset pipeline | Accept PNG-first delivery for MVP, label SVG as "cleaned vector"; invest in tracing only if customers complain |
| WhatsApp verification or templates delayed | Launch date | Start in week 0; web intake fallback built behind the same conversation layer |
| Real imagery missing on generated sites | Website generation | Owner photos via WhatsApp plus curated stock library; never AI-generate product shots |
| Review becomes a bottleneck | Operations | 15-minute review target; sample review after quality proves out; hire at 50 orders per week |
| Customers expect unlimited changes | Margins and support | Revision limits written into the package and enforced by the state machine |
| Free generations abused | Costs | One free concept preview per number, watermarked; full files only after payment |
| AI logos resemble existing marks | Legal and reputation | Trademark caution in the flow, customer signs off, designer spot-checks for obvious collisions |
| Meta or Paystack policy change | Delivery | Provider seams for messaging and payments from day one |

---

## 7. Decisions the founder needs to make before week 3

1. **Pricing.** The roadmap says ₦15k to ₦30k / ₦50k to ₦100k / ₦75k to ₦120k.
   The billing and WhatsApp docs say ₦20,000 / ₦60,000 / ₦120,000. Pick one set.
   Recommendation: ₦20k / ₦60k / ₦120k, because it is already written into the
   chat flow, Paystack plan names and margin model.
2. **Is human review mandatory before delivery?** The roadmap calls it an
   optional add-on; the implementation plan makes it a launch gate; the WhatsApp
   flow has no review step at all. Recommendation: mandatory for the first 100
   orders, then sample review. Charge for a *priority* designer pass, never for
   basic quality.
3. **When does payment happen?** The integration sprint says paid before
   generation; the conversation flow generates first and charges before delivery.
   Recommendation: free watermarked concept, payment unlocks files and site. This
   converts better and costs at most one wasted generation per number.
4. **Where do website images come from?** Not answered anywhere in the docs.
   Recommendation: owner photos plus a curated stock library. No AI product
   imagery.
5. **Which domain do generated sites use?** The roadmap says
   `{slug}.cre8ivedistrict.com`; the website plan says `{slug}.cre8ive.ng`. Pick
   one and buy it now.
6. **Is WhatsApp the only channel at launch?** Recommendation: yes, with web
   intake as a fallback only, not a second product.
7. **Refund and guarantee policy.** Not specified. Needed before the first
   payment link is sent, because the first unhappy customer sets the precedent.

---

## 8. Running costs and unit economics for the MVP

| Line | Monthly estimate |
|---|---|
| Hetzner or Railway backend (1 instance + worker) | €12 to €25 |
| Managed Postgres (or same instance) | ₦0 to ₦25,000 |
| Redis (same instance or Upstash free tier) | ₦0 to ₦8,000 |
| Cloudflare R2 storage and bandwidth | under $2 |
| Vercel Pro (generated sites) | $20 |
| Email (SES) | under $1 |
| WhatsApp templates at 50 customers | ~₦7,500 |
| Sentry, uptime monitoring | free tier |
| Domain | ~$12 per year |
| **Fixed platform cost** | **roughly ₦70,000 to ₦90,000 per month** |

Per-order variable cost from the plan docs: brand generation about ₦660, website
about ₦90, Paystack about 1.5 percent plus ₦100, WhatsApp near zero. Call it
**₦1,000 to ₦2,000 per delivered order**, plus 15 minutes of designer review.
That supports a ₦20,000 entry price with a healthy margin, and a ₦60,000 package
with a very healthy one.

Caution: `IMPLEMENTATION_PLAN.md` section 9 quotes ₦6,500 COGS per brand while
the brand and website docs quote ₦660 and ₦90. The higher figure double-counts
image generation and uses a different exchange rate. Measure actual cost per
brand during beta and replace both numbers with the measured value.

---

## 9. Definition of done for the MVP

- A new customer can go from first WhatsApp message to a paid, delivered brand
  kit and live website without a team member touching the happy path.
- Brand generation completes in under 5 minutes, site generation and deploy in
  under 10, and the customer is never left without a status message for more
  than 30 seconds.
- Every delivered logo has SVG and PNG variants, a palette with accessible
  contrast, a font pairing, a guidelines PDF, favicon and avatars.
- Every delivered site scores 90+ Lighthouse mobile performance, works at 360px
  width, and has a working WhatsApp CTA.
- Payments reconcile: every paid order maps to a delivery, and every delivery
  maps to a paid order.
- The team can see, for any order: conversation, generation cost, review time,
  delivery status and failures.
- 10 beta businesses delivered, 5 paid, fewer than 5 percent of orders needing
  manual rescue.
