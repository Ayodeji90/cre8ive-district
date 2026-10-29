# Website Engineering Research and Requirements

**Workstream:** 1 — Software engineering and architecture  
**Prepared:** 29 October 2026  
**Status:** First-principles proposal for founder/product-owner review  
**Market:** Nigeria-based studio serving Nigerian and international businesses  
**Research boundary:** Product and engineering requirements; not a review limited to the existing static prototype. Public law/platform material is linked for verification, not as legal advice.

## 1. Executive recommendation

Build a **static-first, server-rendered marketing website** with a reliable, consent-aware project enquiry path. At launch, do not build a bespoke application, user accounts, proposal system, or custom CRM. Use a trusted hosted form/CRM service, or a small serverless submission endpoint that forwards to an approved CRM and monitored business inbox. In either case the vendor/function is the backend: a static page plus a form service is not a system with no backend at all.

The website itself is a high-value portfolio item: it must demonstrate brand strategy, responsive information architecture, visual craft, accessibility, performance, copy, and conversion design. The lead form must reliably reach the studio; a visitor should not have to draft a long WhatsApp message and remember to send it before an enquiry exists.

Recommended initial architecture:

```text
Prospect browser
  ├─ pre-rendered site pages and optimized portfolio media (CDN)
  └─ HTTPS project form
       └─ hosted form/CRM intake OR small serverless POST endpoint
            ├─ create lead in approved CRM/lead store
            ├─ send acknowledgement to prospect (optional, only after successful intake)
            └─ notify monitored studio inbox/owner

Direct WhatsApp and email remain visible alternatives.
```

