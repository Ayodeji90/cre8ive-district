# Cre8ive District — MVP Requirements for Product-Market Fit

**Date:** 16 November 2026
**Reference model:** Foundable (AI brand-launch platform, US market)
**Target:** Nigerian and African entrepreneurs launching businesses

This document defines every requirement needed to reach product-market fit. Each requirement is classified as Functional (what the system does) or Non-Functional (how well it does it), tagged with priority (P0 = launch blocker, P1 = needed within 30 days, P2 = deferred), and mapped to current implementation status.

**Product-market fit definition for this MVP:** A customer can describe their business, receive a coherent brand identity and working website, pay in Naira, and launch — all in one session, with quality that makes them share the product with other founders.

---

## Part 1 — Functional Requirements

Functional requirements describe what the system must do. Grouped by the customer journey.

### FR-1: Marketing and Discovery

| ID | Requirement | Priority | Status |
|---|---|---|---|
| FR-1.1 | Marketing site explains the product, shows example outputs, and communicates pricing in Naira | P0 | Partial — site exists, claims need review against actual capability |
| FR-1.2 | Waitlist form collects email and optional business description, confirms receipt | P0 | Implemented — route exists |
| FR-1.3 | Marketing site loads in under 3 seconds on a 3G Nigerian mobile connection | P0 | Not verified |
| FR-1.4 | SEO metadata, Open Graph tags, and share previews are populated for all public pages | P1 | Not verified |
| FR-1.5 | Blog or content section with at least 3 articles explaining the product value | P2 | Not started |

### FR-2: Identity and Access

| ID | Requirement | Priority | Status |
|---|---|---|---|
| FR-2.1 | Customer can sign up with email (magic link via Resend) or Google OAuth | P0 | Partial — Auth.js configured, adapter reported errors |
| FR-2.2 | Customer can sign in, sign out, and return to their workspace with session intact | P0 | Partial — sign-in/sign-up/welcome pages exist |
| FR-2.3 | JWT-based session tokens with expiry and refresh | P0 | Implemented — backend JWT validation exists |
| FR-2.4 | Each customer can only access their own businesses, conversations, brands, orders, and assets | P0 | Implemented — ownership checks on routes |
| FR-2.5 | Admin and designer roles can access the review queue; customers cannot | P0 | Implemented — role-based route protection |
| FR-2.6 | Account deletion: customer can request deletion of their account and all associated data | P1 | Not started |
| FR-2.7 | Password-less flow only (magic link + OAuth); no password storage | P0 | Implemented |

### FR-3: Guided Intake (Abija Chat)

| ID | Requirement | Priority | Status |
|---|---|---|---|
| FR-3.1 | Customer starts a conversation with Abija; Abija greets and asks about their business | P0 | Implemented — WebSocket chat with streaming |
| FR-3.2 | Conversation persists across page refreshes and reconnections | P0 | Implemented — stored history, Redis context |
| FR-3.3 | Abija extracts structured business context (name, industry, description, target audience, values, preferences) from the conversation | P0 | Implemented — context extraction updates business record |
| FR-3.4 | Abija asks clarifying questions when the brief is incomplete (missing industry, audience, or description) | P0 | Implemented in prompt system |
| FR-3.5 | Customer can view their conversation history and resume where they left off | P0 | Implemented — history endpoint |
| FR-3.6 | Chat handles AI provider failures gracefully: shows a retry message, does not lose context | P0 | Implemented — error handling in chat router |
| FR-3.7 | Chat supports text input with optional image/media upload (logo reference, inspiration) | P1 | Partial — schema supports media_url, processing not verified |
| FR-3.8 | Abija's personality is distinctly Nigerian: warm, creative, confident, uses culturally appropriate language | P0 | Implemented in Branding Agent prompt system |
| FR-3.9 | Conversation stage tracking (greeting → discovery → clarification → summary → confirmation) | P0 | Implemented — 7-stage state machine |
| FR-3.10 | Customer can start a new conversation / new business without losing previous ones | P1 | Partial — multi-business model exists |

