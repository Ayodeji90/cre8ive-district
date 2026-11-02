# Cre8ive District — Business & Website V1 Specification

**Status:** Working specification for founder review  
**Version:** 0.1  
**Purpose:** Define the first sellable version of Cre8ive District and the website that supports it.

## 1. Product definition

Cre8ive District is a creative and branding studio based in Nigeria and serving businesses in Nigeria and internationally. It helps founders starting a business and existing brands improve their strategy, identity, and visibility across the places customers meet them. Nigeria is the home market, not the limit of the intended market.

The first version is a founder-led service business supported by a simple marketing website and a manual sales and delivery workflow. The website's job is to explain the offer, establish trust with truthful evidence, and start qualified conversations. It is not a self-service design platform, a marketplace, or an automated proposal and payment system.

### Launch positioning

> Cre8ive District helps founders and growing businesses build a distinctive brand, from clear strategy and visual identity to the creative and digital assets that bring it into the world.

Lead with brand strategy and identity. Offer web, campaign, and ongoing creative work when it fits the client's wider brand need and the studio's actual capacity.

## 2. Customers and problems

### Primary customer groups to validate

1. **Founders preparing to launch** who need brand strategy, identity, and practical launch assets.
2. **Existing businesses in Nigeria or abroad** whose brand or digital presence needs to become clearer, more distinctive, or more consistent.

### Customer needs

- Explain what makes the business distinct and who it serves.
- Replace disconnected or improvised brand materials with a coherent system.
- Understand what the studio will deliver, how collaboration works, the likely timeline, and the investment before committing.
- Have one clear next step to discuss a project.

These are launch hypotheses. Validate which customer types, sectors, and geographies are reachable and profitable against real enquiries and sales after the first month. Do not let a broad service area turn the positioning into a message for everyone.

## 3. Services and sellable offers

The studio may provide four connected service lines. Each project must have a written scope, deliverables, exclusions, schedule, fee, payment milestones, revision limits, and client responsibilities before work starts.

| Service line | Customer outcome | Typical scope to confirm per project |
|---|---|---|
| Brand strategy and identity | A clear brand direction and usable identity system | Discovery, positioning/story, logo suite, visual system, usage guide, agreed launch assets |
| Digital presence | A clear, on-brand website or landing page | Content structure, visual design, agreed page set, build/platform, responsive QA, launch handoff |
| Campaigns and creative | A consistent creative idea and assets for a launch or promotion | Concept, art direction, agreed formats/assets, handoff |
| Ongoing creative support | A predictable source of design support | Monthly scope, capacity/turnaround, channels, included work, exclusions |

### First offer to productize

Create one fixed-scope **Brand Foundation** package as the primary entry offer. The exact deliverables, duration, number of feedback rounds, price, and exclusions are not approved yet and must be set from delivery capacity, costs, and margin. Until then, describe it as a tailored project rather than publishing a fixed price or timeline.

Do not advertise mobile app development, paid media management, guaranteed business results, or other capabilities until the studio confirms it can deliver them reliably and profitably. The current strategy and operational draft contain broader service and price assumptions; they are not authoritative launch commitments.

## 4. Website V1 scope

### Pages

| Route | Purpose | Required content and action |
|---|---|---|
| `/` | Explain the studio and direct visitors to an enquiry | Positioning, core offer, service summary, approach, truthful proof or clearly labelled concepts, primary project CTA |
| `/services` | Help a visitor understand service fit | Four service lines, likely outcomes, scoping note, enquiry CTA |
| `/about` | Explain the studio's point of view and working style | Why the studio exists, principles, Nigeria base and confirmed international working arrangements, enquiry CTA |
| `/contact` | Collect enough context to begin qualification | Name, email, business, service, budget range, timing, project context; WhatsApp and email alternatives |

The current `/Homepage` route should continue to resolve to the homepage. Case variants such as `/Contact` should not become separate content destinations.

### Primary user journey

1. A visitor arrives from a referral, social post, search, or direct link.
2. They can identify who the studio helps, what it offers, and its primary next step without navigating deeply.
3. They review services and the working approach if they need more detail.
4. They start an enquiry through the contact page, WhatsApp, or email.
5. The studio responds, qualifies the request, and agrees whether to prepare a proposal.

### Enquiry behaviour in V1

The current contact form validates required fields and opens a prefilled WhatsApp message. The visitor must send the message in WhatsApp; the website does not store or submit the enquiry to a Cre8ive District database. This limitation must remain clear in page copy and internal handling. The studio must manually log enquiries and follow up.

Email and direct WhatsApp links remain available as alternatives. No account, booking calendar, CRM, payment, or client portal is part of V1.

## 5. Functional requirements

- All navigation, page links, contact methods, and route redirects resolve correctly.
- The contact form prevents submission when required fields are invalid and passes the entered details into the WhatsApp draft.
- The contact flow works on current mobile and desktop browsers, including when WhatsApp is not installed but WhatsApp Web is available.
- The mobile menu exposes its open/closed state to assistive technology and can be operated by keyboard.
- Motion respects the visitor's reduced-motion system preference. Motion is decorative and must not block reading or navigation.
- Every page has a descriptive title and summary, semantic headings, visible keyboard focus, form labels, and useful link text.
- Pages remain readable and usable at narrow phone widths, with no horizontal overflow or clipped primary actions.
- Work samples, client names, testimonials, logos, performance claims, and statistics are published only when true, approved, and properly attributed. Self-initiated concepts are labelled as concepts.

