# Cre8ive District Website — Requirements Specification

**Status:** Draft for founder approval  
**Version:** 0.1  
**Product:** Public marketing website for Cre8ive District, a Nigeria-based creative and branding studio serving Nigeria and international clients  
**Release target:** Website V1 / public launch

## 1. Purpose and product boundary

The website helps prospective clients understand Cre8ive District's offer, judge whether it fits their needs, and start a project conversation. It supports a founder-led service business whose sales, qualification, proposal, payment, and delivery processes are handled manually.

V1 is a static, mobile-first marketing website. It has no server-side application, stored lead database, authentication, CRM, appointment booking, or checkout. The contact form validates in the visitor's browser and opens a prefilled WhatsApp draft. The visitor must press Send in WhatsApp; no enquiry reaches the studio until they do.

### Product goals

1. Explain the studio's brand-led offer and intended customer clearly.
2. Build trust through accurate process information and approved work examples or explicitly labelled studio concepts.
3. Give visitors a clear route to ask about a project.
4. Work well on common phone and desktop screen sizes, including for keyboard and assistive-technology users.
5. Let the founder learn which sources and services generate qualified enquiries using a manual lead tracker.

### Not product goals for V1

- Transacting or delivering creative services online.
- Automatically capturing, assigning, storing, or analysing leads.
- Acting as a portfolio CMS, social network, or client collaboration tool.
- Promising a specific sales, awareness, or business result to clients.

## 2. Users and access

| User | Needs | Access in V1 |
|---|---|---|
| Prospective client | Understand fit, scope and next step; contact the studio | Public read access; form may create a WhatsApp draft locally |
| Referral partner / collaborator | Quickly understand the studio and share the right page | Public read access; no special role |
| Studio founder / staff | Update copy, confirm routes and contact details, respond to leads | Source-file edits and access to WhatsApp/email; no website admin console |
| Website operator | Publish a reviewed version and keep domain/hosting configured | Deployment access outside the public site |

No user account or protected content exists in V1.

## 3. Information architecture and route requirements

| Canonical route | Current file | Purpose | Required sections / information |
|---|---|---|---|
| `/` | `index.html` | Position and convert | Who the studio helps, brand-led value proposition, core capabilities, approach, customer situations, process, truthful proof/concepts, primary CTA |
| `/services` | `services/index.html` | Explain service fit | Approved service categories, customer outcomes, examples of scope, how scoping/pricing works, CTA |
| `/about` | `about/index.html` | Establish point of view and trust | Studio purpose, principles, working style, accurate Nigeria base and confirmed international service arrangements, CTA |
| `/contact` | `contact/index.html` | Start qualification | Enquiry form, direct WhatsApp and email, base/service area, truthful form behaviour notice |
| `/Homepage` and legacy case variants | Existing legacy folders/config | Preserve old links without duplicate public pages | Redirect or resolve to the canonical lowercase route; only one indexable destination per page |

Shared site elements: header and responsive navigation, branded wordmark, footer, consistent primary CTA, typography/color system, and shared stylesheet/script. Every page must have a unique document title, concise description, one descriptive H1, and a canonical route decision before launch.

## 4. Main journeys

### J1 — Referred visitor enquires

Referral link → homepage → understands offer and location → services or approach if needed → contact page → completes fields → reviews WhatsApp draft → chooses Send → studio receives message → founder logs and follows up.

### J2 — Visitor contacts directly

Any page → direct WhatsApp or email link → visitor sends message → founder logs source and need manually.

### J3 — Studio updates the offer

Founder confirms service/scope/proof/contact details → edits source content → checks desktop and mobile rendering and all links → publishes via configured host. V1 has no browser-based content management.

## 5. Functional requirements

Priority: **M** = required for V1 launch; **S** = desirable for V1; **L** = later release.

### Navigation and routes

| ID | Priority | Requirement |
|---|---|---|
| FR-01 | M | Each canonical route is reachable from shared navigation/footer and loads when entered directly. |
| FR-02 | M | Mobile navigation can be opened and closed by pointer, keyboard, and touch; its expanded state and control relationship are exposed accessibly. Selecting a link closes the menu. |
| FR-03 | M | Legacy routes resolve to the intended canonical route without broken pages or duplicate indexable content. |
| FR-04 | M | The primary CTA on every page leads to `/contact`; secondary links lead to relevant service/approach information. |
| FR-05 | S | A visitor can identify current page/section in navigation using an accessible state such as `aria-current`. |

### Content and proof