### FR-4: Brand Generation

| ID | Requirement | Priority | Status |
|---|---|---|---|
| FR-4.1 | System generates a brand strategy document from the business brief: positioning, values, personality, tagline direction | P0 | Implemented — BrandStrategy model with 9 fields |
| FR-4.2 | System generates 3 logo concepts in different styles (icon+wordmark, abstract mark, lettermark) | P0 | Implemented — logo prompt builder with 3 concept types |
| FR-4.3 | System derives a color palette (primary, secondary, accent, neutrals) with WCAG contrast validation | P0 | Implemented — palette derivation with contrast checks |
| FR-4.4 | System selects a font pairing (heading + body) from a curated library of Google Fonts | P0 | Implemented — 20-pair curated library |
| FR-4.5 | System generates brand copy: tagline, short bio, elevator pitch, social media bio, hashtag set | P0 | Implemented — BrandCopy model |
| FR-4.6 | Automated quality validation: tagline length, positioning genericity check, contrast ratios, font availability, logo resolution | P0 | Implemented — ValidationResult model |
| FR-4.7 | Customer can preview all brand outputs in a visual brand board before approval | P0 | Partial — split preview UI exists, not verified end-to-end |
| FR-4.8 | Customer can request revisions to specific brand elements (regenerate logo, change colors, update tagline) | P0 | Partial — revision model exists, UI flow not complete |
| FR-4.9 | Brand generation works as a background job with progress updates visible to the customer | P0 | Implemented — job queue with status tracking |
| FR-4.10 | Provider-agnostic AI layer: can switch between Claude, GPT-4o, Ideogram, DALL-E without code changes | P0 | Implemented — AIService protocol with factory |

### FR-5: Website Generation

| ID | Requirement | Priority | Status |
|---|---|---|---|
| FR-5.1 | System generates a multi-page website from business facts and brand outputs (home, about, services, contact) | P0 | Implemented — Website Agent with template rendering |
| FR-5.2 | Generated website uses the customer's brand colors, fonts, logo, and copy | P0 | Implemented — brand inputs feed site spec |
| FR-5.3 | Website content is grounded in customer facts; no invented awards, testimonials, or service claims | P0 | Implemented in prompt constraints |
| FR-5.4 | System deploys the website to a real URL (Vercel subdomain) and reports the actual deployment status | P0 | Implemented — Vercel deployer in Website Agent |
| FR-5.5 | Customer can see their live website URL only after deployment succeeds; never a broken or pending link shown as "live" | P0 | Implemented — status state machine |
| FR-5.6 | Website job survives worker restart and Redis outage; stale jobs are recovered | P0 | Implemented — PostgreSQL job state with recovery |
| FR-5.7 | Customer can retry a failed website generation | P0 | Implemented — retry API |
| FR-5.8 | Quality checks on generated website: mobile responsive, valid HTML, no placeholder text, brand consistency | P1 | Partial — quality checker exists in Website Agent |
| FR-5.9 | Custom domain support (customer brings their own domain) | P2 | Not started |

### FR-6: Review and Approval

| ID | Requirement | Priority | Status |
|---|---|---|---|
| FR-6.1 | Every AI-generated brand package enters a review queue before customer delivery | P0 | Implemented — review creation on brand generation |
| FR-6.2 | Admin/designer can list, filter, claim, and review pending brand packages | P0 | Implemented — review endpoints |
| FR-6.3 | Reviewer can approve, request revisions (with notes), or reject a brand package | P0 | Implemented — approve/revise/reject endpoints |
| FR-6.4 | Approval triggers asset rendering and delivery pipeline | P0 | Implemented — enqueue_asset_render on approve |
| FR-6.5 | Review state transitions are persisted with timestamps and reviewer identity | P0 | Implemented — review model with audit fields |
| FR-6.6 | Real-time admin notifications via SSE when new reviews arrive or status changes | P1 | Implemented — admin events endpoint |
| FR-6.7 | Admin dashboard UI with review queue, detail view, and action buttons | P0 | Not started — admin app is scaffold only |
| FR-6.8 | Customer sees review status in their workspace (under review / approved / revision requested) | P1 | Partial — status model exists, UI not verified |

