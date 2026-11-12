# Foundable.com — Complete Site Structure & Page-by-Page Analysis

*Thorough research of every web page on foundable.com — structure, content,
layout, interactions, and information architecture. Styling and colors excluded.*

**Research date:** 2026-11-08
**Company:** Autono Labs, Inc. (Delaware C-corporation)
**Co-founders:** Stefan Stoll and Wesley Lin
**Founded:** April 10, 2026 | **HQ:** San Francisco, CA
**Product name:** Foundable | **AI persona:** Ted

---

## Table of Contents

1. [Complete Page Inventory](#1-complete-page-inventory)
2. [Global Elements (shared across all pages)](#2-global-elements)
3. [Homepage](#3-homepage)
4. [Pricing](#4-pricing)
5. [About](#5-about)
6. [Security](#6-security)
7. [Solutions Pages (7 pages)](#7-solutions-pages)
8. [Integrations](#8-integrations)
9. [Ideas](#9-ideas)
10. [Blog](#10-blog)
11. [Community](#11-community)
12. [Press](#12-press)
13. [Careers](#13-careers)
14. [Contact](#14-contact)
15. [Legal Hub & Legal Documents (13 pages)](#15-legal-hub--legal-documents)
16. [Auth & App Pages](#16-auth--app-pages)
17. [Documentation Site](#17-documentation-site)
18. [Structural Patterns & Takeaways](#18-structural-patterns--takeaways)

---

## 1. Complete Page Inventory

**48 unique English public pages + ~25 app routes behind auth.**
All public pages exist in **36 locale variants** (ca, cs, da, de, es, et, fi, fil, fr, hi, hr, hu, id, it, ja, ko, lt, lv, ms, nb, nl, pl, pt-br, ro, ru, sk, sl, sv, sw, th, tr, uk, vi, zh-hans, zh-hant).

### Public Marketing Pages
| # | Path | Purpose |
|---|------|---------|
| 1 | `/` | Homepage |
| 2 | `/pricing` | Pricing plans |
| 3 | `/about` | Company story |
| 4 | `/security` | Security architecture |
| 5 | `/integrations` | 34 app integrations |
| 6 | `/ideas` | 15 browsable business ideas |
| 7 | `/community` | Discord + social links |
| 8 | `/press` | Brand resources |
| 9 | `/careers` | Hiring |
| 10 | `/contact` | Email directory |

### Solutions Pages (7)
| # | Path | Audience/Use Case |
|---|------|-------------------|
| 11 | `/solutions/websites` | Website building |
| 12 | `/solutions/selling-online` | E-commerce/checkout |
| 13 | `/solutions/run` | Autonomous AI agent mode |
| 14 | `/solutions/marketing` | Social + email marketing |
| 15 | `/solutions/small-businesses` | SMB owners |
| 16 | `/solutions/creators` | Content creators |
| 17 | `/solutions/side-projects` | Side hustlers |

### Blog (18 posts)
| # | Path | Title |
|---|------|-------|
| 18 | `/blog` | Blog index |
| 19 | `/blog/ai-business-builder` | What is an AI business builder? |
| 20 | `/blog/ai-business-builder-fees` | AI business builder fees |
| 21 | `/blog/foundable-vs-chatgpt` | Foundable vs ChatGPT |
| 22 | `/blog/foundable-vs-durable` | Foundable vs Durable |
| 23 | `/blog/foundable-vs-lindy` | Foundable vs Lindy |
| 24 | `/blog/foundable-vs-lovable` | Foundable vs Lovable |
| 25 | `/blog/foundable-vs-marblism` | Foundable vs Marblism |
| 26 | `/blog/foundable-vs-nanocorp` | Foundable vs NanoCorp |
| 27 | `/blog/foundable-vs-polsia` | Foundable vs Polsia |
| 28 | `/blog/foundable-vs-sintra` | Foundable vs Sintra |
| 29 | `/blog/foundable-vs-wix` | Foundable vs Wix |
| 30 | `/blog/foundable-vs-zapier-agents` | Foundable vs Zapier Agents |
| 31 | `/blog/is-foundable-legit` | Is Foundable legit? |
| 32 | `/blog/is-polsia-worth-it` | Is Polsia worth it? |
| 33 | `/blog/lovable-app-first-customers` | Lovable app first customers |
| 34 | `/blog/make-money-from-idea-with-ai` | Make money from idea with AI |
| 35 | `/blog/polsia-alternatives` | Polsia alternatives |
| 36 | `/blog/switch-to-foundable` | Bring your business to Ted |

### Legal Pages (13)
| # | Path | Document |
|---|------|----------|
| 37 | `/legal` | Legal hub/index |
| 38 | `/terms` | Terms of Service |
| 39 | `/privacy` | Privacy Policy |
| 40 | `/acceptable-use` | Acceptable Use Policy |
| 41 | `/refund-policy` | Refund & Dispute Policy |
| 42 | `/ai-disclosure` | AI Disclosure |
| 43 | `/subprocessors` | Subprocessors & Data Recipients |
| 44 | `/dmca` | DMCA Notice & Takedown |
| 45 | `/responsible-disclosure` | Responsible Disclosure Policy |
| 46 | `/legal/security` | Security Policy |
| 47 | `/legal/domain-holding-agreement` | Domain Holding Agreement |
| 48 | `/cookies` | Cookie & Tracking Notice |

### Auth & App Pages (behind login)
Discovered via robots.txt — not publicly accessible:
`/sign-in`, `/sign-up`, `/home`, `/build`, `/run`, `/grow`, `/inbox`,
`/library`, `/schedule`, `/settings`, `/start`, `/new`, `/line`, `/f/`,
`/admin`, `/checkout/`, `/companies/`, `/account/`, `/invite/`, `/join`,
`/welcome/`, `/open-gift`, `/open-line`, `/signed-out`, `/imessage/`

### External Sites
- `docs.foundable.com` — Documentation (Mintlify-hosted)
- `docs.foundable.com/changelog` — Changelog
- `status.foundable.com` — Status page

---

## 2. Global Elements

### Top Navigation Bar (every page)

```
┌─────────────────────────────────────────────────────────────────────┐
│ [Foundable logo]   Product ▾   Solutions ▾   Resources ▾           │
│                    Pricing      Security        Log in   [Start free] │
└─────────────────────────────────────────────────────────────────────┘
```

- **Logo** (left): Foundable wordmark SVG, links to `/`
- **Product dropdown**: Links to solutions/websites, solutions/selling-online, solutions/run, solutions/marketing, integrations
- **Solutions dropdown**: Links to solutions/small-businesses, solutions/creators, solutions/side-projects
- **Resources dropdown**: Links to blog, community, ideas, docs.foundable.com
- **Pricing**: Direct link to `/pricing`
- **Security**: Direct link to `/security`
- **Log in** (right): Links to `/sign-in`
- **Start free** (right, button CTA): Links to `/sign-up`
- Skip-to-content anchor `#content` present

### Footer (every page)

```
┌──────────────────────────────────────────────────────────────────┐
│  Product          Solutions           Company         Legal      │
│  ─────────        ──────────          ─────────       ─────      │
│  Websites         Small businesses    About           Legal      │
│  Selling online   Creators            Careers         Terms      │
│  Run              Side projects       Press           Privacy    │
│  Marketing        Ideas               Contact         Security   │
│  Integrations                         Status          Subproc.   │
│  Docs                                 Community                  │
│  Blog                                                            │
│                                                                  │
│  © 2026 Autono Labs, Inc.    [Language selector ▾]               │
│  [X] [LinkedIn] [Instagram] [Threads] [Discord] [GitHub]        │
└──────────────────────────────────────────────────────────────────┘
```

- 4-column link grid
- Copyright: "© 2026 Autono Labs, Inc."
- Language selector: 36 locales
- Social icons: X, LinkedIn, Instagram, Threads, Discord, GitHub

---

## 3. Homepage (`/`)

### Section 1 — Hero (centered)

- Ted avatar icon above the headline
- **H1:** "Build a business that runs on its own."
- **Subtitle:** "Meet Ted, the AI employee who does the work."
- Large demo image/screenshot showing Ted building a website from a single sentence
- The image shows a split-screen: Ted's chat on the left, the website he's generating on the right

### Section 2 — Social Proof Logos

- 8 institution logos displayed in a row: **Stanford, Duke, Google, Stripe, OpenAI, Shopify, MIT, Costco**
- Text: "14,000+ people have signed up, including founders from the best teams."
- Clarification: "People who studied and built at these places use Foundable to start something of their own."
- CTA button: "Start yours"

**Important note:** These are places Foundable's *users* come from, NOT the team's background. There are no team bios on the site.

### Section 3 — How It Works (5 numbered steps)

Each step has a heading, description, and accompanying screenshot/illustration:

1. **"Meet Ted."** — "Your AI employee."
2. **"Say the idea. Ted builds it."** — "A website, logo and email, all done for you."
3. **"He runs it while you sleep."** — "Step after step, and you see every move."
4. **"He finds people to reach out to."** — "He drafts each email. You decide what goes out."
5. **"Text him from anywhere."** — "Phone or desktop, he's always a text away."

### Section 4 — Brand Showcase

- **Heading:** "Made for your business"
- **Subtitle:** "Not templates. Everything Ted makes starts from your brand."
- Uses a fictional demo brand **"Afterhours"** (heavyweight hoodies, Los Angeles) to show outputs
- 5 cards displayed, each showing a different type of output Ted generates:
  - **Brand Identity** — logo, colors, typography
  - **Social Media Posts** — Instagram-style posts
  - **Pitch Deck** — presentation slides
  - **Research** — market/competitor research
  - **Spreadsheets** — business data

### Section 5 — Capabilities Grid

- **Heading:** "Everything a business needs, handled"
- 6 feature cards:

| Feature | Description |
|---------|-------------|
| **Website on own domain** | Ted builds and publishes to custom domain |
| **Stripe payments** | No Foundable fee, customers pay into user's Stripe |
| **Emails/posts with approval** | Ted drafts, user approves before anything goes out |
| **Phone number** | Ted answers calls (Pro/Max plans) |
| **App integrations** | 21 logos shown: Gmail, Slack, Instagram, Stripe, Notion, HubSpot, TikTok, Sheets, Mailchimp, X, QuickBooks, Analytics, Calendly, LinkedIn, Drive, YouTube, Airtable, Facebook, Search Console, Google Calendar, Ted |
| **Data privacy** | Content not used for AI training |

### Section 6 — Community Stats

- **"4,800+ businesses started"**
- **"3,000+ websites built"**

### Section 7 — FAQ Accordion (7 questions)

1. What is Foundable?
2. Do I need to know how to code?
3. How do I get started?
4. What does Ted do on his own vs. what needs approval?
5. How much does it cost?
6. Do I own what Ted builds?
7. Can I accept payments through my website?

Covers: no coding needed, free to start, approval model ("Ask First" default, "On its own" mode available), ownership confirmed, Stripe payments in 44 countries.

### Section 8 — Final CTA

- Ted mascot illustration
- **"Ted's ready. Are you?"**
- CTA button to sign up

---

## 4. Pricing (`/pricing`)

### Hero

- **H1:** "Put Ted to work."
- **Subtitle:** "He builds your business and runs it while you're away. Start free, and upgrade when he has more to do."

### Plan Cards (4 cards, side by side)

| Plan | Price | Credits | Highlights |
|------|-------|---------|------------|
| **Free** | $0/mo | 15 welcome + 5/day (30/mo cap) | 1 website, build + publish, no card needed |
| **Basic** | $25/mo | 200/mo + 5 free/day | "One idea, ready to run." Cancel anytime. |
| **Pro** *(Most popular badge)* | $50/mo | 500/mo + 5 free/day, 20% off per credit | Team invites. Slider toggle: 500 ↔ 1,000 credits |
| **Max** *(Best value badge)* | $200/mo | 2,500/mo + 5 free/day, 36% off per credit | Slider toggle: 2,500 / 5,000 / 10,000 credits |

**Interactive element:** Pro and Max cards have slider toggles that let users adjust credit amounts (and the price changes accordingly).

### "Every plan includes" (6 cards)

1. Ted builds websites
2. Text Ted from your phone
3. Publish in one press
4. Free fixes (10/day)
5. Encrypted and private
6. *(6th card content)*

### FAQ Accordion (10 questions)

1. What do I get on the free plan?
2. What are credits?
3. Do unused credits roll over? (Pro/Max carry 1 month; Basic doesn't)
4. Can I change my plan?
5. Can I buy more credits without upgrading? (Yes — 100 to 1,000 credit packs, one-time)
6. What is the refund policy?
7. What happens when my plan ends?
8. Do you charge per team member? (No per-seat pricing)
9. Do I own what Ted builds? (Yes)
10. How do I pay? (Link by Stripe, USD only)

### Key pricing insights

- **Credit-based system** — everything Ted does costs credits
- **Free tier is functional** — 15 welcome credits + 5/day, enough to explore
- **No per-seat pricing** — teams included on Pro/Max
- **USD only** — no local currency support
- **Link by Stripe** — not raw Stripe checkout, uses Stripe's Link product
- **Credit packs** — one-time purchases of 100–1,000 credits available
- **Rollover rules** — Pro/Max carry unused credits 1 month, Basic doesn't

---

## 5. About (`/about`)

### Hero

- **H1:** "An AI employee for anyone with an idea."
- **Body:** "We believe anyone with an idea should be able to start a business. So we built Ted, the AI employee who does the work."

### Three-Column Feature Blocks

| Block | Content |
|-------|---------|
| **What we're building** | Ted builds your website, puts it online and runs the business |
| **Who it's for** | Small businesses, creators and side projects |
| **What drives us** | Ideas that become real businesses |

### "Why we started"

Two paragraphs explaining how good ideas stall because of operational overhead. The thesis: people with ideas shouldn't need to also be web developers, designers, and marketers.

**"What Ted does today" (5 bullets):**
1. Builds a website and publishes it
2. Makes a logo and business email
3. Writes to stores and customers
4. Drafts social media posts
5. Sets up Stripe payments

**Company facts sidebar:**
- Founded: April 2026
- HQ: San Francisco
- Entity: Autono Labs, Inc.
- **No founder bios, no team photos, no individual member information**

### "How we build" (3 principles)

1. **"Ted does the work"** — AI handles execution
2. **"You see him work"** — Transparency in what Ted is doing
3. **"Proof before polish"** — Ship working things fast, refine later

### Community CTA

- "More than 5,000 people are in the Foundable Discord"
- "Join the community" button

### "Get in touch" (5 links)

Contact, Press, Careers, Security, "Is Foundable legit?" (blog post)

### Final CTA

"Start with your idea." → sign-up

---

## 6. Security (`/security`)

### Hero

- **H1:** "Your business, kept safe."
- Two CTAs: "Read the security policy" → `/legal/security`, "Report an issue" → `/responsible-disclosure`

### "Four ways Foundable keeps it safe" (tabbed/segmented UI, 4 groups × 3 cards = 12 cards)

**Your Data:**
- Account ownership checked on every request
- Checked again at the database level
- Other accounts turned away

**Sign-in:**
- Google/Apple/email code (no passwords stored)
- Session expires automatically
- Protected cookie hidden from page JavaScript

**Building:**
- Each build runs in a walled-off sandbox
- Only reaches AI + code library
- Everything else out of reach

**Releases:**
- Test copy runs updates first
- Each change reviewed before going live
- Rollback available

### "Built in for every account" (6 feature cards)

1. Passwordless sign-in
2. Expiring sessions
3. Ownership check per request
4. Database-level access enforcement
5. Keys in locked store
6. Rate limiting

### "Secured layer by layer" (4 numbered layers)

1. **Layer 01:** Worldwide CDN for published websites (isolated code per site)
2. **Layer 02:** App hosted in US with one front door (single entry point)
3. **Layer 03:** Sandboxed build environments (one sandbox per build)
4. **Layer 04:** Encrypted storage + encrypted connections + 14-day backups

### "For founders" (website security, 4 bullets)

- Sandbox per build
- CDN delivery
- Database isolation per site
- Stripe account in user's name (Foundable never touches the money)

### "Your data, your rules" (3 cards)

1. Kept out of AI training
2. Deleted on demand
3. Disconnect apps any time

### "Read it in writing" (5 document links)

Security policy, DPA, Subprocessors, Privacy, Responsible disclosure.
Contact: security@foundable.com

### FAQ Accordion (8 questions)

1. Does Foundable train AI on my content? (No)
2. Where is my data stored? (US)
3. Who can access my account data?
4. How are keys and secrets handled?
5. What happens if there's a security incident?
6. Can I delete my account and all data?
7. How are payments handled? (Stripe)
8. How do I report a security issue?

**Notable:** No SOC 2, ISO 27001, or other compliance certifications mentioned anywhere.

---

## 7. Solutions Pages (7 pages)

All 7 solutions pages follow an **identical template** with unique content per page:

```
┌─────────────────────────────────────┐
│  [Eyebrow label]                    │
│  H1 with *italicized keyword*       │
│  Paragraph                          │
│  [Primary CTA]  [Secondary CTA]    │
│                    [Hero image]     │
├─────────────────────────────────────┤
│  H2 + subtitle                      │
│  ┌──────┐ ┌──────┐ ┌──────┐       │
│  │Feat 1│ │Feat 2│ │Feat 3│       │
│  │H3+txt│ │H3+txt│ │H3+txt│       │
│  │+image│ │+image│ │+image│       │
│  └──────┘ └──────┘ └──────┘       │
├─────────────────────────────────────┤
│  "How it works" — 3 numbered steps  │
├─────────────────────────────────────┤
│  H2 + 6-card grid                   │
├─────────────────────────────────────┤
│  FAQ accordion (4–6 questions)      │
├─────────────────────────────────────┤
│  Ted illustration                    │
│  "Ted's ready. Are you?"            │
│  [CTA button]                       │
└─────────────────────────────────────┘
```

### 7a. `/solutions/websites` — "From idea to a live site."

**Hero:**
- Eyebrow: "Websites"
- H1: "From idea to a *live site*."
- Body: "Tell Ted what the business needs. He builds the website, puts it live at its own address and changes it whenever you ask."
- CTAs: "Tell Ted your idea" → sign-up | "Add a checkout" → /solutions/selling-online
- Image: Ted's chat beside the website he built (split-screen)

**3 Features — "Websites, built by Ted" / "No templates to fill in and no code to write."**
1. **"Built from a conversation"** — Tell Ted what you want, or show him a site you like. He builds it, and you look it over on desktop, tablet and phone.
2. **"Change any part"** — Select a part of the page and say what to change, or swap a photo. Nothing goes live until you publish.
3. **"More than pages"** — A website can take payments, keep its own database, and you can take a copy of its code.

**How it works:** Describe it → Ted builds it → Publish (free at foundable.app address, own domain on paid plan)

**6-card grid — "Websites Ted builds":** Business websites, Landing pages, Online stores, Booking sites, Portfolios, Event pages

**FAQ (5):**
- Do I need to know how to code? (No)
- Where does the website live? (foundable.app subdomain)
- Can I use my own domain? (Yes, on paid plan)
- Can I undo changes? (Yes, version history with rollback)
- Do I own the website? (Yes, code export on paid plan)

---

### 7b. `/solutions/selling-online` — "Checkout, built into your site."

**Hero:**
- Eyebrow: "Selling online"
- H1: "Checkout, built into *your site*."
- Body: "Tell Ted what you sell. He adds it to your website with a Buy button, and customers pay into a Stripe account in your name."
- CTAs: "Tell Ted what you sell" → sign-up | "See how Ted builds sites" → /solutions/websites

**3 Features — "Selling, without the setup" / "No payment forms to set up."**
1. **"Tell Ted what you sell"** — Name and price → Ted shows product to approve → adds to site
2. **"A Stripe account in your name"** — One press sets up Stripe. Every sale lands there. Foundable takes no fee.
3. **"Live, with checkout"** — Ted publishes when you say so, Buy buttons and all.

**How it works:** Tell Ted what you sell → Approve the offer → Customers pay (through Stripe, into your account)

**6-card grid — "Things you can sell":** Products, Services, Classes, Consultations, Workshops, Event tickets

**FAQ (6):**
- Who takes payment? (Stripe in your name, no Foundable fee)
- Which businesses can sell? (Paid plan, 44 Stripe countries)
- How do I set prices? (One-time or monthly, Ted can suggest)
- Can I test first? (Yes, practice with fake card)
- How do refunds work? (Full refund from Payments or ask Ted)
- Do I need a website first? (No, Ted creates one)

---

### 7c. `/solutions/run` — "Ted works without being asked."

**Hero:**
- Eyebrow: "Run"
- H1: "Ted works without *being asked*."
- Body: "Start Run and Ted runs the business in the background, doing the next most useful thing again and again, and you can always see what he's doing and thinking."
- CTAs: "Tell Ted your idea" → sign-up | "See what Ted does for marketing" → /solutions/marketing
- Image: Ted's activity log beside his outreach/social/ads map

**3 Features — "Your business, running" / "Ted decides what's next and does it."**
1. **"The next useful thing, again and again"** — While Run is on, Ted works out what would help most, does it, then picks the next thing. (Image shows log: shops found, emails drafted, posts queued)
2. **"Asks before it goes out"** — Emails, posts and website changes wait for your Approve. Switch to "On its own" and he sends them himself. (Image shows approve/decline buttons)
3. **"You decide what he may do"** — For each connected account, choose what Ted is allowed to do: post, reply or follow activity. (Image shows per-account permission toggles)

**How it works:** Start Run (choose credit budget) → Ted works (picks next useful thing) → You decide (approve, answer questions, or stop)

**6-card grid — "What Ted handles while you're away":** Website improvements, Outreach emails, Social posts, Competitor research, Write-ups, Questions for you

**FAQ (6):**
- What does Ted do during a run? (Improves website, markets, learns about industry, writes up findings)
- Can I see what he's doing? (Always — goal + log + summary shown)
- What if Ted publishes something I don't like? (Asks first by default, "On its own" mode has Undo)
- Can I try a run for free? (One free run per business, Run Lite on own credits)
- How much does a run cost? (You set the credit budget, pause/stop anytime)
- How is this different from Polsia? (Approval gate, own Stripe account, no Foundable sales fee)

---

### 7d. `/solutions/marketing` — "Posts, emails and outreach."

**Hero:**
- Eyebrow: "Marketing"
- H1: "Posts, emails and *outreach*."
- Body: "Ted writes the posts, drafts the emails and finds people who could become customers. Ted asks you before anything goes out."
- CTAs: "Tell Ted about your business" → sign-up | "See how Ted runs it" → /solutions/run

**3 Features — "Marketing that gets done" / "The posts, the emails and the people to send them to."**
1. **"Posts for your accounts"** — On paid plan, Ted writes post + makes picture. Waits for Approve or scheduled time. (Image shows Instagram-style post with Edit/Schedule/Decline/Approve buttons)
2. **"Outreach, with your OK"** — Ted finds businesses that could buy, confirms addresses, drafts first email to each.
3. **"Your accounts, your rules"** — Connect Instagram, Facebook, LinkedIn, X or Threads. Choose what Ted may do per account.

**How it works:** Connect your accounts → Ted writes (posts with pictures, emails, first messages) → You approve

**6-card grid — "What Ted handles":** Social posts (FB, IG, LinkedIn, X, Threads, TikTok), Post pictures, Scheduled posts, Finding customers, Outreach emails, Comment replies (drafted for FB, IG, X — you send)

**FAQ (5):**
- Which accounts? (Facebook, Instagram, LinkedIn, X, Threads, TikTok on paid plan)
- Does Ted post without asking? (No — asks first, "On its own" mode available within budget)
- Where do emails come from? (Your foundable.app address, own domain on paid plan)
- Can I edit posts before they go out? (Yes — edit words, swap picture, ask for new one)
- Does Ted reply to comments/messages? (Drafts replies, you send them)

---

### 7e. `/solutions/small-businesses` — "Ted handles the busywork."

**Hero:**
- Eyebrow: "For small businesses"
- H1: "Ted handles the *busywork*."
- Body: "Ted keeps your website current, drafts your emails and works in the apps you already use, so you can get back to the work you love."
- CTAs: "Tell Ted about your business" → sign-up | "See what Ted does for marketing" → /solutions/marketing
- Image: Coffee shop's Foundable home showing chat, generated content, website

**3 Features — "The busywork, off your plate" / "Tell Ted once. He does the work."**
1. **"Emails, drafted for you"** — Ted writes business emails from your address, sends on your approve.
2. **"Works in the apps you use"** — Connect Gmail, Google Calendar, Sheets, Slack, QuickBooks, etc. Ted reads and drafts changes for approval.
3. **"Sell from your site"** — Tell Ted what to sell and the price. Customers pay into your Stripe account.

**How it works:** Tell Ted about the business → Ted does the work (website, emails, spreadsheets, scheduled jobs) → You approve

**6-card grid — "What Ted handles":**
1. Website updates
2. Customer emails
3. Jobs on a schedule
4. Spreadsheets and decks
5. **Phone calls** (own number on Pro/Max, Ted picks up every call)
6. **Text Ted** (ask by iMessage or SMS)

**UNIQUE to this page:** Only solutions page that mentions phone calls, iMessage/SMS texting, and app integrations (Gmail, Sheets, Slack, QuickBooks). Broadest capability scope.

**FAQ (6):**
- Do I need to be technical? (No — plain words, no code)
- Which apps? (Gmail, Google Calendar, Drive, Docs, Sheets, Slack, Notion, Airtable, HubSpot, Outlook, Teams, Calendly, Mailchimp, QuickBooks)
- Can I use my own domain? (Yes, on paid plan)
- Does Ted send things without asking? (Asks first, "On its own" within budget)
- Can I take payments? (Yes — Stripe in your name, 44 countries, no Foundable fee)
- How much does it cost? (Free to start, paid adds credits/domain/payments/social/deeper runs)

---

### 7f. `/solutions/creators` — "Turn followers into a business."

**Hero:**
- Eyebrow: "For creators"
- H1: "Turn followers into a *business*."
- Body: "Ted builds a home for what you make, sells it through your own Stripe account and writes the posts that bring people to it."
- CTAs: "Tell Ted what you make" → sign-up | "See how selling works" → /solutions/selling-online

**3 Features — "From audience to shop" / "Your followers already want more."**
1. **"A shop for what you make"** — Website + products + prices + Buy buttons. Stripe account in your name.
2. **"Posts, ready for your OK"** — Ted writes post + makes picture. Waits for Approve.
3. **"Your accounts, your rules"** — Connect IG, FB, LinkedIn, X, Threads. Set permissions.

**How it works:** Tell Ted what you make (merch, classes, guides, sessions) → Ted builds your shop → Ted helps you launch (posts for approval)

**6-card grid — "What you could start":** Merch shop, Online classes, Paid guides, Coaching calls, Workshops, Fan newsletter

**FAQ (5):**
- Do I need a website? (No, Ted creates one)
- Where does the money go? (Stripe, 44 countries, no Foundable fee)
- Which social accounts? (FB, IG, LinkedIn, X, Threads, TikTok on paid)
- Does Ted post without asking? (Asks first, "On its own" available)
- Do I own it? (Yes, code export on paid plan, domain transferable)

---

### 7g. `/solutions/side-projects` — "Launch it this weekend."

**Hero:**
- Eyebrow: "For side projects"
- H1: "Launch it this *weekend*."
- Body: "Tell Ted the idea on Friday. He builds the website, puts it live and keeps it moving while you're busy with everything else."
- CTAs: "Tell Ted your idea" → sign-up | "See how Ted builds sites" → /solutions/websites

**3 Features — "Small project, real launch" / "You have a day job. Ted works the hours you don't have."**
Uses a **narrative timeline** instead of capability descriptions:
1. **"Friday: tell Ted the idea"** — A sentence is enough. Text from your phone.
2. **"Sunday: it's live"** — Ted builds website, publishes at foundable.app when you say so.
3. **"Monday: it keeps going"** — Start Run. Ted keeps working. Summary waiting when run ends.

**How it works:** Tell Ted the idea (in chat or by text) → Ted builds it → Ted keeps it moving

**6-card grid — "What you could start":** Launch page, Booking site, Newsletter, Small shop, Community, Portfolio

**UNIQUE to this page:** Weekend timeline narrative (Friday/Sunday/Monday). Only page to feature iMessage/SMS as entry point. Fewest FAQ questions (4). Most casual tone.

**FAQ (4):**
- How quickly? (First version in a single conversation)
- Can I use my phone? (Yes — iMessage/SMS + link to Foundable)
- Is there a free plan? (Yes, welcome + daily credits; paid adds domain/payments/social)
- Do I own it? (Yes, code export, domain transferable)

---

### Solutions Pages — Cross-Comparison

| Page | Audience | H1 keyword | Unique angle | Secondary CTA → | FAQ count |
|------|----------|-----------|--------------|-----------------|-----------|
| websites | Anyone needing a site | "live site" | Website building + code export | selling-online | 5 |
| selling-online | Anyone selling | "your site" | Stripe integration, zero Foundable fee | websites | 6 |
| run | Automation-seekers | "being asked" | Autonomous agent with approval gate | marketing | 6 |
| marketing | Growth-focused | "outreach" | Social posting + outreach emails | run | 5 |
| small-businesses | SMB owners | "busywork" | App integrations + phone + broadest scope | marketing | 6 |
| creators | Content creators | "business" | Followers → shop narrative | selling-online | 5 |
| side-projects | Side hustlers | "weekend" | Weekend launch timeline + iMessage | websites | 4 |

**Content reuse:** Several images appear on multiple pages (Instagram connection, post approval, Stripe setup screenshots). FAQ answers about approval, ownership, and pricing are nearly identical, reworded for each audience.

---

## 8. Integrations (`/integrations`)

### Hero

- Integration logos displayed: Gmail, Fathom, Google Drive, Slack, HubSpot, Mailchimp, QuickBooks, Instagram
- **H1:** "Bring the apps you already use."
- **Body:** "Connect them once, and Ted finds, reads, writes and sends in them."

### "How it works" (3 steps)

1. **Connect it** — Settings > Integrations
2. **Ask Ted** — Ted can read, search, and draft in the connected app
3. **Stay in charge** — Ted asks before sending or changing

### "Browse every app" (tabbed filter, 34 integrations)

| Category | Count | Apps |
|----------|-------|------|
| **Email & Calendar** | 4 | Gmail, Google Calendar, Microsoft Outlook, Calendly |
| **Meeting Notes** | 2 | Fathom, Granola |
| **Docs & Files** | 8 | Google Drive, Google Docs, Google Sheets, Notion, Airtable, OneDrive, Excel, Dropbox |
| **Team Chat** | 2 | Slack, Microsoft Teams |
| **Customers & Projects** | 2 | HubSpot, Linear |
| **Marketing & Analytics** | 4 | Mailchimp, Canva, Google Analytics, Google Search Console |
| **Accounting** | 1 | QuickBooks |
| **Social Accounts** | 11 | Instagram, X, Facebook, Google Business, LinkedIn, TikTok, YouTube, WhatsApp, Meta Ads, TikTok Ads, LinkedIn Ads |

### "Built into Foundable" (4 items, not third-party integrations)

1. **Stripe** — Payments
2. **GitHub** — Code versioning
3. **Custom domains** — Own web address
4. **Business email inbox** — foundable.app or custom domain email

### FAQ (6 questions)

1. How do I connect an app? (Settings > Integrations, one click)
2. What can Ted do in connected apps? (Read, search, draft changes — sends on approval)
3. Who can connect integrations? (Account owner and admins)
4. Can I disconnect? (Yes, instantly ends access)
5. Does Ted store my passwords? (No — OAuth tokens, revocable)
6. Which social networks? (Instagram, Facebook, LinkedIn, X, Threads, TikTok on paid plans)

---

## 9. Ideas (`/ideas`)

### Hero

- **H1:** "Start a business with Ted."
- **Body:** "Ideas Ted can build and run for you today. Pick one, or bring your own."

### Filterable Card Grid (15 ideas across 5 categories)

**Filter tabs:** All (15), Sell what you make (3), Offer a service (3), Share what you know (3), Run a local business (3), Build a tool (3)

| Category | Ideas |
|----------|-------|
| **Sell what you make** | Shop for your work, Made to order, Classes & workshops |
| **Offer a service** | Coaching & tutoring, Freelance work, Home service |
| **Share what you know** | Newsletter, Online course, Creator brand |
| **Run a local business** | Café & bakery, Studio & gym, Street shop |
| **Build a tool** | Directory & listings, Booking app, Team app |

Each card shows:
- Integration logos relevant to that idea
- Heading
- Short description
- Category tag

### Bottom CTA

"Have an idea of your own?" → sign-up

### FAQ (4 questions)

1. What if I don't have an idea? (Ted can suggest one)
2. What does Ted do after I pick? (Plans → builds → runs)
3. Do I need to code? (No)
4. Can I accept payments? (Yes, via Stripe)

---

## 10. Blog (`/blog`)

### Index Page

- **Eyebrow:** "Foundable blog"
- **H1:** "Guides and updates."
- **Body:** "How to turn an idea into something people can use, reach them, and get paid."
- **Filter tabs:** All, Agents, Build, Company, Payments

### 18 Blog Posts (vertical card list)

Each card shows: category tag, date, title, description. Date range: October 29 – November 4, 2026.

**By category:**
- **Agents (12 posts):** Heavy competitive comparison content — vs Lovable, vs ChatGPT, vs Durable, vs Lindy, vs NanoCorp, vs Sintra, vs Wix, vs Zapier Agents, vs Polsia, vs Marblism, plus "Polsia alternatives" and "Is Polsia worth it?"
- **Build (3 posts):** "AI business builder", "Make money from idea with AI", "Lovable app first customers"
- **Payments (2 posts):** "AI business builder fees", "Switch to Foundable"
- **Company (1 post):** "Is Foundable legit?"

### Blog Post Template (consistent across all posts)

```
Breadcrumb: Blog > [Category]
[Category tag]
H1: [Title]
Published [date] · Updated [date]
No author name displayed

[Bias disclosure + TL;DR section]

~9 H2 sections:
- Competitor praise / what they do well
- Own pitch / how Foundable differs
- Pricing comparison
- Coexistence acknowledgment
- Concession (what competitor does better)
- Disqualification (where competitor falls short)
- Decision checklist

Bold-labeled bullet lists throughout.
No images, tables, or charts in body.
Inline CTA paragraph at end.
No sidebar. No comments. No share buttons.
```

---

## 11. Community (`/community`)

### Hero

- 4 community event photos displayed
- **H1:** "Build alongside other owners."
- **Body:** "5,000+ people share what they're making with Foundable."
- Two CTAs: "Join us on Discord", "Follow on X"

### "Connect" section

Inline text with social icons: Discord, X, Instagram, LinkedIn, Threads

### "Ways to get involved" (4 cards)

1. **The Discord** — Hosted by the team
2. **Share what Ted built** — One-tap sharing on publish
3. **Help center** — docs.foundable.com
4. **The blog** — Guides and updates

### Community links sidebar

Discord, Help center, Blog, Contact, Press + social icons

### "Latest from Foundable" (3 blog post cards)

Displays 3 recent comparison posts (vs Marblism, vs ChatGPT, vs Durable)

### FAQ (4 questions)

1. Do I need an account? (No, Discord is open)
2. Do I need technical skills? (No)
3. Is it free? (Yes)
4. Who runs the community? (The Foundable team)

### Pre-footer CTA

Ted mascot illustrations. "Come say hi in the Discord."

---

## 12. Press (`/press`)

### Hero

- **H1:** "Foundable press and brand resources."
- CTA: "Contact Foundable" → `/contact`

### Boilerplate

"Foundable is an AI platform where Ted, your AI employee, turns your idea into something real, runs the business for you, and helps it earn."

### Company Facts Table

| Field | Value |
|-------|-------|
| Product | Foundable (foundable.com) |
| Operated by | Autono Labs, Inc. |
| Founded | April 10, 2026 |
| HQ | San Francisco |
| Co-founders | Stefan Stoll and Wesley Lin |
| Availability | Live, free accounts |
| Press contact | support@foundable.com |

### Logo & Brand Resources

- Usage guidelines: no redrawing, recoloring, or stretching
- Product name = "Foundable" (proper noun, always capitalized)
- AI employee = "Ted" (always referred to by name)
- Downloads: Logo PNG (512px), Wordmark PNG

### Public Profiles

Links to: X, LinkedIn, Instagram, Threads, GitHub

### FAQ (3 questions)

1. What is Foundable?
2. Is it publicly available? (Yes)
3. Where to download logo?

---

## 13. Careers (`/careers`)

### Hero

- **H1:** "Build the idea-to-profit company."
- **Body:** Describes Foundable's mission — taking an idea to a business that earns.
- CTA: "Contact us" → `/contact`

### Current Openings

**None listed.** Text directs to contact page for general inquiries.

### "How we work" (4 principles)

1. **"Simple on the surface, serious underneath"**
2. **"Make useful things feel alive"**
3. **"Proof before polish"**
4. **"One owner per decision"**

### "Areas we expect to build across"

Listed as future areas, not current openings:
- Product engineering
- AI systems
- Design
- Growth
- Customer development and operations

### FAQ (2 questions)

1. What kind of people? (Product engineering, AI, design, growth, ops)
2. How to get in touch? (Via contact page or job listing when posted)

---

## 14. Contact (`/contact`)

### Hero

- **H1:** "Get in touch."
- **Body:** "Write to the inbox for your topic and a person will reply by email."
- Primary CTA: mailto:support@foundable.com

### Inbox Directory (table layout)

| Topic | Email |
|-------|-------|
| Support, pricing and product | support@foundable.com |
| Press, partnerships and hiring | support@foundable.com |
| Billing and refunds | support@foundable.com |
| Legal questions | legal@foundable.com |
| Privacy questions | privacy@foundable.com |
| Security issues | security@foundable.com |
| Reporting abuse | abuse@foundable.com |
| Copyright (DMCA) | dmca@autono.sh |

### Mailing Address

Autono Labs, Inc. (re: Foundable)
131 Continental Drive, Suite 305
Newark, DE 19713, USA

### "Before you write"

Links to: Security page, Legal/policies, Responsible disclosure

**No web forms on this page — entirely email-based contact.**

---

## 15. Legal Hub & Legal Documents

### `/legal` — Legal Index

- **H1:** "Legal & Policies"
- Last updated: October 31, 2026

**"For everyone" (8 documents):**
Terms of Service, Privacy Policy, Acceptable Use Policy, Refund & Dispute Policy, AI Disclosure, Cookie & Tracking Notice, Data Deletion Instructions, Domain Holding Agreement

**"For businesses" (3 documents):**
Security, Subprocessors and Data Recipients, Data Processing Addendum

**"Reporting" (2 documents):**
Responsible Disclosure Policy, DMCA Notice & Takedown

**"A note on names":** Foundable = product, Autono Labs, Inc. = legal entity. Email handles: @foundable.com and @autono.sh.

**Contact directory (7 inboxes):** legal@, support@, privacy@, security@, abuse@, dmca@autono.sh

**Total: 13 legal documents.**

---

### `/ai-disclosure` — AI Disclosure

*Last updated: October 30, 2026. 8 sections of plain prose.*

**"Ted is AI":** "Ted is software powered by AI, not a person, even when talking with him feels natural." Support chat may involve real team members.

**"What powers Ted":** Models from OpenAI and Anthropic, plus specialized services for images, search, and conversation memory. Full provider list on subprocessors page.

**"What Ted can do":**
- Read user messages, files, connected apps, and websites
- Search the web
- Plan and execute work (websites, writing, images, videos)
- Act within connected services (posting, emailing, texting) per user-set permissions
- Recall prior chats within the same foundable (business)

**"What Ted can't do":**
- Access unconnected devices/accounts
- Guarantee accuracy
- Substitute for licensed professionals
- Reverse actions in external services
- Share knowledge between different foundables

**"Your content and AI training":** "We don't train AI models on your content." API terms from OpenAI and Anthropic similarly prohibit using processed content for model training.

**"Check Ted's work":** Output "can be wrong, out of date, biased, or not right for your audience" and he "can even invent facts, names or sources." Users must review before publishing.

**"Report a problem":**
- abuse@foundable.com → harmful output
- support@foundable.com → wrong/biased output
- security@foundable.com → safety-rule circumvention

**"AI laws":** No compliance certification for EU AI Act or US state AI laws. "You're responsible for the notices, reviews and labels your own use requires."

---

### `/refund-policy` — Refund & Dispute Policy

*Last updated: October 30, 2026. 8 numbered sections.*

**"The short version":** "Pay only for what you meant to buy." Payments processed through Link (a Stripe service) as seller of record.

**Plans:** Billed monthly or yearly in advance. Cancel anytime via Settings → Plans & credit usage → Manage billing, or at link.com. Plan stays active through paid period. **"We generally don't refund or prorate the current period."** Deleting account ends plan immediately, no refund.

**Credits:** "Generally non-refundable once added" because immediately usable. Full refund/reversal of a credit pack → unused credits removed. Credits expire 12 months after purchase (unless never-expiring). Expired credits not refunded. Cannot be exchanged for cash.

**How to request:** Email support@foundable.com with charge date, amount, purchase, and what went wrong. 3 business day reply target. Refund goes to original payment method. Link may also refund within 60 days under its own policy.

**Bank disputes:** Accounts placed on hold during dispute (work stops, credits frozen, plan canceled). If reversed, unused credits from that payment removed. Resolution in Foundable's favor → support lifts hold after confirmation.

**"Legal rights":** "Where the law gives you more, the law wins."

---

### `/subprocessors` — Subprocessors and Data Recipients

*Last updated: November 6, 2026. Table format.*

**26 customer-data subprocessors:**

| # | Provider | Role | Location |
|---|----------|------|----------|
| 1 | **OpenAI** | Core AI — Ted's conversation, onboarding, research, embeddings, website AI | US |
| 2 | **Anthropic** | Chat, paid runs, helpers (summaries, posts, logos, brand reads, product pics), Build agents, Inbox drafts, video composition | US (stored); processing US/Europe/Asia/Australia |
| 3 | **fal.ai** | Image and sound generation (GPT Image, ElevenLabs) | Provider infrastructure |
| 4 | **Google Cloud** | Video generation (Gemini Omni model) | Google Cloud global |
| 5 | **Perplexity AI** | Web search for research and website AI | Provider locations |
| 6 | **Monid Inc.** | Public data lookups (social, reviews, listings, email deliverability via Hunter) | US (San Francisco) |
| 7 | **TypeSafe AI** | Reasoning level selection per reply, first-message checks | US (San Francisco) |
| 8 | **Turbopuffer** | Chat recall — search index over older chats | AWS us-west-2 |
| 9 | **Mobbin** | Design references for Build website planning | Provider locations |
| 10 | **Judgment Labs** | AI quality analytics — model/tool call tracing | Provider locations |
| 11 | **AWS** | Core infrastructure — ECS Fargate, Aurora PostgreSQL, S3, secrets, logs, CloudFront | us-west-1 + global CDN |
| 12 | **Cloudflare** | Publishing — foundable.app sites, R2 storage, Workers, screenshots | Global |
| 13 | **Temporal Technologies** | Durable workflows — Ted turns, Build runs, delivery, scheduled runs | Temporal Cloud region |
| 14 | **Modal Labs** | Sandboxes — Build authoring/compiling, workspace commands, video rendering | Modal infrastructure |
| 15 | **Pierre Computer Company** | Website code — Git repository per website | Pierre infrastructure |
| 16 | **Supabase** | Website backends — database, storage, visitor sign-in per site | AWS us-west-1 |
| 17 | **WorkOS** | Authentication — Google, Apple, email code, sessions | US |
| 18 | **Stripe** | Billing + Foundable Payments — checkout, subscriptions, merchant accounts | Stripe/payment-network locations |
| 19 | **AgentMail** | Inbox — mailboxes on foundable.app or custom domains | US and EU |
| 20 | **Linq** | Texting — iMessage/SMS for linked phone accounts | US |
| 21 | **ZERNIO SOFTWARE SL** | Social publishing, managed campaigns, phone numbers | Spain/EU |
| 22 | **Sampark Inc (Composio)** | Connected apps — credentials, reads, approved actions | Provider locations |
| 23 | **Intercom** | Customer support — Messenger, conversation history | US |
| 24 | **Mailgun (Sinch)** | Email delivery — sign-in codes, invitations, notices, newsletters | US |
| 25 | **PostHog** | Product analytics — events, session recordings (values masked) | US or EU |
| 26 | **Sentry** | Error monitoring — errors, stack traces (headers/bodies/credentials stripped) | Project region |

**Recipients under their own terms (not subprocessors):** Connected integrations, Meta (campaigns + measurement), OpenAI (ad measurement), Google (sign-in, listings), GitHub (setup research), Stripe (fraud/compliance/tax).

---

### `/terms` — Terms of Service

*Last updated: November 6, 2026. 18 numbered sections with clickable TOC.*

**Key sections:**

| Section | Summary |
|---------|---------|
| **§3 Your Account** | Min age 16, no VPN workaround for geo-restrictions, US sanctions compliance |
| **§5 Your Content (IP)** | "You own what you put into Foundable and what Ted makes for you... to the extent the law allows." Broad operational license granted. "We don't train AI models on your content, and we don't sell it." |
| **§6 Connected Apps** | Users responsible for Ted's actions in connected services. Stripe-powered payments — "We aren't the seller and take no fee; Stripe charges its own." |
| **§7 AI Output** | "Ted's work is created by AI. It can be wrong, out of date or unsuitable... and it can resemble what Ted makes for other people." |
| **§8 Credits** | Plan credits expire monthly (Pro/Max carry 1 month). Credit packs expire 12 months. "Credits have no cash value, can't be transferred or used outside Foundable." |
| **§10 Our Property** | "You may not copy or take apart our software, use Foundable to build a competing product or train a competing AI model." |
| **§13 Liability** | Capped at greater of 12-month spend or US$100. No consequential damages. |
| **§17 Disputes** | Mandatory individual binding arbitration (AAA). Class action waiver. 30-day opt-out window. Delaware law. |

---

### `/privacy` — Privacy Policy

*Last updated: November 6, 2026. 17 numbered sections.*

**Data collected:**
- Account: email, name, photo, phone
- User content: messages, files, websites, posts, mail, calls, videos, connected app data
- Billing info
- Support messages
- Automatic: usage data, session recordings (screens, clicks, scrolls, typed text including unsent drafts — passwords/payment fields masked), device info, IP
- From others: sign-in providers, connected apps, public web searches

**How used:** Running the service, AI output generation, security, payments, support, product improvement, legal obligations.

**Sharing:** Service providers (under contract), Stripe (payments), connected apps, Meta/Google/OpenAI (marketing measurement — respects Global Privacy Control). "We don't sell personal information or share it with data brokers."

**Retention:** Account/content deleted immediately on account deletion. Backups up to 60 days. Service logs 30 days. Visitor analytics 90 days. Billing records persist for legal obligations.

**Notable:** Session recordings capture typed text including unsent drafts. Google/Microsoft API data gets heightened Limited Use protections.

---

### `/acceptable-use` — Acceptable Use Policy

*Last updated: October 30, 2026. 9 sections of bulleted prohibited activities.*

| Category | Prohibitions |
|----------|-------------|
| **Don't Harm People** | No CSAM, harassment, non-consensual imagery, hate speech, violence promotion, weapons assistance, self-harm encouragement |
| **Don't Deceive People** | No impersonation/deepfakes, scams/phishing, fake engagement, disinformation/election manipulation, forged documents |
| **Don't Break the Law** | No IP theft, mass profiling, biometric surveillance, malware/hacking, spam, money laundering, sanctions evasion |
| **Don't Misuse Foundable** | No limit circumvention, prompt extraction, unauthorized reselling, training competing AI, overloading, jailbreaking (except good-faith security research) |
| **Decisions About People** | Cannot be sole basis for high-stakes decisions (health, legal, employment, credit, housing, education). Criminal justice entirely forbidden. |
| **Sensitive Data** | No HIPAA data, full card numbers, student records, classified data, children's data without written agreement |

---

### `/responsible-disclosure` — Responsible Disclosure Policy

*Last updated: October 25, 2026. 10 numbered sections.*

**Scope:** foundable.com, login.foundable.com, preview.foundable.app, *.foundable.app. Customer websites and third-party systems are out of scope.

**In-scope:** XSS, CSRF, SQL injection, auth bypasses, privilege escalation, SSRF, RCE, significant misconfigs.

**Out-of-scope:** Best-practice findings without PoC, rate-limit observations, DoS, social engineering, physical attacks, clickjacking on non-sensitive pages, missing cookie flags, zero-days with patches <30 days.

**AI-safety testing:** Jailbreak, prompt-injection, cross-foundable context, and unsafe-agent-action findings accepted. Test only against own accounts/content.

**Reporting:** Email security@foundable.com. One vulnerability per report. Acknowledgment within 3 business days.

**Safe harbour:** "We will not initiate legal action based solely on that research."

---

### Other Legal Pages (summarized)

- **`/dmca`** — DMCA Notice & Takedown process. Send to dmca@autono.sh with required statutory info.
- **`/cookies`** — Cookie & Tracking Notice. Session cookies, analytics (PostHog), support (Intercom).
- **`/legal/domain-holding-agreement`** — Terms for Foundable holding a custom domain on user's behalf.
- **`/legal/security`** — Detailed security policy (expanded version of the `/security` page).
- **`/data-deletion`** — Instructions for deleting account and all data.
- **`/dpa`** — Data Processing Addendum for business users.

---

## 16. Auth & App Pages

### `/sign-up` — Sign Up

- **Heading:** "Start free."
- **Two OAuth buttons:** "Continue with Google" | "Continue with Apple"
- **Divider:** "or"
- **Email field** + "Continue" button (sends magic code, no password)
- **Legal text:** "By continuing, you agree to Foundable's Terms of Service and acknowledge the Privacy Policy and Refund Policy."
- **Link:** "Already have an account? Log in" → `/sign-in`
- **No GitHub OAuth. No password field. Entirely passwordless.**

### `/sign-in` — Log In

- **Heading:** "Log in."
- **Same two OAuth buttons:** "Continue with Google" | "Continue with Apple"
- **Same email field** + "Continue" button
- **Link:** "Don't have an account? Sign up" → `/sign-up`
- **Same legal footer as sign-up**
- **Identical layout to sign-up** — only the heading and bottom link text differ

### App Routes (behind authentication)

Attempting to access `/home`, `/build`, `/run`, `/start` shows a **"Loading Foundable" splash screen** with Ted mascot (day/night variants based on time). No app UI visible without authentication.

**All known app routes (from robots.txt):**

| Route | Likely Purpose |
|-------|---------------|
| `/home` | Main dashboard / home screen |
| `/build` | Website building interface |
| `/run` | Autonomous agent mode |
| `/grow` | Marketing / growth tools |
| `/inbox` | Business email inbox |
| `/library` | Asset library |
| `/schedule` | Content calendar / scheduling |
| `/settings` | Account settings, integrations |
| `/start` | New business creation |
| `/new` | New project creation |
| `/line` | Communication channel |
| `/f/` | Published foundable pages |
| `/admin` | Admin panel |
| `/checkout/` | Payment flow |
| `/companies/` | Business management |
| `/account/` | Account management |
| `/invite/` | Team invitations |
| `/join` | Team join flow |
| `/welcome/` | Onboarding |
| `/open-gift` | Gift/promo redemption |
| `/open-line` | Communication channel opening |
| `/signed-out` | Post-logout page |
| `/imessage/` | iMessage integration |

---

## 17. Documentation Site (`docs.foundable.com`)

Hosted on **Mintlify**. Has top-level tabs: **Home, Build, Run.**

### Changelog (`docs.foundable.com/changelog`)

- **Title:** "What's new"
- **273 entries** from October 6 – November 7, 2026 (~6 weeks)
- Reverse chronological. ~6–7 features shipped per day.

**Major capabilities added (chronological):**
Security scans → website building → inline text editing → payment processing →
social posting → GitHub sync → app integrations → scheduling → cart/shipping →
email system → AI website features → Run mode (autonomous agent) → WhatsApp →
phone answering → video creation → ad campaigns (Meta, Google, TikTok, LinkedIn,
Pinterest) → domain purchasing → iMessage/SMS texting → referral program →
credit system refinements → 34 language support.

**Shipping velocity:** ~273 updates in ~32 days = **8.5 shipped changes per day.**
This is an extremely aggressive pace for a 7-month-old company.

### Documentation Categories

| Path | Topics |
|------|--------|
| `/get-started/` | Quickstart, starting a business, find your way around, Home screen |
| `/build/` | Website building overview, publishing |
| `/run/` | Autonomous operation, ask-first vs on-its-own |
| `/ted/` | Meet Ted, approvals, autonomous actions, work-or-chat mode |
| `/domains/` | Custom web addresses |
| `/payments/` | Stripe integration, sales |
| `/account/` | Plans and credits |
| `/help/` | FAQ, glossary, getting help |

### Homepage Structure

- 4 onboarding cards: Create account, First website, Start business, Navigation
- 3 basics cards: Home, Build, Run
- 6 top questions: Publishing, Autonomy, Domains, Payments, Approvals, Pricing
- Help section: Live chat, FAQ, Contact

### Additional

- Full machine-readable index at `docs.foundable.com/llms.txt`
- Changelog at `docs.foundable.com/changelog`

---

## 18. Structural Patterns & Takeaways

### Site-Wide Patterns

1. **Consistent template system** — Solutions pages all share an identical skeleton (hero → 3 features → 3 steps → 6-card grid → FAQ → CTA). Content is unique per page but structure is identical.

2. **Ted as the central character** — Every page frames the product through "Ted," the AI persona. He's never called "the AI" or "our system." He's "Ted" — an employee, not a tool. Consistent anthropomorphization.

3. **Approval-first messaging** — Nearly every page reinforces: "Ted asks before anything goes out." The autonomy permission model ("Ask First" vs "On its own") is explained on almost every solutions page.

4. **"No Foundable fee" on payments** — Repeated across selling-online, creators, small-businesses: Stripe handles payments directly into the user's account. Foundable takes zero transaction fee. Revenue comes from subscriptions/credits only.

5. **Credit-based economics** — Everything Ted does costs credits. Free tier gets 5/day + 15 welcome. Paid tiers get 200–10,000/mo. Credit packs available one-time. Pro/Max carry unused credits 1 month.

6. **USD-only pricing** — All prices in USD. No local currency support. Payment via Link (Stripe). This is a gap for African markets.

7. **Passwordless auth** — No passwords anywhere. Google, Apple, or email code only. WorkOS handles auth.

8. **No team bios** — About page and press page mention co-founders Stefan Stoll and Wesley Lin by name but show no photos, bios, or team section.

9. **Aggressive SEO/comparison content** — 12 of 18 blog posts are "Foundable vs X" comparison articles. Clear SEO strategy targeting competitor searches.

10. **36-language internationalization** — Every public page available in 36 locales. Broad global ambition.

### Technical Infrastructure (from subprocessors)

- **AI:** OpenAI (primary for conversation), Anthropic (chat, paid runs, builds, social), fal.ai (images), Google Cloud (video)
- **Infra:** AWS (ECS Fargate, Aurora PostgreSQL, S3, CloudFront), Cloudflare (site hosting, R2, Workers)
- **Workflows:** Temporal (durable workflows), Modal Labs (sandboxes)
- **Website backends:** Supabase (database, storage, auth per generated site)
- **Code:** Pierre Computer Company (Git repos per website), GitHub (code versioning)
- **Auth:** WorkOS (Google, Apple, email code)
- **Payments:** Stripe (billing + merchant accounts)
- **Email:** AgentMail (inbox), Mailgun (transactional)
- **Texting:** Linq (iMessage/SMS)
- **Social:** ZERNIO SOFTWARE SL (publishing, campaigns, phone numbers), Composio (connected app credentials)
- **Search:** Perplexity AI (web search)
- **Analytics:** PostHog (product analytics), Sentry (errors), Judgment Labs (AI quality)
- **Support:** Intercom (customer support)
- **Meeting notes:** Fathom, Granola integrations
- **Design refs:** Mobbin (design references for website planning)
- **Chat memory:** Turbopuffer (vector search over old chats)

### What's Notable for Cre8ive District

1. **Credit model vs. project pricing** — Foundable charges per-credit (activity-based), we charge per-project (deliverable-based). Different economics, different user expectations.

2. **USD-only = Africa gap** — No naira, no bank transfer, no USSD. This is our opening.

3. **No human layer** — Foundable is pure AI. No designer review, no human refinement option. Our human team is a differentiator.

4. **Ted as employee, not tool** — The persona framing is strong. Worth studying: they never break character.

5. **Run mode** — Autonomous agent that works without being asked, then asks for approval. This is their most differentiated feature.

6. **26 subprocessors** — Heavy third-party dependency. Their stack is sophisticated but complex.

7. **Founded April 2026** — Only 7 months old. 14,000+ signups. Moving fast.

8. **No mobile app** — Web only + iMessage/SMS. No dedicated iOS/Android app.

9. **Stripe Connect for user payments** — Users get their own Stripe account, Foundable takes no fee. Revenue is purely subscription.

10. **44 Stripe countries** — Many African countries not in Stripe's supported list. Another gap we fill with Paystack.