| ID | Priority | Requirement |
|---|---|---|
| FR-06 | M | Homepage states the approved positioning, audience, primary service offer, location/service area, and next step. |
| FR-07 | M | Services page describes only services the founder confirms the studio can deliver; any scope examples are not represented as guaranteed inclusions. |
| FR-08 | M | About and process content describes the real studio and workflow; draft staffing, prices, credentials, dates, or response promises are not presented as facts without approval. |
| FR-09 | M | Client names, client logos, testimonials, outcomes, and case-study materials require factual support and permission. Self-initiated examples are visibly labelled as studio concepts. |
| FR-10 | S | Each service detail can be linked directly via a stable page anchor for use in outreach. |

### Contact and conversion

| ID | Priority | Requirement |
|---|---|---|
| FR-11 | M | Contact page offers the approved primary contact route and a working email alternative. The number/address must be founder-verified before publishing. |
| FR-12 | M | Form includes labelled inputs for name, email, business/brand, service interest, budget range, timing, and project context. Required fields and optional fields are identified consistently. |
| FR-13 | M | Browser validation prevents the WhatsApp draft from opening when required values are absent or malformed and provides usable feedback. |
| FR-14 | M | Valid form details are URL-encoded into the prefilled WhatsApp message without losing punctuation, spaces, or line breaks. |
| FR-15 | M | Before submission, the page explains that the website itself does not send or store the enquiry; the visitor must send the WhatsApp message. Do not promise that the studio has received it until Send is pressed. |
| FR-16 | M | If opening WhatsApp is blocked or unavailable, visitors can still use a visible direct WhatsApp link and email address. The site must not silently imply successful submission. |
| FR-17 | S | The form includes a brief privacy notice explaining that the page does not store the values and that sending them via WhatsApp/email transfers them to those services. Final copy requires founder review. |
| FR-18 | L | Persist enquiries on a server, send email notifications, integrate a CRM, provide booking, or show a submission confirmation after backend receipt. Requires a separately approved backend/data design. |

### Motion and interactive identity

| ID | Priority | Requirement |
|---|---|---|
| FR-19 | M | Decorative logo depth, reveal effects, ticker, and other motion do not prevent understanding, input, or navigation. |
| FR-20 | M | Reduced-motion preference disables or simplifies nonessential animation; brand mark remains legible and navigation remains functional. |
| FR-21 | S | Touch and keyboard users receive the same content and actions without relying on mouse tilt or hover. |

### Search and sharing

| ID | Priority | Requirement |
|---|---|---|
| FR-22 | M | Each canonical page includes a unique title and description, semantic page structure, and a human-readable URL. |
| FR-23 | S | Public launch includes an approved favicon and social sharing image/title/description, plus an explicit canonical URL and crawl/indexing policy. |
| FR-24 | L | Add structured data, a CMS-managed case-study library, blog, or campaign landing-page variants after positioning and content ownership are defined. |

## 6. Non-functional requirements

| ID | Priority | Requirement / acceptance condition |
|---|---|---|
| NFR-01 — Responsive | M | At narrow phone, tablet, and desktop widths, content remains readable; no horizontal overflow, overlapped navigation, clipped CTAs, or inaccessible controls. |
| NFR-02 — Accessibility | M | Semantic landmarks and heading order; labels associated with fields; keyboard-operable controls; visible focus; meaningful link names; sufficient text/background contrast; decorative images ignored by assistive technology; status/errors announced. Aim for WCAG 2.2 AA. |
| NFR-03 — Motion accessibility | M | Respect `prefers-reduced-motion`; avoid flashing and motion that requires precise pointer input. |
| NFR-04 — Performance | M | Static pages avoid unnecessary libraries and large media; primary text and CTA render without waiting for animation or third-party scripts. Use compressed, appropriately sized assets and lazy-load below-fold media if introduced. Confirm hosting and font dependency behavior before launch. |
| NFR-05 — Browser support | M | Core navigation and contact flow work in current supported mobile and desktop browsers with JavaScript enabled. Content, contact alternatives, and basic navigation remain understandable if decorative JavaScript fails. Exact support window requires founder/operator sign-off. |
| NFR-06 — Reliability | M | Direct URL loading, clean URLs, redirects, and asset paths work on the production host; external font failure retains a readable local fallback. |
| NFR-07 — Privacy | M | V1 stores no form data server-side and uses no unapproved tracking. Clearly disclose the WhatsApp/email handoff. Any future analytics, cookies, or backend storage requires a separate decision and suitable notice/controls. |
| NFR-08 — Security | M | No secrets or credentials are embedded in public assets. External links use safe navigation behavior where applicable; no user-provided input is interpreted as markup or executed. |
| NFR-09 — Search quality | M | Each page has useful metadata, one clear H1, descriptive page copy, meaningful internal links, and no duplicate route content intended for indexing. |
| NFR-10 — Maintainability | S | Shared page chrome, styles, and behaviour remain centralized; repeated legacy content is not maintained as independent variants; content claims have a named founder approver. |
| NFR-11 — Observability | L | If measurement is added later, document collected events, ownership, retention, consent/notice requirements, and how launch decisions will use them. |