### FR-7: Billing and Payment

| ID | Requirement | Priority | Status |
|---|---|---|---|
| FR-7.1 | Customer can select a package tier and pay in Naira via Paystack | P0 | Implemented — billing initialize/verify |
| FR-7.2 | Payment confirmation via Paystack webhook (idempotent, handles duplicates and replay) | P0 | Implemented — webhook handler |
| FR-7.3 | Order and credit ledger: track what was paid, what was consumed, and current balance | P0 | Implemented — credit model with ledger |
| FR-7.4 | Brand generation requires a paid order; return 402 if unpaid | P0 | Implemented — payment gate on generate endpoint |
| FR-7.5 | Package tiers with clear pricing: Brand Starter, Brand+Web, Brand Complete | P0 | Partial — needs pricing configuration |
| FR-7.6 | Payment receipt sent via email | P1 | Partial — email service exists, receipt template not verified |
| FR-7.7 | Refund handling: process and record refunds, update credit balance | P1 | Not started |
| FR-7.8 | Business ownership enforced on all billing routes (customer can only pay for their own business) | P0 | Partial — needs verification |

### FR-8: Asset Delivery

| ID | Requirement | Priority | Status |
|---|---|---|---|
| FR-8.1 | Render approved brand into deliverable files: logo variants (SVG, PNG at multiple sizes), guidelines PDF, complete ZIP | P0 | Implemented — asset rendering service |
| FR-8.2 | Upload rendered assets to object storage with organized paths per business/brand | P0 | Implemented — R2 storage with path convention |
| FR-8.3 | Customer can download assets via time-limited signed URLs | P0 | Implemented — signed link generation |
| FR-8.4 | Delivery email with download links sent to customer | P0 | Implemented — delivery service with Resend |
| FR-8.5 | Assets remain available in customer workspace for re-download | P1 | Partial — asset listing endpoint exists |
| FR-8.6 | Asset rendering handles failures and retries without duplicate delivery | P0 | Partial — job retry exists, idempotency not verified |

### FR-9: Waitlist to Launch Transition

| ID | Requirement | Priority | Status |
|---|---|---|---|
| FR-9.1 | Waitlist subscribers are notified when the product launches | P1 | Not started |
| FR-9.2 | Early waitlist members receive priority access or a discount code | P2 | Not started |
| FR-9.3 | Waitlist data feeds into analytics to understand demand | P1 | Not started |

---

## Part 2 — Non-Functional Requirements

Non-functional requirements define quality attributes. These are what separate a demo from a product customers trust and recommend.

### NFR-1: Performance

| ID | Requirement | Priority | Metric |
|---|---|---|---|
| NFR-1.1 | Marketing site First Contentful Paint < 2s on 4G, < 4s on 3G | P0 | Lighthouse score ≥ 80 on mobile |
| NFR-1.2 | API response time < 500ms for authenticated requests (p95) | P0 | Measured at API gateway |
| NFR-1.3 | Chat first token latency < 2s from message send | P0 | Measured at WebSocket |
| NFR-1.4 | Brand generation completes within 3 minutes for a standard package | P0 | Measured end-to-end |
| NFR-1.5 | Website generation and deployment within 5 minutes | P0 | Measured from job enqueue to live URL |
| NFR-1.6 | Asset rendering (logos + PDF + ZIP) within 2 minutes after approval | P1 | Measured from approve to download-ready |

### NFR-2: Reliability

