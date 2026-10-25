# Cre8ive District — Ads & Promotion Department Playbook

> A Graceman IT Concepts Company | Lagos, Nigeria  
> Version 1.0 | October 2026

---

## Table of Contents

1. [Platform Breakdown](#1-platform-breakdown)
2. [Service Packages](#2-service-packages)
3. [Campaign Workflow](#3-campaign-workflow)
4. [Creative Best Practices for Nigeria](#4-creative-best-practices-for-nigeria)
5. [Tools & Tech Stack](#5-tools--tech-stack)
6. [Pricing & Revenue Model](#6-pricing--revenue-model)
7. [Common Pitfalls & How to Avoid Them](#7-common-pitfalls--how-to-avoid-them)
8. [Case Study Templates](#8-case-study-templates)

---

## 1. Platform Breakdown

### 1.1 Meta Ads (Facebook & Instagram)

**The most important platform for Nigerian businesses.** Nigeria has ~33 million Facebook users and ~11 million Instagram users. Meta ads offer the widest reach at the lowest CPM in the market.

#### Account Structure
```
Ad Account
└── Campaign (objective)
    └── Ad Set (audience + budget + placement)
        └── Ad (creative + copy + CTA)
```

Always use **one objective per campaign**. Never mix objectives (e.g. don't put a conversion ad in a traffic campaign).

#### Campaign Objectives — When to Use Each

| Objective | Use When | Expected Outcome |
|---|---|---|
| **Awareness** | New brand, launching into a new market | Reach, impressions, video views |
| **Traffic** | Drive people to a website or landing page | Link clicks, landing page views |
| **Engagement** | Grow page likes, boost post reach, promote events | Post interactions, event responses |
| **Leads** | Collect contact info without a website | Form fills (name, phone, email) — great for Nigerian SMEs without a landing page |
| **App Promotion** | Drive installs for a client's mobile app | App installs, in-app events |
| **Sales / Conversions** | Website purchases, form submissions, sign-ups | Purchase events, conversion events — requires Pixel |

**For most Nigerian SME clients: start with Lead Generation.** It's the lowest friction (no website needed), works with WhatsApp lead forms, and produces an actionable contact list the client can follow up on directly.

#### Audience Targeting Options

**Core Audiences (Demographics)**
- Location: Target by country, state, city, or radius (e.g. "people within 10km of Victoria Island, Lagos")
- Age & gender: Essential for fashion, beauty, food, fitness clients
- Detailed interests: Target fans of competitors, relevant interests (e.g. "Jumia", "Konga", "MTN", "GTBank")
- Behaviors: Online shoppers, engaged shoppers, mobile device users

**Custom Audiences (Retargeting)**
- Website visitors (requires Pixel — standard 30/60/90-day windows)
- Video viewers (anyone who watched 25%/50%/75% of a video ad)
- Page engagers (anyone who interacted with the Facebook/Instagram page in the last 180 days)
- Customer list (upload phone numbers or emails from WhatsApp/CRM — Meta matches to accounts)

**Lookalike Audiences (Scale)**
- Built from any Custom Audience
- 1% LAL = most similar to source (higher quality, smaller size)
- 3-5% LAL = broader reach at slightly lower relevance
- Always start with 1% from your best custom audience (e.g. past purchasers or highest-value leads)

#### Ad Formats

| Format | Best For | Notes |
|---|---|---|
| **Single image** | Simple offers, announcements, brand awareness | Fastest to produce, test first |
| **Video (15-60s)** | Product demos, testimonials, storytelling | Hook in first 3 seconds. Square (1:1) or vertical (9:16) for mobile |
| **Carousel** | Showcasing multiple products/services, before/after | Good for fashion, food, real estate |
| **Stories / Reels** | Younger audiences, viral potential | Must be 9:16 vertical. High-energy, fast-paced |
| **Collection** | E-commerce product catalogues | Requires Catalogue setup |
| **Lead Form** | Collecting contacts without a website | Instant forms fill out inside Meta — very high conversion rate in Nigeria |

#### Meta Pixel Setup (Essential for any website client)
1. Create Pixel in Events Manager
2. Install on client website (via manual code or Google Tag Manager)
3. Set up standard events: PageView, ViewContent, Lead, Purchase
4. Verify with Meta Pixel Helper Chrome extension
5. Allow 7-14 days for the Pixel to warm up before running conversion campaigns

#### Nigerian Market Benchmarks (approximate, 2026)

| Metric | Typical Range |
|---|---|
| CPM (cost per 1,000 impressions) | ₦500 – ₦2,500 |
| CPC (cost per link click) | ₦80 – ₦400 |
| CPL via Lead Form | ₦200 – ₦800 |
| Video CPV (cost per 3-second view) | ₦20 – ₦80 |
| ROAS (return on ad spend) for e-commerce | 2x – 6x (target 3x+ to be profitable) |

> Costs spike significantly in Q4 (October–December) due to holiday competition. Plan client budgets accordingly.

#### Bidding Strategies

- **Lowest Cost (automatic):** Default. Best for starting out and testing. Meta finds the cheapest results.
- **Cost Cap:** Set a max CPL. Good when client has a specific cost-per-lead target.
- **Bid Cap:** Manual control for experienced media buyers. Rarely needed for most clients.
- **Value Optimization:** For e-commerce with purchase events — Meta optimizes for highest-value buyers.

---

### 1.2 TikTok Ads

**Fast-growing in Nigeria.** TikTok has 12+ million Nigerian users, skewed 18–34. Excellent for fashion, food, beauty, entertainment, fitness, and anything with strong visual appeal.

#### Account Setup
1. Create TikTok Business Account at ads.tiktok.com
2. Install TikTok Pixel on client site (similar to Meta Pixel)
3. Connect to TikTok Business Center for agency management

#### Campaign Types

| Campaign | Best For |
|---|---|
| **In-Feed Ads** | Standard video ads that appear in the "For You" feed — most versatile |
| **TopView** | 60-second video at the top of the feed when app opens — high impact, higher cost |
| **Brand Takeover** | Full-screen on app open — premium, typically for large brands |
| **Branded Hashtag Challenge** | UGC campaigns — drives organic participation |
| **Spark Ads** | Boost existing organic TikTok posts as ads — highest authenticity signal |

**For most Cre8ive District clients: In-Feed Ads and Spark Ads** are the right entry points.

#### Creative Best Practices for TikTok
- **Native-first:** Ads that look like TikToks perform far better than ads that look like ads
- **Hook in 0-2 seconds:** Open with the most interesting/surprising moment, not a logo
- **Vertical 9:16, minimum 720p**
- **Music matters:** Use trending sounds (within licensing rights) or upbeat original audio
- **Text overlays:** Many people watch without sound — add subtitles or key text on screen
- **Duration:** 15-30 seconds is the sweet spot for most products
- **Spark Ads:** If a client already has an organic TikTok that performed well, run it as a Spark Ad — it keeps the real engagement count visible

#### TikTok Nigerian Market Notes
- Audience is younger (18–34) vs Meta's broader demographic
- Food, fashion, comedy, and "transformation" content perform extremely well
- Pidgin English and local slang in copy improves relatability
- Costs are generally 20-40% lower CPM than Meta — good for reach campaigns

---

### 1.3 Google Ads

Best for **search-intent traffic** — clients whose customers are actively searching for what they sell. Less relevant for brand building, more relevant for service businesses (lawyers, doctors, schools, repair services).

#### When to Recommend Google Ads
- Client has a service people actively search for ("web developer Lagos", "event venue Abuja")
- Client has an e-commerce store and wants bottom-of-funnel traffic
- Client needs local foot traffic (Google Maps / Local campaign)

#### Campaign Types

| Type | Use Case |
|---|---|
| **Search** | Text ads triggered by keywords. Best ROI for high-intent searches |
| **Display** | Banner ads across Google's network. Brand awareness, retargeting |
| **YouTube** | Video ads before/during YouTube videos. Skippable (TrueView) or bumper (6s) |
| **Performance Max** | Google's AI-driven campaign across all placements. Good for e-commerce |
| **Local** | Drive calls and map visits for physical businesses |

#### Keyword Strategy for Nigerian Businesses
- Focus on **local modifiers**: "in Lagos", "in Abuja", "in Port Harcourt", "Nigeria"
- Long-tail keywords are less competitive and cheaper: "affordable wedding photographer Lagos" vs. "photographer"
- Exclude irrelevant terms with **negative keywords** from day one (e.g. "free", "DIY", "tutorial")
- Use **phrase match** and **exact match** — avoid broad match until you understand your traffic

#### Budget Guidance
- Google Ads are generally more expensive per click than Meta in Nigeria
- Minimum meaningful test budget: ₦50,000/month for Search
- Keyword CPCs range from ₦150 (low competition) to ₦2,000+ (legal, financial, medical)

---

### 1.4 Twitter/X Ads

**Limited utility for most Nigerian SME clients.** Twitter/X Nigeria has an active user base but the ads platform is expensive relative to Meta with lower conversion rates for most consumer products.

**When it makes sense:**
- B2B clients targeting tech, finance, or media professionals
- PR campaigns targeting journalists, influencers, thought leaders
- Cultural moments (events, sports, pop culture activations)

**When to skip it:** For most product/service clients at the SME level, the budget is better spent on Meta and TikTok.

---

### 1.5 LinkedIn Ads

**B2B only.** Relevant for Cre8ive District clients who sell to other businesses (HR software, financial services, professional services, SaaS).

**Key formats:** Sponsored Content (posts in feed), Message Ads (InMail), Lead Gen Forms  
**Cost:** Expensive — Nigerian LinkedIn CPCs are typically ₦800–₦3,000+  
**Minimum budget to test:** ₦100,000/month  

**Recommendation:** Unless a client is clearly B2B with a professional audience and a high-ticket offer, steer them toward Meta/TikTok/Google first.

---

## 2. Service Packages

### Package Tiers

#### Starter — Social Ads Management
**Best for:** Small businesses with a single location, early-stage startups, proof-of-concept campaigns  
**Ad Spend Range:** ₦50,000 – ₦150,000/month (client pays directly)  
**Our Management Fee: ₦150,000/month**

| What's Included | Detail |
|---|---|
| Platform | Meta (Facebook + Instagram) only |
| Ad creatives | 4 designed image/video ads per month |
| Campaign setup | 1 active campaign with 2-3 ad sets |
| Targeting | 1 audience strategy + 1 retargeting audience |
| Reporting | Monthly performance report |
| Communication | WhatsApp updates, monthly review call |
| Contract | 3-month minimum |

---

#### Growth — Multi-Platform Management
**Best for:** Established SMEs ready to scale, businesses with a proven offer  
**Ad Spend Range:** ₦150,000 – ₦600,000/month  
**Our Management Fee: ₦250,000/month**

| What's Included | Detail |
|---|---|
| Platforms | Meta + TikTok (or Meta + Google) |
| Ad creatives | 8 designed assets per month (images + 2 short videos) |
| Campaign setup | 2 active campaigns, full A/B testing |
| Targeting | 3 audience segments + lookalike audiences |
| Pixel / tracking | Setup and event configuration |
| Reporting | Weekly performance snapshots + monthly deep-dive |
| Strategy call | Bi-weekly 30-min calls |
| Contract | 3-month minimum |

---

#### Premium — Full-Funnel Ad Strategy
**Best for:** Brands with serious ad budgets and growth goals  
**Ad Spend Range:** ₦600,000+/month  
**Our Management Fee: ₦450,000/month**

| What's Included | Detail |
|---|---|
| Platforms | Meta + TikTok + Google (all three) |
| Ad creatives | 15+ assets/month (static, video, carousel, stories) |
| Campaign structure | Full funnel: awareness → consideration → conversion |
| Audiences | Full audience architecture (cold, warm, retargeting, lookalike) |
| Landing pages | Basic landing page design/optimization included |
| Tracking | Full GA4 + Meta Pixel + TikTok Pixel setup |
| Reporting | Weekly reports + monthly strategy review |
| Dedicated manager | Single point of contact, priority response |
| Contract | 3-month minimum, monthly thereafter |

---

#### Add-ons (Any Package)

| Add-on | Price |
|---|---|
| Extra ad creative (image) | ₦15,000 per asset |
| Extra ad creative (video, 15-30s) | ₦35,000 per asset |
| Landing page design | ₦120,000 one-time |
| Meta/TikTok Pixel setup | ₦40,000 one-time |
| Google Analytics 4 setup | ₦50,000 one-time |
| Campaign audit (existing account) | ₦75,000 one-time |
| Platform add-on (e.g. add Google to Starter) | ₦80,000/month |

---

## 3. Campaign Workflow

### Phase 1: Client Audit (Week 0)

Before touching any ad account:

**1. Business & Brand Audit**
- [ ] What does the client sell and who is the target customer?
- [ ] What is the unique selling proposition? Why choose them over competitors?
- [ ] Do they have existing brand assets? (logo, photos, videos)
- [ ] What platforms are they currently on? What's working?

**2. Historical Ad Account Review** (if they've run ads before)
- [ ] Request access to existing Business Manager / Google Ads account
- [ ] Review past campaign performance (CTR, CPL, ROAS, spend)
- [ ] Identify what worked, what was wasted, what audiences were burned
- [ ] Check for Pixel installation and event firing accuracy

**3. Competitor Research**
- [ ] Use Meta Ad Library (facebook.com/ads/library) to see what competitors are running
- [ ] Note: ad formats used, messaging angles, offer types, creative styles
- [ ] Identify gaps — what aren't competitors doing that could be an opportunity?

**4. Deliverable: Audit Report** (send to client before kickoff)
- Summary of findings
- Recommended platforms and budget allocation
- Initial audience and creative hypothesis
- Expected outcomes (realistic, not overpromised)

---

### Phase 2: Strategy Development (Week 1)

**Budget Allocation Framework**

For a new client with no prior data, allocate as follows:
- **60% Testing:** Multiple ad sets, audiences, creatives to find what works
- **30% Scaling:** Double down on the best-performing combination from testing
- **10% Retargeting:** Warm audiences who've already engaged

Once 2-3 months of data exist, shift to:
- **40% Proven audiences (scale)**
- **30% Retargeting**
- **20% New audience testing**
- **10% Lookalike audiences**

**Funnel Mapping**

| Stage | Objective | Audience | Creative |
|---|---|---|---|
| **Top of Funnel** | Awareness / Reach | Cold (interest-based, broad) | Video, brand story, problem-awareness |
| **Middle of Funnel** | Engagement / Leads | Warm (video viewers, page engagers) | Testimonials, offers, how-it-works |
| **Bottom of Funnel** | Conversion / Purchase | Hot (website visitors, cart abandoners) | Urgency, specific offer, direct CTA |

---

### Phase 3: Creative Production (Week 1-2)

This is where Cre8ive District's in-house design team is a major advantage — most standalone agencies outsource creative.

**Creative Brief Template per Ad:**
- Objective (what should the viewer do?)
- Hook (what stops them from scrolling?)
- Body (what's the offer or key message?)
- CTA (what's the single action we want?)
- Format (image / video / carousel / story)
- Platform (Meta feed / Reels / TikTok / YouTube)
- Sizing (1:1 for feed, 9:16 for stories/reels, 16:9 for YouTube)

**Testing Matrix (minimum 3 variables to test):**

| Variable | Option A | Option B |
|---|---|---|
| Hook/headline | Problem-first ("Tired of...") | Benefit-first ("Get [result] in...") |
| Visual | Product/service image | People/lifestyle photo |
| CTA | "Chat us on WhatsApp" | "Get a free quote" |

Always isolate variables — don't change two things at once or you won't know what worked.

---

### Phase 4: Campaign Setup & Launch (Week 2)

**Pre-launch Checklist:**
- [ ] Business Manager access confirmed (client adds us as Partner, not employee)
- [ ] Ad account funding method set up (client adds their card/Paystack)
- [ ] Pixel installed and firing correctly (test with Pixel Helper)
- [ ] UTM parameters added to all destination URLs
- [ ] All creatives uploaded and reviewed
- [ ] Audiences built and saved
- [ ] Campaign budget set — start at ₦5,000–10,000/day minimum to exit learning phase faster
- [ ] Ad copy reviewed for policy compliance (no misleading claims, no before/after weight loss, no prohibited content)
- [ ] Client sign-off on all creatives before launch

**Learning Phase** (Meta)  
Meta needs ~50 conversion events per ad set per week to exit the learning phase. Until then, results are unstable — don't make decisions based on early numbers. Allow 7-14 days before optimizing.

---

### Phase 5: Monitoring & Optimization

**Daily Tasks (15 minutes/account)**
- Check spend vs. budget — flag any anomalies
- Check for disapproved ads — fix immediately
- Review CTR: anything below 0.8% on a cold audience is underperforming
- Scan for any sudden CPL spikes

**Weekly Tasks (1 hour/account)**
- Compare ad performance — pause bottom 25% of creatives
- Check audience overlap — are multiple ad sets competing?
- Review frequency — if frequency > 4, audience is saturated, expand or refresh creative
- Adjust budgets — shift spend toward best-performing ad sets
- Update client on weekly numbers

**Monthly Tasks (2-3 hours/account)**
- Full performance review against KPIs
- Audience refresh — build new custom and lookalike audiences
- Creative refresh — introduce new angles, pause fatigued ads
- Strategy review — are we still pursuing the right objective?
- Update landing pages or offers if conversion rate is declining

---

### Phase 6: Reporting & Client Communication

**Weekly Snapshot** (send every Monday, 5-minute read)
- Spend last 7 days
- Key metric vs. target (CPL, ROAS, or reach)
- 1-2 top-performing ads with creative thumbnails
- What we're testing this week

**Monthly Report** (send by the 5th of each month, 10-15 minute read)

Report sections:
1. **Executive Summary** — 3-4 bullet points, wins, issues, next steps
2. **Performance Dashboard** — Spend, Impressions, Reach, Clicks, CPL/ROAS, Conversions
3. **Audience Insights** — Which segments are performing, which are not
4. **Creative Performance** — Top 3 ads vs. bottom 3 ads with thumbnails
5. **Recommendations** — What to change, test, scale next month
6. **Budget Projection** — Spend forecast for next month

**Metrics to always include:**

| Metric | Why It Matters |
|---|---|
| Reach & Impressions | Brand awareness signal |
| CPM | Ad cost efficiency |
| CTR (link click through rate) | Creative + audience relevance |
| CPC | Traffic cost |
| CPL (cost per lead) | Core efficiency metric |
| Lead volume | The actual result |
| ROAS (for e-commerce) | Revenue vs. ad spend |

---

## 4. Creative Best Practices for Nigeria

### What Works in the Nigerian Market

**Video beats static in almost every category.** Nigerian audiences are highly video-engaged, especially on TikTok and Instagram Reels. Even a simple 15-second phone-shot video outperforms a polished static image in most tests.

**Creative formats that consistently perform:**

| Format | Why It Works | Example |
|---|---|---|
| **UGC / testimonial video** | Trust signal — real person, real result | Customer talking about their experience in their own voice |
| **Before / After** | Clear transformation, visual proof | Makeover, home renovation, business results |
| **Problem / Solution** | Immediate relevance | "If you're tired of [problem]... here's what we did for [client]" |
| **Behind the scenes** | Authenticity, trust-building | Show the team at work, the printing process, the design process |
| **Countdown / Urgency** | Scarcity drives action | "Offer ends this Friday" — but only use if it's real |
| **Price reveal** | Overcomes price anxiety | "Our [service] starts at just ₦X" |

### Copy Frameworks

**PAS (Problem → Agitate → Solution)**
```
Are you still using a DIY Canva logo for your business?  [Problem]
Every day, potential customers are judging your credibility — and leaving. [Agitate]
Cre8ive District builds brands that make people stop and take you seriously. [Solution]
```

**AIDA (Attention → Interest → Desire → Action)**
```
[Attention] Your competitors are running ads. You're not.
[Interest]  We helped FitLife Lagos get 2,000 leads in 3 weeks.
[Desire]    Same strategy, same team, your business.
[Action]    Chat us today — first consultation is free.
```

### Language Considerations

| Approach | When to Use | Example |
|---|---|---|
| **Standard English** | Professional services, B2B, upscale brands | "Elevate your brand with a professional identity system." |
| **Conversational English** | Most SME clients, broad consumer | "Your business needs a logo that people actually remember." |
| **Nigerian Pidgin** | Youth brands, food, fashion, entertainment | "Your brand suppose dey fire — make we fix am." |
| **Local language** | Hyper-local campaigns, specific ethnic markets | Yoruba for SW Nigeria campaigns, Igbo for SE, Hausa for North |

### Cultural Nuances

- **Community and family resonate** — frame products/services around impact on family, community, or social status
- **Value/price consciousness** — Nigerians are savvy buyers; always address value, not just price
- **Social proof is powerful** — "1,000 customers served" or real testimonials carry enormous weight
- **Payment friction** — always mention payment options (Paystack, bank transfer, instalments) in ad copy for higher-ticket items
- **WhatsApp as CTA** — "Chat us on WhatsApp" consistently outperforms "Visit website" for Nigerian audiences; lower friction, higher trust
- **Speed of delivery** — "Same-day", "48-hour turnaround", "ready in one week" outperform vague timelines

---

## 5. Tools & Tech Stack

### Ad Management
| Tool | Purpose | Cost |
|---|---|---|
| Meta Business Suite / Ads Manager | Manage all Facebook/Instagram campaigns | Free |
| TikTok Ads Manager | Manage all TikTok campaigns | Free |
| Google Ads | Search, Display, YouTube campaigns | Free (pay per click) |
| Meta Business Manager | Agency-level multi-account management | Free |

### Tracking & Analytics
| Tool | Purpose |
|---|---|
| Meta Pixel | Track website actions from Facebook/Instagram ads |
| TikTok Pixel | Track website actions from TikTok ads |
| Google Analytics 4 | Full website behavior tracking, multi-channel attribution |
| Google Tag Manager | Deploy all pixels and tags without touching code |
| UTM Builder | Create trackable URLs (use Google's Campaign URL Builder) |

### Creative Production
| Tool | Purpose |
|---|---|
| Figma | Static ad design (integrates with the design team's workflow) |
| Canva Pro | Quick social graphics, resizing ads to all formats |
| CapCut | Short-form video editing (TikTok-native, excellent for reels) |
| Adobe Premiere / DaVinci Resolve | Professional video editing for longer assets |
| Adobe After Effects | Motion graphics, animated ad elements |

### Reporting & Client Dashboards
| Tool | Purpose |
|---|---|
| Google Looker Studio | Free — connect Meta, Google Ads, GA4 into one live dashboard |
| Notion | Internal strategy docs, campaign briefs, client notes |
| Google Sheets | Performance tracking, budget management, manual reporting |

### Communication & Project Management
| Tool | Purpose |
|---|---|
| WhatsApp Business | Primary client communication channel |
| Slack | Internal team communication |
| Trello / Notion | Campaign task tracking |
| Google Drive | Asset storage, file sharing with clients |

---

## 6. Pricing & Revenue Model

### Management Fee Structures

**Option A: Flat Monthly Retainer (Recommended for most clients)**

The simplest structure. Client pays a fixed monthly fee for management, regardless of ad spend. Clean, predictable, no perverse incentive to overspend the client's budget.

| Package | Management Fee | Ad Spend Range |
|---|---|---|
| Starter | ₦150,000/month | ₦50k – ₦150k |
| Growth | ₦250,000/month | ₦150k – ₦600k |
| Premium | ₦450,000/month | ₦600k+ |

**Option B: Percentage of Ad Spend**

Agency earns 15-20% of the total ad spend managed. Better for high-spend clients; less predictable for us.

- 20% on ad spend under ₦500k/month
- 15% on ad spend ₦500k – ₦2M/month
- 10% on ad spend above ₦2M/month
- Minimum fee: ₦120,000/month regardless of spend

**Option C: Hybrid (Recommended for Growth+ clients)**

Flat base fee + % of ad spend above a threshold.
- Base: ₦150,000/month flat
- Plus 15% on any spend above ₦300,000/month
- Gives us upside as the client scales, while protecting against low-spend months

### One-Time Setup Fees (charge these always)

These cover account architecture, pixel installation, audience building, and the first campaign setup — real work that doesn't repeat.

| Service | Fee |
|---|---|
| New ad account setup (full) | ₦100,000 |
| Pixel installation (Meta or TikTok) | ₦40,000 |
| Google Ads account setup + first campaign | ₦120,000 |
| Full tracking audit & fix | ₦75,000 |

### Payment Collection

- Invoice via bank transfer or Paystack
- 100% upfront for month 1 (includes setup fee)
- Ongoing: invoice on the 25th, due before the 1st of the following month
- Ad spend: client loads their own Business Manager / Google Ads account directly — this protects both parties

### Margins

At the pricing above, a 3-person team handling 6 Starter clients and 2 Growth clients generates:

```
Starter × 6:  6 × ₦150,000 = ₦900,000
Growth  × 2:  2 × ₦250,000 = ₦500,000
Total monthly revenue from ads dept: ₦1,400,000

Costs (staff, tools, overhead): ~₦500,000
Gross margin: ~₦900,000 (64%)
```

---

## 7. Common Pitfalls & How to Avoid Them

### Ad Account Issues

**1. Account Restrictions / Bans**
- Cause: Policy violations (prohibited content, misleading claims, before/after health claims)
- Prevention: Read Meta's advertising policies. Never use "you" in a way that implies knowledge of personal attributes ("Are you struggling with debt?"). Never run real estate or financial products without Special Ad Category enabled.
- Recovery: Submit for review via Business Support. Keep a backup ad account set up on a secondary Business Manager for emergencies.

**2. Pixel Not Firing Correctly**
- Cause: Wrong implementation, conflicting tags, page redirects
- Prevention: Always verify with Meta Pixel Helper and TikTok Pixel Helper Chrome extensions before launching conversion campaigns
- Recovery: Rebuild via Google Tag Manager for cleaner implementation

**3. Exiting Learning Phase Problems**
- Cause: Too many ad sets with too little budget; too many changes too soon
- Prevention: Consolidate ad sets. Don't edit campaigns in the first 7 days. Budget at least ₦5,000/day per ad set

### Client Management Issues

**4. Unrealistic Expectations**
- Problem: Client expects 1,000 sales from ₦50,000 ad spend in week 1
- Prevention: Set expectations at proposal stage. Share realistic benchmarks. Define "success" in writing before starting.
- Template language: "Based on current market benchmarks, a ₦100,000 monthly budget targeting Lagos consumers should yield 80-150 leads at ₦650-1,200 cost per lead. These are projections, not guarantees."

**5. Client Changing Creative Without Telling You**
- Problem: Client edits the Facebook page, runs boosted posts from the page, or changes the website — breaking your campaigns or attribution
- Prevention: In the contract, state that client must not run any ads independently or modify tracking during the engagement without prior notice.

**6. Attribution Confusion**
- Problem: Client doesn't believe the ads are working because WhatsApp leads are calling and not saying "I saw your ad"
- Prevention: Use UTMs on all landing page links. Set up Google Analytics 4. Show them the full customer journey. Educate clients that most people don't volunteer where they saw an ad.

### Campaign Performance Issues

**7. Budget Wasted on Wrong Audiences**
- Prevention: Exclude existing customers, unqualified locations, and irrelevant age groups from day one.

**8. Creative Fatigue**
- Signs: CTR drops, frequency rises above 4, CPL increases
- Fix: Refresh at least 2 new ad creatives per month per account

**9. Spending All Budget Too Fast (Budget Pacing)**
- Cause: Daily budget set too high for the audience size, or ad set start date in the past
- Prevention: Ensure budget is set as daily (not lifetime) for ongoing campaigns. Monitor spend in the first 48 hours of any new campaign.

---

## 8. Case Study Templates

### Case Study 1: Restaurant Launch — Meta Lead Generation

**Client:** Luxe Bistro Lagos (new upscale restaurant, Victoria Island)  
**Brief:** Generate reservations and awareness for grand opening weekend

**Strategy:**
- Platform: Meta (Facebook + Instagram)
- Objective: Lead Generation (WhatsApp form)
- Targeting: Ages 25-45, Lagos Island / VI / Lekki / Ikoyi, interests: fine dining, Eko Hotel, events, Lagos lifestyle
- Budget: ₦200,000 total over 3 weeks
- Creative: Video tour of the restaurant + chef-in-action footage + opening weekend offer (free dessert with reservation)

**Results:**
| Metric | Result |
|---|---|
| Total reach | 185,000 people |
| Impressions | 420,000 |
| CPM | ₦476 |
| Leads generated | 624 |
| Cost per lead | ₦321 |
| Reservations confirmed | 218 (35% conversion from lead to booking) |
| Opening weekend tables | Fully booked |

**Key insight:** Video showing the interior ambiance had 3× the CTR of food photography. Showing the *experience* outperformed showing the product.

---

### Case Study 2: Fitness App Launch — TikTok + Meta

**Client:** FitLife Nigeria (home workout app, paid subscription)  
**Brief:** Drive app downloads and free trial sign-ups

**Strategy:**
- Platforms: TikTok (primary) + Meta (retargeting)
- Objective: TikTok — App Installs; Meta — Retargeting video viewers with offer
- Targeting: TikTok — ages 18-35, Nigeria, interests: fitness, weight loss, healthy lifestyle
- Budget: ₦350,000 (₦250k TikTok / ₦100k Meta retargeting) over 4 weeks
- Creative: 15-second UGC-style "I tried this app for 7 days" testimonial videos + results

**Results:**
| Metric | Result |
|---|---|
| TikTok impressions | 1.2M |
| TikTok CPM | ₦208 |
| App installs | 3,400 |
| Cost per install | ₦73 |
| Free trials started | 1,850 (54% of installs) |
| Paid conversions (month 1) | 310 |
| Revenue from campaign | ₦1,550,000 (at ₦5,000/subscription) |
| ROAS | 4.4× |

**Key insight:** UGC-style phone-shot videos outperformed polished studio content 4:1 on TikTok. Authenticity > production value.

---

### Case Study 3: E-commerce Fashion Brand — Full Funnel Meta

**Client:** Koko Lagos (contemporary women's fashion, online store)  
**Brief:** Scale online sales profitably, year-round management

**Strategy:**
- Platform: Meta only (Instagram-heavy)
- Full 3-stage funnel:
  - TOF: Video carousel of new arrivals → warm audiences
  - MOF: Testimonial/UGC retargeting → website visitors who didn't purchase
  - BOF: Dynamic product ads → cart abandoners (Pixel + Catalog)
- Budget: ₦500,000/month ad spend
- Our management fee: ₦250,000/month (Growth tier)
- Creative output: 12 assets/month across all funnel stages

**Results (Month 3 — after funnel maturity):**
| Metric | Result |
|---|---|
| Monthly ad spend | ₦500,000 |
| Revenue attributed to ads | ₦2,850,000 |
| ROAS | 5.7× |
| Orders | 187 |
| Average order value | ₦15,240 |
| New customer acquisition cost | ₦1,840 |
| Returning customer rate | 28% |

**Key insight:** BOF dynamic product ads (cart abandonment) had 12× ROAS despite being only 10% of the budget — always set up retargeting from day one, even for small budgets.

---

*Document version: 1.0 | Created: October 2026 | Review: Quarterly*  
*Maintained by: Cre8ive District Ads Department | Graceman IT Concepts*