Use static HTML or a small static-site generator (SSG) for the public pages. Choose framework based on the team’s actual ability to maintain it; no single framework is a product requirement. Keep project content in structured files initially. Add a non-technical CMS when the founder needs to publish or update case studies and content without a developer. A Vercel Function is a valid later or minimal server-side endpoint, but it does not by itself provide durable lead storage, a CRM, or an email service. Vercel documents Functions as server-side request handlers that can connect to APIs and databases and are deployed alongside static/app code ([Vercel Functions](https://vercel.com/docs/functions), reviewed 29 Oct 2026).

### Why capture form submissions

The goal is qualified business enquiries. A form that only composes a WhatsApp URL can lose the prospect if the popup is blocked or the person closes the draft; it also does not create a reliable lead record. Treat direct WhatsApp/email as alternative routes, and make the primary form submission a real acknowledged intake. If the founder deliberately chooses a zero-backend temporary launch, label the WhatsApp handoff plainly and accept that submission tracking and delivery reliability are weaker.

## 2. Product boundary and user journeys

### Website outcomes

1. A suitable prospect in Nigeria or another market understands the studio’s brand-led offer and how the team can help.
2. The visitor can assess fit through actual work, clearly labelled concepts, process, and service scope.
3. The visitor can make an enquiry through a dependable route and know whether it was received.
4. The founder can update core facts, services, and proof without creating duplicate or conflicting content.
5. The site provides a credible example of Cre8ive District’s web design/build capability.

### Main journeys

- **New-business founder:** referral/social/search → home → Brand Strategy/Identity and process → relevant concept/case study → enquiry → studio qualification → discovery.
- **Existing business seeking more visibility:** search/referral → service/case study → understands brand-to-website/campaign relationship → enquiry with current challenge and desired change.
- **International prospect:** social/search/referral → proof and process → understands Nigeria base and remote working model, contact expectations and next step → enquiry → response in an agreed time zone.
- **Direct-contact visitor:** any page → direct WhatsApp/email. Site records no lead until the studio manually logs that contact.
- **Studio editor:** approved copy/proof → edit structured content/CMS → preview → accessibility/content/link review → production publish → verify pages and form.

### Out of scope for launch

Client login/portal, online payments, booking calendar, quote calculator, proposal generation, e-commerce, client file upload, blog comments, multi-language localization, autonomous chat/AI, CRM replacement, and custom software/hardware delivery. These require separate product, privacy, security, support, and business cases.

## 3. Functional requirements

Priority key: **M** = launch blocker; **S** = strong follow-up; **L** = later, only after evidence. Acceptance criteria describe observable results; they are not claims that the current implementation has been verified.

### Information architecture and content

| ID | Priority | Requirement | Acceptance criteria |
|---|---:|---|---|
| WEB-F01 | M | Publish canonical Home, Services, About, Contact, and selected Work/Case Study destinations. | Every canonical page loads from direct URL and internal links; nav/footer use one consistent route per page. |
| WEB-F02 | M | Describe the studio as Nigeria-based and open to international clients without suggesting service coverage or proof that is not confirmed. | Copy clearly states the base and approved service arrangements; audience, service claims, and contact expectations are founder-approved. |
| WEB-F03 | M | Present the lead offer, customer fit, work scope boundaries, engagement process, and one primary CTA. | A visitor can identify the intended client situation, what happens next, and how to enquire without inferring guaranteed outcomes. |
| WEB-F04 | M | Show authentic evidence of work. Support client case studies and separately labelled studio concepts. | Every project has a verified owner/source, permission status, public-use approval, role/scope description, and approved claims; concept work is unmistakably labelled. |
| WEB-F05 | M | Model case study content with problem/context, objective, scope/role, process/decisions, selected applications, outcome only when evidenced, and CTA. | A case page can omit confidential or unapproved facts while remaining useful; the editor can distinguish client work from concept work. |
| WEB-F06 | M | State practical remote collaboration details for international clients as they are confirmed. | About/contact or process page answers how discovery, reviews, time zones, files, payment, and handoff work; no assumed country/payment promises. |
| WEB-F07 | S | Add a resource/insights section only if the studio can sustain original, useful publishing. | Each published item has a named reviewer, date/refresh owner, and audience purpose; no auto-generated SEO filler. |

### Contact and lead handling

| ID | Priority | Requirement | Acceptance criteria |
|---|---:|---|---|
| WEB-F08 | M | Offer a primary enquiry form and visible direct WhatsApp and email alternatives. | Form and alternatives work on phone and desktop; exact contact details are verified and monitored. |
| WEB-F09 | M | Ask for only qualification information needed for a first response: name, email, business, service interest, desired outcome/context, timing, and optional budget range. | Each field has a label, required status is clear, optional fields are not coerced, and no sensitive personal/customer data or attachments are requested. |
| WEB-F10 | M | Validate input in browser and again at the receiving service/API. Normalize and encode safely; do not treat user input as markup or code. | Invalid/incomplete requests receive specific accessible feedback; server/provider rejects malformed or overlong values; no executable content is rendered. |
| WEB-F11 | M | Persist accepted enquiries in an approved lead system or CRM and notify a named, monitored owner. | Successful submit returns a truthful confirmation only after intake succeeds; a test lead is visible to the owner; failed intake shows a retry/direct-contact path. |
| WEB-F12 | M | Reduce spam and abuse without blocking legitimate prospects. | Intake has provider anti-spam or proportionate rate limits, honeypot/abuse controls as appropriate, and a monitored procedure for false positives. Do not rely only on client-side checks. |
| WEB-F13 | M | Preserve the lead source where known (UTM/referral page) without collecting unnecessary identity or behavioral data. | CRM captures source fields with documented definitions; missing source is allowed; source data is not placed into public page content. |
| WEB-F14 | M | Tell prospects what happens to their enquiry and where it is sent; link a suitable privacy notice. | Notice names purpose, data categories, recipient/vendor categories, contact route for privacy requests, and retention approach after legal review. |
| WEB-F15 | S | Send an acknowledgement to the prospect after successful acceptance. | Email is triggered only on successful intake; copy states next steps without promising an unapproved response time. |
| WEB-F16 | S | Provide a manual export/delete path from the lead system with access restricted to authorized staff. | Owner can retrieve, correct, close, and delete/retain according to approved policy; deletion expectations include vendor copies/backups where supported. |
| WEB-F17 | L | Connect lead intake to a CRM workflow, assignment rules, and project management when manual operations show a bottleneck. | Integration has an owner, failure alert, retry/deduplication behavior, and documented fields; no duplicate lead is silently lost. |

### Content operations, international readiness, and search

| ID | Priority | Requirement | Acceptance criteria |
|---|---:|---|---|
| WEB-F18 | M | Keep structured site content separate from layout and reusable components. | Services, proof, contact data, metadata, and navigation have one authoritative source or clearly controlled page source; duplicate route variants are removed/redirected. |
| WEB-F19 | M | Provide preview/review before public content changes. | Every publishing route includes a human review of facts, rights, links, image alt text, metadata, and mobile presentation. |
| WEB-F20 | M | Support English-language copy and international contact in phase one; defer translation until priority markets and translation owner are selected. | No hard-coded assumption that visitors use WAT or NGN in future contact flows; currency/time-zone instructions are explicit where shown. |
| WEB-F21 | S | Support additional localized content only when a target language/region and professional review are available. | Each translation has a canonical/locale URL plan and accurate `hreflang` only for actual equivalent localized pages. |
| WEB-F22 | M | Provide descriptive page titles, unique meta descriptions, indexable HTML content, canonical URLs, sitemap, robots policy, and redirects. | Search crawlers see primary content without requiring app-only rendering; sitemap contains only intended canonical URLs; legacy/case variants redirect to one destination. |
| WEB-F23 | S | Add verified Organization structured data, social sharing metadata/image, and favicon. | Markup matches publicly visible, approved business information; no invented addresses, client reviews, or LocalBusiness facts. Google says Organization structured data can clarify organization details, and does not guarantee a rich result ([Google Organization data](https://developers.google.com/search/docs/appearance/structured-data/organization), reviewed 29 Oct 2026). |
| WEB-F24 | S | Connect Search Console and measure search visibility. | A business-owned account has named access/ownership and a process for reviewing indexing or manual issues. |

## 4. Non-functional requirements

| ID | Priority | Requirement | Acceptance criteria / target |
|---|---:|---|---|
| WEB-N01 | M | Responsive across small phones, tablets, laptops, and large displays. | No horizontal scroll, overlapping controls, clipped text, or unreachable primary actions at agreed viewport sizes and zoom. |
| WEB-N02 | M | Target WCAG 2.2 AA for public pages and form. | Keyboard-only and screen-reader review; semantic landmarks/headings; visible focus; accessible names/status/errors; contrast; reflow; target sizes; focus not obscured; captions for meaningful video. WCAG 2.2 is a W3C Recommendation and adds criteria including focus visibility/not obscured and target size ([W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/), reviewed 29 Oct 2026). |
| WEB-N03 | M | Respect reduced-motion preference; animation is nonessential. | All required content/action remains available with motion disabled; no content waits for reveal animation; no hover-only information. |
| WEB-N04 | M | Deliver fast, stable pages on mobile networks. | Measure field Core Web Vitals when enough traffic exists: at 75th percentile, LCP ≤2.5 s, INP ≤200 ms, CLS ≤0.1. Use compressed/responsive images, reserved media space, limited third-party JS, and font fallbacks. These are Google’s current “good” CWV thresholds ([web.dev Core Web Vitals](https://web.dev/articles/vitals), reviewed 29 Oct 2026). |
| WEB-N05 | M | Core content works if decorative JavaScript, analytics, or external fonts fail. | Static HTML renders key message, services, proof, navigation links, and contact routes; form failure gives an accessible fallback. |
| WEB-N06 | M | Protect lead data and site administration. | HTTPS; secrets only in server-side environment storage; least-privilege owner/editor roles; MFA for hosting, domain, CMS, and CRM; dependency updates; backups/export; no credentials or form PII in source control or client logs. |
| WEB-N07 | M | Respect privacy and data minimization across Nigeria and prospect locations. | Document purpose, lawful basis, vendors, storage region, access, retention, data-subject request path, and breach handling before collecting leads. Nigeria’s NDPC says the NDP Act scope includes organizations operating in Nigeria and processing of Nigerian data, and discusses adequacy/other conditions for cross-border personal-data transfers ([NDPC FAQ](https://ndpc.gov.ng/faqs/), reviewed 29 Oct 2026). Obtain qualified advice on applicability and implementation. |
| WEB-N08 | M | Determine whether other target-market privacy regimes apply. | Before intentionally marketing to people in the EU/UK or collecting analytics/cookies from them, review applicable rules with qualified counsel. EDPB guidance describes GDPR territorial scope where non-EU organizations intentionally offer services to people in the Union or monitor behavior; a general accessible website alone does not settle applicability ([EDPB territorial-scope guidance](https://www.edpb.europa.eu/sites/default/files/files/file1/edpb_guidelines_3_2018_territorial_scope_after_public_consultation_en_1.pdf), reviewed 29 Oct 2026). |
| WEB-N09 | M | Provide lead-intake reliability and clear operational ownership. | Define receiving provider SLA/support, notification owner and backup, and fallback if service fails; daily/weekly monitoring matches expected volume. No silent “success” if the record was not accepted. |
| WEB-N10 | M | Maintainable by a small team. | Document local setup, content model, deployment/revert, environment variable owners, vendor access, and change process; avoid unnecessary backend services and dependencies. |
| WEB-N11 | M | Separate preview, production, and any test data. | Preview deploys do not send real prospects into live notification/CRM unless intentionally configured; credentials are environment-specific; production data is not copied into test. |
| WEB-N12 | S | Provide privacy-conscious measurement. | Start with aggregate Search Console and CRM attribution; add analytics only after data purpose, consent/notice, retention, access, and vendor terms have been reviewed. Do not add ad pixels by default. |
| WEB-N13 | S | Establish search and social sharing preview quality. | Unique title/description and share image for core pages; images are meaningful, optimized, and have suitable alternatives; URLs are stable and readable. |
| WEB-N14 | S | Define service availability and response expectations. | Publish operating hours/response target only after owner coverage and backup are assigned; no implied 24/7 coverage. |

Security requirements should be reviewed against OWASP ASVS as the site adds custom server-side code; OWASP describes ASVS as a framework for designing, developing, and verifying web application security ([OWASP ASVS 5.0](https://asvs.owasp.org/), reviewed 29 Oct 2026). For a no-code hosted form, review the provider’s security, privacy, access, and retention controls instead of assuming its product name guarantees compliance.

## 5. Backend decision and options

| Option | What it includes | Benefits | Costs/risks | Recommendation |
|---|---|---|---|---|
| **A. Static pages + WhatsApp/email links only** | No project form storage, API, CRM, or lead database | Lowest build and maintenance burden; simple, fast public site | A drafted message is not received until sent; blocked popup/closed draft loses lead; manual source attribution; no receipt acknowledgement; structured enquiry data can be exposed in WhatsApp URL query parameters | Temporary fallback only if the no-storage decision is explicit. Avoid asking for confidential details in a wa.me prefill. |
| **B. Static/SSG site + hosted form/CRM** | Form is handled by a managed provider; provider stores/forwards lead and can send notifications | Fastest reliable capture without operating a custom backend; allows site to remain mostly static | Vendor processes personal data; recurring cost, lock-in, vendor outage, region/retention terms; embeds/scripts may affect speed/privacy/accessibility | **Recommended launch path** if vendor review and pricing are acceptable. Prefer a styled form or server-to-server integration over a heavy third-party embed. |
| **C. Static/SSG + serverless POST endpoint + CRM** | Small serverless function validates, rate-limits, and calls CRM/email APIs; durable lead record remains in CRM | Strong branded experience and control of routing, dedupe, validation, telemetry; little server management | Must operate secrets, abuse controls, retries, monitoring, schema evolution, vendor contracts, and failures; a function is not itself a database/CRM | Good if founder needs a bespoke form and there is a named technical owner. Do not add a custom database unless the CRM cannot meet requirements. |
| **D. Full dynamic application/backend/CMS** | App database, CMS, accounts, workflows, admin, service APIs | Supports authenticated portal, complex workflows, products, or frequent content operations | Highest build/security/support burden and privacy surface; distracts from launch unless requirements prove need | Later only for validated product needs; separate architecture and business case. |

### Recommended MVP data flow

1. Browser sends a TLS-protected form POST to a reputable form/CRM provider or project endpoint.
2. Endpoint validates types, lengths, allowed options, origin/CSRF strategy where relevant, rate limits, and anti-spam signals. Browser validation is convenience only.
3. Accepted request is written to one system of record (CRM or tightly controlled lead store); generate stable lead ID and deduplicate where practical.
4. Notify the designated team inbox and owner. Notification contains only the minimum needed; CRM is the authoritative record.
5. Return success only after durable acceptance. Return error/retry and direct contact options on failure. Use idempotency or duplicate detection so a retry does not create multiple leads.
6. Retain only while needed under a founder-approved policy; restrict access and support correction/deletion requests.

Do not send contact data to the CRM in GET query strings, analytics events, or page URLs. The current prototype’s form-to-WhatsApp pattern requires a message in a URL query; if retained as an optional fallback, limit fields and warn users not to put sensitive or confidential information there. The primary form should use POST over HTTPS.

### CMS decision

At launch, core pages and a small number of case studies can be structured in Markdown/JSON/content files in version control with preview deployments. This keeps source ownership and avoids CMS costs. If a non-technical founder needs to publish case studies regularly, add a managed headless CMS with draft/preview, roles, version history, export, image handling, and structured fields. Do not build a custom CMS. A CMS is a content editing backend, not a lead database; evaluate each separately.

## 6. Data and privacy requirements

### Minimum data schema

- `lead_id` (system-generated)
- `received_at_utc`
- `name`, `email`
- `business_name` (optional)
- `service_interest` (controlled values plus “other/not sure”)
- `project_context` (optional, length-limited free text)
- `timeframe` and `budget_band` (optional; only if founders use them for qualification)
- `source/referrer/campaign` (optional, no fingerprinting)
- `consent/notice_version` where consent is the selected lawful basis and legally needed
- `status`, `owner`, `next_action_due`, `closed_reason` (internal CRM data)

Avoid collecting private client/customer records, health/financial/sensitive data, passwords, attachments, or a detailed confidential strategy in the first-contact form. Ask for deeper data only after a suitable agreement and secure channel.

### Privacy operations before launch

- Identify who is controller/processor for site lead data and which vendors process it.
- Determine lawful basis and give transparent notice for each use (replying, qualification, optional marketing); don't bundle marketing subscription into an enquiry.
- Approve retention periods, deletion process, authorized users, vendor access, and data-subject request owner.
- Review data location, cross-border transfers, subprocessors, breach notification obligations, and vendor agreements with a qualified Nigeria privacy professional. Review prospect-target-market regimes separately. The NDPA and cross-border rules need legal interpretation against the actual vendor/service chain.
- If analytics, cookies, ad pixels, session replay, or embedded social widgets are introduced, document their data flows and decide notice/consent controls before deployment.

## 7. Website content model and editorial roles

### Minimum content entities

- **Service:** name, customer fit, problem, outcome, included work examples, exclusions, CTA, approval date.
- **Case study/concept:** title, client/concept type, permission status, sector (if approved), challenge, role/scope, decisions/process, media with alt text, results with evidence/approval, related services.
- **Testimonial:** exact approved text, person/title/business attribution, permission/evidence, date, source URL or record.
- **Page metadata:** canonical URL, title, description, social image, index/noindex policy, update owner.
- **Contact settings:** email, WhatsApp, service area, response owner/hours, privacy notice version; secret values remain in host/provider settings, not reusable public source if not intended public.

### Roles

- Founder/product owner approves positioning, claims, services, prices, proof permissions, international promises, and privacy notices.
- Content editor drafts/publishes updates and maintains media/alt text.
- Developer controls template, form integration, security, deploy access, rollback, and technical monitoring.
- Privacy/legal adviser reviews lawful basis, contracts/vendor transfers, retention, and jurisdictional obligations when needed.

In a small launch, one person can hold multiple roles, but approvals and ownership remain explicit.

## 8. Search, conversion, and international requirements

- Put core service and proof copy in crawlable HTML, not only canvas or client-side rendered content.
- One canonical URL per page; permanent server-side redirects for aliases and old case variants. Include only canonical URLs in sitemap. Google's guidance identifies redirects as a strong canonicalization signal and sitemaps as a weaker signal ([Google duplicate URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls), reviewed 29 Oct 2026).
- Use page-specific titles/descriptions, descriptive internal links, accurate image text alternatives, Search Console, and original people-first content. Google's guidance cautions against producing search-engine-first content ([Google helpful content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content), reviewed 29 Oct 2026).
- Use Organization JSON-LD for accurate organization facts where useful. Only use LocalBusiness markup/listings when the business facts and eligibility support it; Google’s LocalBusiness markup describes local physical businesses and does not establish the business’s eligibility for a Business Profile.
- Social preview images should be designed and generated for known page content, readable on mobile, rights-cleared, and stored with stable absolute URLs.
- Keep launch language English initially; determine future locale based on prospect evidence. Do not display conversion using guessed location. If public fees are later added, show currency and scope clearly; international currency conversion, taxes, and payment rails require founder/accounting approval.
- Store timestamps in UTC; present meeting/contact windows with a named timezone (e.g. WAT, UTC+1) and optionally show conversions when booking exists. Do not promise response deadlines without coverage.

## 9. Deployment and operations

- Domain, DNS, registrar, Vercel/hosting, code repository, CMS, CRM, and email accounts are owned by the business, not a personal contractor account alone; provide named owner and recovery path.
- Use Git-connected preview deployments for review and a controlled production deploy; protect production secrets; prohibit previews from writing to production CRM except an intentionally isolated test workflow.
- Require rollback/revert instructions, backup/export for content and leads, dependency update ownership, and a broken-form escalation route.
- Use uptime/form synthetic checks that do not submit fake leads into sales without isolation. If a provider lacks health checks, assign an owner to periodically verify intake and lead notifications.
- Configure custom domain canonicalization (www/non-www choice), HTTPS, cache policy for static assets, and cache invalidation for content. Keep serverless endpoint in a region appropriate to its CRM/data source and regulatory posture; measure real latency and confirm the chosen vendor’s regional availability. Vercel says Functions run in a configured region and recommends locating functions near their data source ([Vercel Functions](https://vercel.com/docs/functions), reviewed 29 Oct 2026).

## 10. Risks and controls

| Risk | Impact | Control / decision |
|---|---|---|
| Leads disappear in a WhatsApp draft or blocked popup | Lost business and false conversion expectations | Real form intake with success/failure state; direct WhatsApp/email fallback; owner notification |
| Lead data flows to an unreviewed vendor or foreign region | Privacy non-compliance, trust/reputation damage | Data-flow inventory, vendor terms/DPA review, minimization, lawful basis/notice, qualified advice |
| Site says “international” without operational support | Unmet client expectations | Validate country, payments, time zone, contract and delivery readiness; copy exactly what is supported |
| No client portfolio or permission ambiguity | Lower trust or rights dispute | Label concepts; maintain permission register; publish only approved client assets and claims |
| CMS/backend scope grows before offer validation | Cost, maintenance burden, delayed launch | Static-first architecture; explicit later-stage triggers; no accounts/portal in MVP |
| Embedded form/analytics harms speed, accessibility, or privacy | Form abandonment and inaccessible interactions | Prefer first-party styled POST or light integration; no unapproved pixels; audit the full visitor journey |
| Duplicate legacy routes dilute search and confuse users | Route/canonical ambiguity | One canonical route; HTTP redirects; canonical metadata and sitemap alignment |
| Unowned technical accounts or secrets | Loss of site/control or exposure | Business-owned accounts, MFA, least privilege, recovery owner, server-side secret store |

## 11. Phased implementation course

### Phase 0 — Product decisions

Confirm domain, primary audience/offer, approved service claims, proof/permissions, international delivery statement, contact owner/backup, response expectations, privacy owner, form data fields, budget, hosting/domain ownership, vendor approval, and data-retention policy.

### Phase 1 — Launch MVP

1. Finalize sitemap and conversion journeys.
2. Create responsive design system and high-fidelity page designs.
3. Implement pre-rendered pages, case study template, accessible interactions, optimized media, metadata/canonical/sitemap/redirects.
4. Select hosted form/CRM or serverless integration; configure field validation, spam protection, lead persistence, notifications, success/error states, and fallback paths.
5. Publish privacy notice after review; maintain vendor/data-flow record.
6. Manually verify content, keyboard/screen-reader behavior, reduced motion, mobile networks, direct routes, contact, and production delivery before launch.

### Phase 2 — Improve from real lead evidence

Add CRM pipeline automation, source attribution, aggregate analytics, content editor/CMS, translation, richer case studies, or client-facing pricing only where observed operational or sales friction justifies it. Maintain the static/pre-rendered public surface if it remains suitable.

### Phase 3 — Product/portal hypotheses

Only if client work proves repeated demand, scope a portal, booking/payment workflow, interactive tool, AI feature, or custom business software as a separate product. Conduct threat modeling, privacy impact/data-flow analysis, support ownership, unit economics, and architecture review before build.

## 12. Launch acceptance checklist

- [ ] Founder approves positioning, service scope, claims, proof, location and international delivery statements.
- [ ] Primary form creates a durable lead record and alerts the named owner; failure does not imply success.
- [ ] Contact alternatives reach monitored accounts; no confidential data is requested in public form or URL query.
- [ ] Privacy notice, vendor list, retention, data access, and transfer review are approved.
- [ ] Canonical routes and legacy redirects are defined; sitemap and page metadata align.
- [ ] Keyboard, screen-reader, contrast, reflow, reduced-motion, and mobile browser behavior meet WCAG 2.2 AA acceptance goals.
- [ ] Core pages have clear titles, H1s, useful content, image alternatives, and social sharing previews.
- [ ] Page performance has been measured; CWV field targets are tracked when enough real traffic exists.
- [ ] Production owner can deploy/revert, manage domain and vendor accounts, and respond to form/hosting incidents.
- [ ] Content, lead data, and credentials are backed up/exportable and access is restricted.

## 13. Founder decisions required

1. Which enquiry route is primary at launch: hosted form/CRM, a serverless endpoint to an existing CRM, or an intentionally temporary WhatsApp-only flow?
2. Who owns the inbox/CRM and provides backup, and what response time can the team honestly sustain?
3. Which contact fields are needed to qualify leads, and is a budget range useful enough to ask at first contact?
4. Which countries/regions should the launch explicitly say it serves, and what working hours, payments, contracting, and handoff are ready now?
5. How many real client projects and concepts can be shown with permission? Who maintains the permission register?
6. Who should be able to update the website? How often will case studies/service content change? This determines whether repository content is sufficient or a CMS is needed.
7. Which legal entity, privacy contact, and counsel/adviser will approve privacy terms and cross-border data/vendor choices?
8. Is the current domain/host/repository account business-owned, with recovery access and a named deployment owner?
9. What is the affordable monthly ceiling for form/CRM, hosting, email, CMS, and analytics vendors?
10. What accessibility review method and launch sign-off owner will be used?

## 14. Sources

Primary references reviewed 29 October 2026:

- [W3C — WCAG 2.2 Recommendation](https://www.w3.org/TR/WCAG22/)
- [web.dev — Web Vitals and Core Web Vitals thresholds](https://web.dev/articles/vitals)
- [Vercel — Functions](https://vercel.com/docs/functions)
- [OWASP — Application Security Verification Standard](https://asvs.owasp.org/)
- [NDPC — FAQs, including scope and international data transfer](https://ndpc.gov.ng/faqs/)
- [NDPC — Nigeria Data Protection Act 2023](https://ndpc.gov.ng/download/nigeria-data-protection-act-2023)
- [EDPB — Guidelines on GDPR territorial scope](https://www.edpb.europa.eu/sites/default/files/files/file1/edpb_guidelines_3_2018_territorial_scope_after_public_consultation_en_1.pdf)
- [Google Search Central — Helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
- [Google Search Central — Consolidate duplicate URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)
- [Google Search Central — Organization structured data](https://developers.google.com/search/docs/appearance/structured-data/organization)
- [Google Search Central — Build and submit a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)

**Interpretation note:** The recommendations about choosing a hosted form/CRM, static-first rendering, and delaying a custom backend are engineering inferences from the stated small-team/launch goals and the documented capabilities above. They must be revisited if the founder chooses different business, privacy, or operational constraints.

## 15. Reference study: Adis Design and application to Cre8ive District

**Review date:** 29 October 2026. **Reference:** [adisdesign.com](https://www.adisdesign.com/). This is a public-site content and information-architecture review, not a full browser-based audit. The available page view exposes its navigation, copy, links, and project narratives; it does not provide reliable evidence for visual breakpoints, Core Web Vitals, keyboard behavior, screen-reader output, or live form delivery. Treat those items as unverified rather than as findings.

### What is observable

- The home page combines an introductory studio statement, grouped service categories, a short portfolio selection, founder/team story, and direct contact details. The visible service taxonomy covers branding, digital design, presentations, motion, collateral, and print. [Adis home page](https://www.adisdesign.com/)
- The top navigation exposes Design Services, Case Studies, About Us, and Contact Us, with named Strivr, ClearStory Data, and Kaiser Permanente project links. The project stories are separate destinations rather than only an undifferentiated gallery. [Adis home page](https://www.adisdesign.com/)
- Its Strivr story explains project context and scope, then exposes research and process artifacts: information gathering, usability testing, stakeholder interviews, sitemap rebuild, persona collaboration, wireframes, visual iterations, a design review involving product managers and engineering, prototype coverage across product tabs/mobile, and ongoing revision. It describes design decisions and constraints, not only final screens. [Strivr case study](https://www.adisdesign.com/strivr)
- Its Kaiser Permanente story names the user-interface scope and responsibilities, describes sitemap/task-flow work, clickable wireframes, and three rounds of usability tests with 5–8 participants each; it also says interviews and research informed visual decisions. The page identifies the work date as 2014, which helps readers interpret its age. These are claims in the studio's case narrative, not independently verified research records. [Kaiser Permanente case study](https://www.adisdesign.com/kaiserpermanente)
- The About section gives a founder name/qualification, a personal experience claim, an explanation of the studio's name, and a short account of how its team works. The page also publishes email and telephone contact. These are trust cues visible in the content; their effect on conversion is not measured here. [Adis home page](https://www.adisdesign.com/)
- The site identifies Wix-hosted image assets in the rendered page extract. That reveals a platform/content delivery dependency, but does not itself establish performance, accessibility, or engineering quality. No public pricing or enquiry intake workflow was established from the accessible content.

### Principles worth adapting, without copying the visual identity

Keep two kinds of evidence separate. The **homepage** provides the observable information architecture and studio introduction: navigation, service groupings, a three-project selection, founder/team context, and contact details. The crawler's text extraction is sparse and cannot establish whether the visual design is sparse, how sections appear above the fold, or whether the page looks polished. The **case studies** provide the stronger transferable material: how to document research, design decisions, iterations, artifacts, and collaboration. Recommendations below draw mainly on that case-study method, not on an asserted visual audit of Adis's homepage.

| Observed principle | Cre8ive District application | Engineering/content requirement |
|---|---|---|
| Connect design to a goal and user need | Make every homepage section answer a prospect question: who is this for, what changes, what is included, why trust the team, and what happens next. | Map each section to a user journey and one primary CTA; remove decorative sections that do not build understanding, proof, or action. |
| Show reasoning behind finished work | Present 2–3 strong case studies or clearly labelled concepts with context, audience/problem, strategy decision, identity system, applications, and evidenced result. | Create a reusable case-study content schema; support role/permission notes and optional sections so a case remains honest when outcome data are unavailable. |
| Show process artifacts as proof | Share selected anonymized strategy maps, sketches, systems, or before/after applications when ownership and permissions allow. For a new studio, use original concepts clearly marked as concepts. | Add optimized, responsive media with captions/alt text and rights metadata; avoid publishing confidential client data. |
| Put a real person and accountable team behind the work | Explain who leads strategy/design/web, what is founder-owned versus partner-delivered, and how Nigeria-based remote delivery works for international clients. | Maintain one reviewed profile/content source; do not promise team size, credentials, time zones, or response targets that are not true. |
| Organize service breadth into understandable categories | Lead with the approved Brand Foundation and its buyer situation; show website and visibility as separate, clearly scoped next steps. Keep AI/software/hardware out of the launch menu until validated. | Use an offer/service data model with inclusions, exclusions, fit, and CTA; do not publish a broad capability list that implies unstaffed delivery. |
| Let project proof have a direct route | Use descriptive project cards that link to individual cases; help visitors scan by project type and then inspect detail. | Cards need text labels, semantic links, meaningful image alternatives, stable case URLs, page metadata, and internal links back to enquiry. |

### Proposed Cre8ive District page model

1. **Home:** a clear outcome-led statement for founders and existing businesses in Nigeria and abroad; the Brand Foundation pilot; a compact proof strip; 2–3 featured cases/concepts; a short, numbered process; founder/team ownership; a prominent project enquiry CTA.
2. **Services:** Brand Foundation as the lead offer with deliverables, boundaries, buyer fit, timeline assumptions, and next step; website and visibility as separately scoped engagements; no speculative future offerings.
3. **Work:** filter or group by strategy/identity/web only if there is enough real work to make filtering useful. At launch, a simple set of descriptive project cards is preferable to a complex portfolio interface.
4. **Case study template:** short context → user/business problem → strategic choice → system and applications → process/iterations → outcome with evidence or an explicit no-metric explanation → contributor/permission details → enquiry CTA.
5. **About/process:** founder and collaborators, real capability boundaries, review/approval steps, remote work method, file handoff, and confirmed contact expectations.
6. **Contact:** short accessible POST form with truthful success/failure states and a durable lead record, plus direct WhatsApp/email alternatives. The prototype currently opens a prefilled WhatsApp draft; that is a useful alternative route, not proof that the studio received a lead. See WEB-F08–F16 and backend options in Section 5.

### Visual and interaction translation

Use the reference for the **content logic** of studio statement → service map → selected proof → human/team context → contact. Do not reproduce Adis's layout, graphics, case-study wording, image assets, typography, or brand name. Cre8ive should use its own approved identity and a distinctive visual system grounded in its work.

At desktop widths, give case-study imagery enough scale to demonstrate craft while keeping explanatory text legible alongside it. On narrow screens, stack text and media in reading order, preserve project labels and CTA visibility, use responsive image sources and fixed aspect-ratio placeholders, and avoid horizontal carousels as the only way to reach work. These are implementation recommendations; Adis's responsive behavior was not measured. All controls need keyboard focus and visible labels; motion must respect reduced-motion settings. Do not infer accessibility from the site's crawl notice that mentions tab navigation.

### Engineering priorities derived from this reference

- **P0 before launch:** settle the V1 offer and work permissions; build canonical Home/Services/Work/Case Study/About/Contact routes; use pre-rendered HTML and a small reusable component system; optimize portfolio imagery; implement accessible navigation and a real form-to-hosted-CRM or serverless-to-CRM intake; publish accurate metadata and canonical URLs.
- **P1 after proof grows:** add a CMS or structured editorial workflow when the founder needs routine case updates without engineering help; add work filters only when portfolio volume supports them; add aggregate source attribution and Search Console after privacy/vendor review.
- **Later only with evidence:** client portals, custom dashboards, bespoke databases, AI-assisted tools, app/software/hardware features. Adis's product case studies demonstrate the value of communicating design process; they do not justify building a product backend for Cre8ive District's marketing site.

### Limits of the comparison

Adis presents a broad service range and product-design cases, while Cre8ive District's launch focus is a narrow strategy-led brand offer and credible digital presence. The transferable lesson is how to explain intent and show process, not to match its service menu. This review did not inspect private analytics, test a live enquiry, contact the studio, verify project claims, or run external audits of performance/accessibility/SEO. Public claims and portfolio narratives remain self-presented; this document does not independently verify the outcomes.