| ID | Requirement | Priority | Metric |
|---|---|---|---|
| NFR-2.1 | API uptime ≥ 99.5% (≤ 3.6 hours downtime/month) | P0 | Health check monitoring |
| NFR-2.2 | No data loss on worker crash or restart; all jobs are recoverable from PostgreSQL | P0 | Tested with kill-and-restart |
| NFR-2.3 | Webhook processing is idempotent: duplicate Paystack callbacks do not create duplicate orders or credits | P0 | Tested with repeated webhook delivery |
| NFR-2.4 | Chat reconnection: customer resumes within 30 seconds without losing context or messages | P0 | Tested with WebSocket disconnect |
| NFR-2.5 | Database backups every 6 hours with tested restore procedure | P0 | Backup verification log |
| NFR-2.6 | Graceful degradation: if AI provider is down, customer sees a clear message, not a 500 error | P0 | Tested with provider timeout |

### NFR-3: Security

| ID | Requirement | Priority | Metric |
|---|---|---|---|
| NFR-3.1 | All traffic over HTTPS; no mixed content | P0 | SSL certificate valid |
| NFR-3.2 | JWT tokens expire within 24 hours; refresh tokens rotate | P0 | Token configuration |
| NFR-3.3 | No API keys, secrets, or credentials in client-side code or git history | P0 | Secret scan passing |
| NFR-3.4 | CORS restricted to known frontend origins only | P0 | Implemented — configurable CORS |
| NFR-3.5 | Input validation on all API endpoints (Pydantic models) | P0 | Implemented |
| NFR-3.6 | Rate limiting: 60 requests/minute per user on API, 10 messages/minute on chat | P0 | Not implemented |
| NFR-3.7 | SQL injection protection via parameterized queries (SQLAlchemy ORM) | P0 | Implemented by framework |
| NFR-3.8 | XSS protection in rendered website content and brand copy | P0 | Template escaping required |
| NFR-3.9 | Signed, time-limited asset download URLs (not guessable permanent links) | P0 | Implemented |
| NFR-3.10 | Admin endpoints require role-based authentication; no public access | P0 | Implemented |

### NFR-4: Scalability

| ID | Requirement | Priority | Metric |
|---|---|---|---|
| NFR-4.1 | Support 100 concurrent users without degradation | P0 | Load test baseline |
| NFR-4.2 | Support 50 concurrent brand generations without queue starvation | P1 | Worker pool sizing |
| NFR-4.3 | Database connection pooling with bounded pool size | P0 | Async SQLAlchemy pool |
| NFR-4.4 | Stateless API: horizontal scaling by adding containers | P1 | No server-side session storage |
| NFR-4.5 | Object storage (R2/S3) for assets, not local filesystem | P0 | Implemented |

### NFR-5: Usability

| ID | Requirement | Priority | Metric |
|---|---|---|---|
| NFR-5.1 | Mobile-first responsive design: all customer flows work on a phone screen | P0 | Tested at 375px width |
| NFR-5.2 | Keyboard-accessible: all interactive elements reachable without a mouse | P1 | WCAG 2.1 AA |
| NFR-5.3 | Readable contrast ratios on all text (≥ 4.5:1 for body text) | P0 | Automated contrast check |
| NFR-5.4 | Clear loading states: skeleton screens during data fetch, progress indicator during generation | P0 | Visual verification |
| NFR-5.5 | Error messages are human-readable and actionable, not stack traces or codes | P0 | All error responses audited |
| NFR-5.6 | Works on Chrome, Safari, Firefox (last 2 major versions) and Samsung Internet | P0 | Cross-browser test |
| NFR-5.7 | Respects prefers-reduced-motion for animations | P1 | CSS media query check |
| NFR-5.8 | Page titles and navigation distinguish each section for screen readers | P1 | Accessibility audit |

### NFR-6: AI Output Quality