## 6. Visual and content direction

- Keep the current modern editorial visual system: dark and warm-neutral surfaces, orange accents, strong typography, generous spacing, and restrained motion.
- The Cre8ive District wordmark may use subtle interactive depth. It must remain legible, quick to render, and stable for touch users and reduced-motion users.
- Write in plain language focused on customer needs, deliverables, process, and next action.
- Use one primary CTA: **Start a project** or equivalent wording leading to `/contact`.
- Do not publish unverified client proof, invented credentials, fixed delivery dates, fixed package prices, or promises of sales growth.

## 7. Sales and delivery workflow

V1 operates manually using a designated business inbox/WhatsApp, a lead tracker, document templates, and a shared project folder. A CRM can be selected later if manual tracking becomes unreliable.

1. **Enquiry received:** acknowledge it during the studio's stated working hours; log source, need, timing, budget, and next action.
2. **Qualification:** confirm business context, desired outcome, decision-maker, scope, timeline, budget fit, and delivery capacity.
3. **Discovery:** collect the brief and any existing brand assets; agree the problem and success criteria.
4. **Proposal:** send scope, deliverables, exclusions, timeline, milestones, fee, payment terms, revision limits, ownership/handoff terms, and proposal expiry.
5. **Booking:** begin only after written acceptance and the agreed first payment/retainer are received.
6. **Kickoff and production:** confirm client contacts, feedback owner, schedule, asset access, review dates, and change-request process.
7. **Review and handoff:** obtain approval against the agreed scope, collect final payment, deliver agreed files, and explain usage.
8. **Close and learn:** request feedback, ask permission before publishing work or testimonial, and record outcome and referral opportunity.

Response-time promises, payment percentages, refund/cancellation terms, ownership terms, and minimum fees require founder approval before being used with clients. Existing strategy drafts contain example thresholds and team structures; treat those as proposals until checked against the real business.

## 8. Launch measurement

Track weekly in a simple spreadsheet or CRM:

- Enquiries by source
- Qualified enquiries
- Discovery conversations held
- Proposals sent and accepted
- Paid projects started and cash collected
- Average response time and follow-up completion
- Lost/unqualified reasons
- Work sold versus delivery capacity

The first month is a validation period. Set numeric targets after confirming capacity and fixed costs. Revenue goals must be based on the studio's own costs, delivery margin, and available time; reach and clicks alone are not success measures.

## 9. Explicitly out of scope for V1

- Automated form storage, email notifications, CRM synchronisation, or lead analytics on the website
- Online booking, user accounts, client portal, e-commerce, and online payment
- Case-study CMS or frequently updated portfolio system
- Blog, newsletter, or downloadable resource funnel
- Paid advertising campaign setup and ongoing ad reporting
- A promise that branding or marketing will produce a specific commercial outcome

These can be considered after the manual process and offer have been validated.

## 10. Decisions required before public launch

| Decision | Owner input needed | Why it matters |
|---|---|---|
| Primary service and Brand Foundation deliverables | Confirm what the team can reliably deliver | Defines the offer, proposal, and website claims |
| Fees, minimum project size, payment milestones | Confirm cost base, desired margin, and client payment approach | Prevents unprofitable or inconsistent selling |
| Founder/team roles and weekly delivery capacity | Confirm who does sales, creative, web, marketing, and project coordination | Prevents overselling and missed follow-up |
| Portfolio and proof | Select approved client work and/or studio concepts | Establishes trust without unsupported claims |
| Contact details and response hours | Verify WhatsApp number, email ownership, and coverage | Ensures enquiries reach someone who can respond |
| Service area and international delivery | Confirm actual base, remote/in-person arrangements, countries served, time zones, payment, and contracting approach | Keeps location and service claims accurate and operationally supportable |
| Legal/contract terms and privacy handling | Approve agreement, IP handoff, cancellation, and handling of enquiries | Clarifies client expectations and data practices |
| Website analytics and lead measurement | Decide whether to add privacy-conscious measurement in a later iteration | Makes channel learning more reliable |

## 11. Acceptance criteria for V1

V1 is ready for public launch when:

- The founder has approved the positioning, sellable offer, scope boundaries, and enquiry response owner.
- All public content and proof have been reviewed for accuracy and permission.
- Home, services, about, contact, and legacy route behavior are consistent.
- The contact paths and form-to-WhatsApp handoff have been manually checked on a phone and desktop.
- The studio can manually capture and follow up every enquiry, prepare a proposal, accept payment, and deliver the agreed first offer.
- Mobile layout, keyboard navigation, labels, reduced-motion behavior, and page metadata have been reviewed.
- Pricing, availability, contact details, and any response-time claims shown publicly are confirmed.

---

*This specification describes a proposed first version, not a commitment to unconfirmed prices, staffing, delivery times, or results. Update it with founder decisions and first-month evidence.*