## 7. Out of scope for website V1

- Server/API endpoint, database, inbox automation, lead tracker, or CRM sync.
- Sign-up/sign-in, roles, client dashboard, project messaging, file uploads, or client proofing.
- Calendly-style booking, online payment, e-commerce, quoting/pricing calculator, or instant proposal generation.
- CMS, blog, gated downloads, newsletter capture, multilingual publishing, or portfolio filtering.
- Chatbot, AI assistant, AI-generated proposals, automated personalization, or AI content generation on the public site.
- Advertising platform pixels or analytics until an owner approves the tool, purpose, privacy treatment, and success metrics.

These are possible future capabilities, not implicit launch requirements.

## 8. Dependencies and owners

| Dependency | Needed from | Blocks |
|---|---|---|
| Approved positioning, first offer, service list, exclusions, and initial customer/geography focus | Founder | Final copy and conversion claims |
| Actual deliverables, price/range policy, timing, available start slots | Founder / delivery owner | Package details and qualification choices |
| Verified WhatsApp number and monitored email | Founder / business operator | Contact functionality |
| Approved client work, testimonials, concept labels, and usage permissions | Founder / rights holders | Proof sections and social previews |
| Domain, DNS, hosting, redirect behaviour, and deployment ownership | Website operator | Production availability and canonical URLs |
| Business base, international delivery/payment arrangements, and in-person/service-area facts | Founder | Location and international-service copy, contracts, and any local listing claims |
| Privacy wording and future measurement decision | Founder / appropriate adviser | Form notice, analytics, and future data capture |

## 9. V1 acceptance checklist

V1 is accepted for public launch when all **M** requirements are reviewed and these user-visible checks pass:

1. Home, services, about, and contact pages load directly on the production host and from shared navigation.
2. Legacy links land on the appropriate canonical route; no duplicate case-variant pages are presented as separate destinations.
3. A visitor can state from the homepage who the studio helps, what it offers, and how to begin a project.
4. Published claims, offers, contact details, locations, work samples, and testimonials are founder-approved and accurate.
5. Required contact fields validate; a valid submission opens a correctly encoded WhatsApp draft containing each entered value; the visible copy makes clear the visitor still has to send it.
6. WhatsApp and email alternatives work, including on a device where only a browser-based WhatsApp experience is available; a blocked popup does not falsely report receipt.
7. All primary actions and navigation work using keyboard, touch, and pointer; focus is visible and form fields have usable labels and feedback.
8. Reduced-motion mode remains readable and usable; decorative motion does not carry unique information.
9. At representative phone and desktop widths, the pages have no horizontal overflow, overlapping content, or clipped primary action.
10. Page titles/descriptions, favicon, canonical URL, and social preview metadata are reviewed for launch; unresolved items have a named owner and launch decision.
11. Founder/operator has a manual process and named owner to capture, respond to, and follow up on each message received.

## 10. Founder decisions to resolve

1. Which customer segment and offer lead the homepage: new businesses, established businesses, or a clear test of both?
2. Is **Brand Foundation** the approved core offer? What are its exact outputs, exclusions, client inputs, timing, revision rounds, price or starting-price policy?
3. Which adjacent services can be promised and delivered now: websites, campaign assets, social design, ongoing support, advertising, apps?
4. Is the current contact budget selector useful and aligned with actual qualification policy? If not, should it use fewer bands or “not sure yet” only?
5. Who owns WhatsApp/email response, during which hours, and what acknowledgement time can actually be sustained?
6. Which projects may be shown, and who has approved public use of each asset/testimonial?
7. Which canonical domain, email, WhatsApp number, business location, and service area should be published?
8. Is the site intentionally launched without stored enquiries and analytics for the initial validation period? If so, who records source and outcome manually?
9. Which browser support baseline, performance target, social preview art, favicon, and accessibility review process should be used for production sign-off?

---

*This is a proposed implementation specification based on the current prototype and strategy docs. Founder approval is required for business claims, contact values, service scope, privacy copy, and production release decisions.*