| ID | Requirement | Priority | Metric |
|---|---|---|---|
| NFR-6.1 | Brand outputs are grounded in customer facts; no invented history, awards, testimonials, or services | P0 | Prompt evaluation harness |
| NFR-6.2 | Generated taglines are unique (not generic "Innovating the future" style) | P0 | Genericity check in validator |
| NFR-6.3 | Color palettes pass WCAG AA contrast for text on background combinations | P0 | Automated contrast validation |
| NFR-6.4 | Selected fonts are verified available on Google Fonts before delivery | P0 | Font availability check |
| NFR-6.5 | Logo concepts are visually distinct from each other (3 different styles, not 3 color variants) | P0 | Prompt design + manual review |
| NFR-6.6 | Website copy does not contain placeholder text ("Lorem ipsum", "[Company Name]", "Coming soon") | P0 | Quality checker in Website Agent |
| NFR-6.7 | AI-generated content is labeled as AI-generated in metadata or customer-facing disclosure | P1 | Disclosure policy |
| NFR-6.8 | Prompt evaluation: ≥ 80% of test business descriptions produce passing-quality output | P0 | Batch evaluation harness |

### NFR-7: Observability and Operations

| ID | Requirement | Priority | Metric |
|---|---|---|---|
| NFR-7.1 | Structured logging with request IDs correlated across API, worker, and agents | P0 | Implemented — structlog |
| NFR-7.2 | Health and readiness endpoints on every service | P0 | Implemented — /health |
| NFR-7.3 | Error alerting: team is notified within 5 minutes of a 5xx spike or job failure spike | P0 | Alert configuration required |
| NFR-7.4 | Cost tracking: model inference, image generation, storage, and hosting costs per customer workflow | P1 | Logging instrumentation |
| NFR-7.5 | Job queue monitoring: visible queue depth, processing time, failure rate | P0 | Redis/worker metrics |
| NFR-7.6 | Database migration is automated and reversible; rollback tested | P0 | Alembic downgrade tested |

### NFR-8: Legal and Compliance

| ID | Requirement | Priority | Metric |
|---|---|---|---|
| NFR-8.1 | Terms of service and privacy policy published before accepting payments | P0 | Not started |
| NFR-8.2 | NDPR (Nigeria Data Protection Regulation) compliance: consent collection, data processing records, right to deletion | P0 | Not started |
| NFR-8.3 | AI disclosure: customers informed that brand outputs are AI-generated and require their review | P0 | Not started |
| NFR-8.4 | Asset/IP ownership terms: customer owns delivered brand assets; Cre8ive District retains no exclusive rights | P0 | Not started |
| NFR-8.5 | Payment terms, refund policy, and dispute resolution process documented | P0 | Not started |
| NFR-8.6 | Cookie consent for marketing site analytics | P1 | Not started |
| NFR-8.7 | Data retention and deletion policy: how long data is kept, when it is purged, how deletion requests are handled | P0 | Not started |

### NFR-9: Deployment and DevOps

| ID | Requirement | Priority | Metric |
|---|---|---|---|
| NFR-9.1 | CI pipeline: lint, typecheck, and test on every push for all services | P0 | Partial — API has GitHub Actions |
| NFR-9.2 | Staging environment that mirrors production | P0 | Not configured |
| NFR-9.3 | Zero-downtime deployment: rolling updates or blue-green | P1 | Deployment strategy required |
| NFR-9.4 | Secrets managed via environment variables or managed secrets service; not in code | P0 | Implemented — Pydantic Settings |
| NFR-9.5 | Rollback procedure: revert to previous working version within 15 minutes | P0 | Not documented |
| NFR-9.6 | Infrastructure as code: reproducible environment setup | P1 | Docker Compose for local; production IaC not started |

---

## Part 3 — Foundable Feature Parity Map

What Foundable does that Cre8ive District needs for competitive parity at MVP.

| Foundable feature | Cre8ive District equivalent | MVP? | Status |
|---|---|---|---|
| AI chat intake (Ted) | Abija chat with Nigerian personality | Yes | Implemented |
| Brand strategy generation | Brand strategy from brief | Yes | Implemented |
| Logo concepts (3 options) | 3 logo concepts via Ideogram/DALL-E | Yes | Implemented |
| Color palette | WCAG-validated palette | Yes | Implemented |
| Typography selection | Google Fonts curated pairs | Yes | Implemented |
| Brand guidelines PDF | PDF generation in asset pipeline | Yes | Implemented |
| Website generation | Multi-page site via Website Agent | Yes | Implemented |
| Website deployment | Vercel subdomain deployment | Yes | Implemented |
| Stripe payment | Paystack (Naira) payment | Yes | Implemented |
| Email magic link auth | Resend magic link + Google OAuth | Yes | Partial |
| Real-time generation progress | Job status + SSE events | Yes | Implemented |
| Asset download (ZIP) | ZIP bundle with signed URLs | Yes | Implemented |
| Custom domain | Customer-provided domain mapping | No | Deferred |
| Social media templates | Social graphics and templates | No | Deferred |
| Brand refresh / iteration | Revision workflow | Yes | Partial |
| Team collaboration | Multi-seat workspace | No | Deferred |
| Blog/SEO content | Website includes blog template | No | Deferred |
| Analytics dashboard | Site analytics for customer | No | Deferred |

---

## Part 4 — Priority Summary

### P0: Launch blockers (must have for first paying customer)

**Functional (22 items):**
FR-1.1, FR-1.3, FR-2.1, FR-2.2, FR-2.3, FR-2.4, FR-2.5, FR-2.7, FR-3.1 through FR-3.6, FR-3.8, FR-3.9, FR-4.1 through FR-4.10, FR-5.1 through FR-5.7, FR-6.1 through FR-6.5, FR-6.7, FR-7.1 through FR-7.5, FR-7.8, FR-8.1 through FR-8.4, FR-8.6

**Non-Functional (27 items):**
NFR-1.1 through NFR-1.5, NFR-2.1 through NFR-2.6, NFR-3.1 through NFR-3.10, NFR-4.1, NFR-4.3, NFR-4.5, NFR-5.1, NFR-5.3 through NFR-5.6, NFR-6.1 through NFR-6.6, NFR-6.8, NFR-7.1 through NFR-7.3, NFR-7.5, NFR-7.6, NFR-8.1 through NFR-8.5, NFR-8.7, NFR-9.1, NFR-9.2, NFR-9.4, NFR-9.5

### What is actually blocking launch right now

Based on current code state, these are the gaps between "code exists" and "first customer can pay and receive":

1. **Auth flow broken** — NextAuth adapter error prevents sign-up/sign-in
2. **Admin review UI missing** — admin app is a scaffold; no way for designers to review
3. **End-to-end flow unverified** — no evidence of complete journey from sign-up to delivery
4. **Legal documents missing** — no terms, privacy policy, AI disclosure, or IP terms
5. **Rate limiting missing** — API is unprotected against abuse
6. **Staging environment missing** — no way to test before production
7. **Package pricing not configured** — tiers defined in docs but not in database/UI
8. **Error alerting not configured** — team has no visibility into production failures
9. **Cross-browser and mobile testing not done** — responsive behavior unverified
10. **AI output quality not batch-tested** — evaluation harness exists but no results recorded

### Estimated effort to close P0 gaps

| Gap | Effort | Owner |
|---|---|---|
| Fix auth flow (NextAuth adapter + Resend) | 2-3 days | Frontend + Backend |
| Admin review dashboard | 3-4 days | Frontend |
| End-to-end verification | 2-3 days | QA / All |
| Legal documents | 3-5 days | Founder + Legal |
| Rate limiting middleware | 1 day | Backend |
| Staging environment | 2-3 days | DevOps |
| Package pricing in DB + UI | 1-2 days | Backend + Frontend |
| Alerting setup | 1 day | DevOps |
| Mobile + cross-browser test | 2 days | Frontend + QA |
| AI quality evaluation batch run | 1-2 days | AI Engineer |
| **Total** | **~18-26 working days** | **Full team** |

---

## Document ownership

This document is the canonical MVP requirements reference. Update it when requirements change, are completed, or are re-prioritized. Implementation evidence belongs in [PROJECT_EXECUTION.md](PROJECT_EXECUTION.md). Durable product decisions belong in [PROJECT_BLUEPRINT.md](PROJECT_BLUEPRINT.md).
