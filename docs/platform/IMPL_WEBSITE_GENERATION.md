# Website Generation — Implementation Plan

*Standalone implementation plan for the website generation system. Takes a brand
identity and business information, produces a live, hosted, responsive website.*

**Last updated:** 2026-11-07
**Owner:** Engineering (CC executes, founder reviews)
**Depends on:** Brand Generation Pipeline (brand package as input)

---

## 1. What This Delivers

Given a completed brand package (logo SVG/PNG, color palette, typography pairing)
and a business description (name, industry, services/products, location, contact
info), the system produces:

- **A complete 3–5 page responsive website**
  - Home (hero, value proposition, featured services/products, CTA)
  - About (story, team/founder, values)
  - Services or Products (grid/list with descriptions)
  - Contact (WhatsApp CTA, optional form, location/map embed)
  - Gallery *(optional, for visual businesses — fashion, food, interiors)*
- **Deployed to Vercel** with a platform subdomain (`yourbusiness.cre8ive.ng`)
- **Custom domain support** on premium plans (CNAME to Vercel)
- **Mobile-first responsive design** — breakpoints at 480px, 768px, 1024px
- **WhatsApp contact integration** — `wa.me/` link as primary CTA on every page
- **Google-ready** — `<title>`, `<meta description>`, Open Graph tags, `robots.txt`,
  `sitemap.xml`, structured data (`LocalBusiness` JSON-LD)
- **Lighthouse performance score ≥ 90** on mobile

### What This Does NOT Deliver (Phase 1)

- E-commerce / checkout (Phase 3 — Paystack storefront)
- Blog / CMS (Phase 3)
- Analytics dashboard (Phase 2 — basic Google Analytics tag only in Phase 1)
- Multi-language sites (Phase 4)

---

## 2. Architecture Decision

### Option A: Full Code Generation

LLM generates raw HTML/CSS/JS from scratch for every site.

| Pros | Cons |
|------|------|
| Maximum flexibility | Wildly inconsistent output quality |
| Unique per site | Hard to maintain — every site is a snowflake |
| | LLM hallucinations in CSS break layouts |
| | Slow — large token output per site |
| | Impossible to patch a bug across all generated sites |

### Option B: Component-Based Generation ★ RECOMMENDED

A pre-built library of ~40 section components, each with a configuration schema.
The LLM selects components, orders them into pages, fills in content, and sets
configuration props. The brand system (colors, fonts, spacing) is applied via CSS
custom properties at the theme level — the components never hard-code colors.

| Pros | Cons |
|------|------|
| Consistent, tested quality | Less unique per site (mitigated by 5 themes + brand colors) |
| Fast generation — LLM outputs JSON config, not code | Requires upfront component library investment |
| Easy to fix bugs — update component once, all sites benefit | New layout patterns require new components |
| Predictable Lighthouse scores | |
| Brand system applied cleanly via CSS variables | |

**Decision: Option B.** Consistency and reliability matter more than novelty for
a brand launch platform. The variety comes from 5 themes × unlimited brand
palettes × component variants × LLM-written copy.

---

## 3. Component Library Design

### 3.1 Technology

Components are **vanilla HTML templates** rendered server-side via Python's
`jinja2` (no React/Vue build step for generated sites). Each component is a
`.html` partial with a matching `.css` file. The final site is pure static
HTML/CSS/JS — zero JavaScript framework overhead.

Why not React: generated sites must load fast on Nigerian 3G connections. A
static HTML site with inlined critical CSS scores 95+ on Lighthouse without
effort. A React SPA requires hydration, bundling, and adds 50–150 KB of
framework JS.

### 3.2 Component Inventory

Each component has: **a Jinja2 template**, **a scoped CSS file**, and **a
JSON schema** defining its configurable props.

#### Navigation

| Component | Variants | Key Props |
|-----------|----------|-----------|
| `nav_header` | `sticky`, `transparent`, `solid` | `logo_url`, `brand_name`, `links[]`, `cta_text`, `cta_url`, `whatsapp_number` |
| `mobile_menu` | `slide`, `fullscreen` | inherits from `nav_header` |

#### Hero Sections

| Component | Variants | Key Props |
|-----------|----------|-----------|
| `hero_centered` | — | `headline`, `subheadline`, `cta_text`, `cta_url`, `background_style` |
| `hero_split` | `image_left`, `image_right` | `headline`, `subheadline`, `cta_text`, `cta_url`, `image_url` |
| `hero_image_bg` | — | `headline`, `subheadline`, `cta_text`, `cta_url`, `background_image_url`, `overlay_opacity` |
| `hero_minimal` | — | `headline`, `subheadline`, `cta_text`, `cta_url` |

#### Content Sections

| Component | Key Props |
|-----------|-----------|
| `services_grid` | `eyebrow`, `heading`, `description`, `items[]{icon, title, description}`, `columns: 2\|3\|4` |
| `services_list` | `heading`, `items[]{title, description, image_url}` |
| `products_grid` | `heading`, `items[]{name, price, image_url, description}`, `columns: 2\|3\|4` |
| `about_story` | `heading`, `paragraphs[]`, `image_url`, `image_position: left\|right` |
| `about_team` | `heading`, `members[]{name, role, image_url, bio}` |
| `about_values` | `heading`, `values[]{icon, title, description}` |
| `gallery_grid` | `heading`, `images[]{url, alt, caption}`, `columns: 2\|3\|4` |
| `gallery_masonry` | same as grid, masonry layout |
| `testimonials_cards` | `heading`, `items[]{quote, author, role, image_url}` |
| `testimonials_slider` | same, carousel layout |
| `pricing_table` | `heading`, `plans[]{name, price, currency, interval, features[], cta_text, cta_url, featured: bool}` |
| `faq_accordion` | `heading`, `items[]{question, answer}` |
| `stats_bar` | `items[]{number, label}` |
| `cta_banner` | `heading`, `description`, `cta_text`, `cta_url`, `style: accent\|dark\|light` |
| `feature_highlight` | `eyebrow`, `heading`, `description`, `image_url`, `image_position: left\|right` |
| `logo_cloud` | `heading`, `logos[]{url, alt}` |
| `map_embed` | `heading`, `address`, `google_maps_embed_url` |

#### Contact

| Component | Key Props |
|-----------|-----------|
| `contact_whatsapp` | `heading`, `description`, `whatsapp_number`, `whatsapp_message`, `cta_text` |
| `contact_form` | `heading`, `fields[]{name, type, required}`, `submit_text`, `action_url` |
| `contact_info` | `heading`, `items[]{icon, label, value, href}` |
| `contact_split` | combines `contact_whatsapp` + `contact_info` side by side |

#### Footer

| Component | Variants | Key Props |
|-----------|----------|-----------|
| `footer_standard` | — | `brand_name`, `tagline`, `links[]`, `social_links[]`, `copyright_year` |
| `footer_minimal` | — | `brand_name`, `copyright_year` |

### 3.3 Component Configuration Schema (Example)

```json
{
  "component": "hero_split",
  "variant": "image_right",
  "props": {
    "headline": "Handmade jewelry that tells your story",
    "subheadline": "Each piece is crafted in our Lagos workshop using locally sourced materials.",
    "cta_text": "Message us on WhatsApp",
    "cta_url": "https://wa.me/2348012345678?text=Hi%2C%20I%27d%20like%20to%20see%20your%20collection",
    "image_url": "/assets/hero.webp"
  }
}
```

### 3.4 CSS Custom Properties (Brand System)

Every generated site includes a `:root` block populated from the brand package:

```css
:root {
  /* From brand package */
  --brand-primary: #2D5A3D;
  --brand-secondary: #8B6914;
  --brand-accent: #D4A853;
  --brand-neutral-900: #1A1A1A;
  --brand-neutral-700: #4A4A4A;
  --brand-neutral-400: #999999;
  --brand-neutral-100: #F5F5F0;
  --brand-bg: #FFFFFF;
  --brand-surface: #FAFAF7;

  /* Typography — Google Fonts loaded in <head> */
  --font-heading: 'Fraunces', serif;
  --font-body: 'Inter', sans-serif;
  --font-size-base: 1rem;
  --font-size-sm: 0.875rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.5rem;
  --font-size-2xl: 2rem;
  --font-size-3xl: 3rem;
  --font-size-display: clamp(2.5rem, 5vw, 4.5rem);

  /* Spacing scale */
  --space-xs: 0.5rem;
  --space-sm: 1rem;
  --space-md: 2rem;
  --space-lg: 4rem;
  --space-xl: 6rem;
  --space-section: 5rem;

  /* Layout */
  --container-max: 1200px;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 16px;
}
```

Components reference these variables exclusively — never raw color values.

---

## 4. Generation Pipeline

```
┌──────────────────────────────────────────────────────────┐
│  INPUT                                                    │
│  brand_package: { logo, colors, fonts }                   │
│  business: { name, description, industry, services,       │
│              location, whatsapp, social_links }            │
└───────────────────────┬──────────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────────┐
│  1. CONTENT GENERATOR  (LLM — Claude Sonnet / Haiku)      │
│  - Selects theme based on industry + business description  │
│  - Decides page structure (which pages, which components)  │
│  - Writes all copy (headlines, descriptions, CTAs)         │
│  - Outputs: SiteSpec JSON                                  │
└───────────────────────┬──────────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────────┐
│  2. LAYOUT ASSEMBLER                                      │
│  - Validates SiteSpec against component schemas            │
│  - Resolves component templates from the library           │
│  - Renders Jinja2 templates with props                     │
│  - Injects brand CSS variables into :root                  │
│  - Assembles pages (header + sections + footer)            │
│  - Generates sitemap.xml, robots.txt, manifest.json        │
│  - Outputs: file tree (HTML/CSS/JS/assets)                 │
└───────────────────────┬──────────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────────┐
│  3. ASSET INTEGRATION                                     │
│  - Places logo in header component                        │
│  - Generates favicon from logo icon mark                   │
│  - Generates Open Graph image (brand colors + name)        │
│  - Optimizes images (WebP, srcset for responsive)          │
│  - Inlines critical CSS                                    │
│  - Outputs: optimized file tree                            │
└───────────────────────┬──────────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────────┐
│  4. QUALITY CHECK                                         │
│  - HTML validation (no broken tags)                        │
│  - CSS validation (no undefined variables)                  │
│  - All links resolve (no 404s)                             │
│  - Responsive check (viewport meta, no horizontal scroll)  │
│  - Accessibility basics (alt tags, contrast, lang attr)    │
│  - Lighthouse CI (target: performance ≥ 90, a11y ≥ 85)    │
│  - Outputs: pass/fail + report                             │
└───────────────────────┬──────────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────────┐
│  5. VERCEL DEPLOYER                                       │
│  - Creates Vercel project (or updates existing)            │
│  - Uploads file tree via Vercel API                        │
│  - Assigns subdomain                                       │
│  - Triggers deployment                                     │
│  - Waits for deployment ready                              │
│  - Returns live URL                                        │
└──────────────────────────────────────────────────────────┘
```

### 4.1 SiteSpec JSON (LLM Output Format)

This is the structured output the LLM produces. It is validated against a
Pydantic model before the assembler runs.

```json
{
  "theme": "warm",
  "pages": [
    {
      "slug": "index",
      "title": "Adé Beads — Handmade Jewelry, Lagos",
      "meta_description": "Handmade beaded jewelry crafted in Lagos. Each piece tells a story.",
      "sections": [
        {
          "component": "hero_split",
          "variant": "image_right",
          "props": {
            "headline": "Jewelry that carries meaning",
            "subheadline": "Every bead is chosen. Every piece is made by hand in our Yaba workshop.",
            "cta_text": "See the collection",
            "cta_url": "#products",
            "image_url": "/assets/placeholder-hero.webp"
          }
        },
        {
          "component": "products_grid",
          "props": {
            "heading": "Our pieces",
            "columns": 3,
            "items": [
              {
                "name": "Ilé Necklace",
                "price": "₦15,000",
                "description": "Glass beads on brass wire. Adjustable length.",
                "image_url": "/assets/placeholder-product-1.webp"
              }
            ]
          }
        },
        {
          "component": "cta_banner",
          "props": {
            "heading": "Want something made just for you?",
            "description": "Custom orders take 5–7 days. Message us on WhatsApp to start.",
            "cta_text": "Message us on WhatsApp",
            "cta_url": "https://wa.me/2348012345678",
            "style": "accent"
          }
        }
      ]
    },
    {
      "slug": "about",
      "title": "About — Adé Beads",
      "meta_description": "The story behind Adé Beads and the hands that make them.",
      "sections": [
        {
          "component": "about_story",
          "props": {
            "heading": "How it started",
            "paragraphs": [
              "Adé Beads began in 2023 at a kitchen table in Yaba...",
              "What started as gifts for friends became a business..."
            ],
            "image_url": "/assets/placeholder-about.webp",
            "image_position": "right"
          }
        }
      ]
    }
  ]
}
```

### 4.2 Content Generation Prompt

```
You are a website content strategist for Cre8ive District. Given a business
description and brand package, produce a SiteSpec JSON that defines a complete
website.

BUSINESS:
Name: {business_name}
Description: {business_description}
Industry: {industry}
Services/Products: {services_or_products}
Location: {location}
WhatsApp: {whatsapp_number}

BRAND:
Primary color: {primary_color}
Style direction: {brand_personality}

RULES:
1. Select a theme from: clean, bold, warm, classic, vibrant
2. Create 3-5 pages depending on the business type
3. Every page MUST include a WhatsApp CTA
4. Write real, specific copy — not generic placeholder text
5. Headlines should be short (under 8 words) and specific to this business
6. Use Nigerian English where appropriate (not American English)
7. All prices in Naira (₦)
8. Output ONLY valid JSON matching the SiteSpec schema
9. Do NOT invent services or products the business didn't mention
10. The home page hero should capture what makes this business worth choosing

OUTPUT: SiteSpec JSON
```

---

## 5. Theme System

Each theme is a CSS file that sets additional design tokens on top of the brand
variables. Components use both brand variables (colors, fonts) and theme
variables (spacing rhythm, border styles, shadow depth, animation style).

### Theme Definitions

| Theme | Feel | Typography Style | Borders | Shadows | Best For |
|-------|------|-----------------|---------|---------|----------|
| **Clean** | Minimal, spacious | Sans-serif, wide letter-spacing | None or `1px solid` | None | Professional services, tech, consulting |
| **Bold** | High-contrast, punchy | Large headings, tight spacing | Thick `3px` accents | Hard shadows (`4px 4px 0`) | Fashion, food, entertainment, events |
| **Warm** | Soft, inviting | Rounded serif + clean sans | Rounded corners `12–16px` | Soft `box-shadow` | Wellness, beauty, childcare, bakeries |
| **Classic** | Established, trusted | Serif headings, refined | Thin lines, ruled sections | Subtle | Legal, consulting, hospitality, luxury |
| **Vibrant** | Energetic, youthful | Bold sans, gradient accents | Rounded, colored borders | Colored/gradient shadows | Youth brands, events, creatives, tech |

### Theme CSS Example (`warm.css`)

```css
/* Theme: Warm — layered on top of brand variables */
:root {
  --theme-radius: 12px;
  --theme-shadow: 0 2px 12px rgba(0,0,0,0.06);
  --theme-shadow-hover: 0 4px 20px rgba(0,0,0,0.10);
  --theme-border: none;
  --theme-heading-weight: 500;
  --theme-body-line-height: 1.7;
  --theme-section-padding: var(--space-xl);
  --theme-transition: 0.3s ease;
  --theme-button-radius: 999px; /* pill buttons */
}
```

The LLM selects the theme in the SiteSpec. The assembler loads the
corresponding theme CSS file alongside the brand variables.

---

## 6. Vercel Deployment Integration

### 6.1 Project Structure on Vercel

Each generated website is a Vercel project under the Cre8ive District team
account. Project naming convention: `cd-{business_slug}` (e.g.,
`cd-ade-beads`).

### 6.2 Deployment Flow (Vercel REST API v13)

**Step 1 — Create project (first deploy only)**

```
POST https://api.vercel.com/v10/projects
Authorization: Bearer {VERCEL_TOKEN}
Content-Type: application/json

{
  "name": "cd-ade-beads",
  "framework": null,
  "buildCommand": "",
  "outputDirectory": ".",
  "publicSource": false
}
```

Response includes `project.id` — store in the `websites` table.

**Step 2 — Upload files and create deployment**

```
POST https://api.vercel.com/v13/deployments
Authorization: Bearer {VERCEL_TOKEN}
Content-Type: application/json

{
  "name": "cd-ade-beads",
  "target": "production",
  "files": [
    {
      "file": "index.html",
      "data": "<base64-encoded content>"
    },
    {
      "file": "about/index.html",
      "data": "<base64-encoded content>"
    },
    {
      "file": "assets/site.css",
      "data": "<base64-encoded content>"
    },
    {
      "file": "assets/logo.svg",
      "data": "<base64-encoded content>"
    }
  ],
  "projectSettings": {
    "framework": null,
    "buildCommand": "",
    "outputDirectory": "."
  }
}
```

Response includes `deployment.url` and `deployment.readyState`.

**Step 3 — Poll for ready state**

```
GET https://api.vercel.com/v13/deployments/{deployment_id}
```

Poll until `readyState === "READY"` (typically 10–30 seconds for static sites).

**Step 4 — Assign subdomain**

```
POST https://api.vercel.com/v10/projects/{project_id}/domains
{
  "name": "ade-beads.cre8ive.ng"
}
```

Requires a wildcard DNS record `*.cre8ive.ng → cname.vercel-dns.com` on the
`cre8ive.ng` domain.

**Step 5 — Custom domain (premium plans)**

```
POST https://api.vercel.com/v10/projects/{project_id}/domains
{
  "name": "adebeads.com"
}
```

Customer adds a CNAME record pointing to `cname.vercel-dns.com`. Vercel
handles SSL automatically.

### 6.3 Updating an Existing Site

Repeat Step 2 with the updated file tree. Vercel creates a new deployment
and promotes it to production. Previous deployments are retained (rollback
possible via the Vercel dashboard or API).

### 6.4 Vercel Token Management

A single Vercel team token with project-creation permissions. Store in
environment variables, never in code. Rate limit: 100 deployments per hour
per team (well within Phase 1 needs).

---

## 7. File Structure

```
cre8ive-platform/
  services/
    website/
      generator.py          — orchestrates the full pipeline
      content.py            — LLM content generation + SiteSpec output
      assembler.py          — renders components → HTML pages
      assets.py             — favicon, OG image, image optimization
      quality.py            — validation + Lighthouse check
      deployer.py           — Vercel API client
      schemas.py            — Pydantic models: SiteSpec, Page, Section, ComponentProps
  components/
    nav_header.html         — Jinja2 template
    nav_header.css          — scoped styles
    hero_centered.html
    hero_centered.css
    hero_split.html
    hero_split.css
    hero_image_bg.html
    hero_image_bg.css
    hero_minimal.html
    hero_minimal.css
    services_grid.html
    services_grid.css
    products_grid.html
    products_grid.css
    about_story.html
    about_story.css
    contact_whatsapp.html
    contact_whatsapp.css
    contact_split.html
    contact_split.css
    cta_banner.html
    cta_banner.css
    faq_accordion.html
    faq_accordion.css
    testimonials_cards.html
    testimonials_cards.css
    gallery_grid.html
    gallery_grid.css
    stats_bar.html
    stats_bar.css
    footer_standard.html
    footer_standard.css
    footer_minimal.html
    footer_minimal.css
    ...
  themes/
    clean.css
    bold.css
    warm.css
    classic.css
    vibrant.css
  base/
    reset.css               — modern CSS reset
    utilities.css           — responsive container, spacing helpers
    base.html               — full page template (doctype, head, body wrapper)
  static/
    placeholder-hero.webp
    placeholder-product.webp
    placeholder-about.webp
```

---

## 8. Deliverables Checklist

| # | Deliverable | Done when |
|---|-------------|-----------|
| 1 | Component library — all templates + CSS + schemas | All components render correctly in isolation with test props |
| 2 | 5 theme CSS files | Each theme visually distinct; verified on 3 test businesses |
| 3 | Content generator (LLM prompt + SiteSpec parser) | Generates valid SiteSpec for 10 different business types |
| 4 | Layout assembler | Renders SiteSpec → complete HTML file tree |
| 5 | Asset integration (favicon, OG image, optimization) | Generated sites include favicon, OG image, optimized assets |
| 6 | Quality checker | Rejects sites with broken HTML, missing alt tags, or Lighthouse < 85 |
| 7 | Vercel deployer | Creates project, deploys, assigns subdomain, returns live URL |
| 8 | Subdomain DNS setup | `*.cre8ive.ng` wildcard configured on Vercel |
| 9 | Custom domain flow | Premium user can add their domain; SSL provisioned automatically |
| 10 | End-to-end test | Business description → live site in under 5 minutes |

---

## 9. Estimated Timeline

### Week 1 — Component Library Foundation

- Build the `base.html` page template with CSS variable injection
- Implement 5 core components: `nav_header`, `hero_centered`, `hero_split`,
  `services_grid`, `footer_standard`
- Build the Jinja2 rendering pipeline (`assembler.py`)
- Create all 5 theme CSS files
- Test: render a hardcoded SiteSpec into a working site

### Week 2 — Full Component Library + Content Generator

- Build remaining ~20 components (about, contact, gallery, testimonials,
  pricing, FAQ, CTA, stats, products)
- Implement the LLM content generator with SiteSpec output
- Build `schemas.py` with full Pydantic validation
- Test: generate SiteSpec for 5 different business types, render all to HTML

### Week 3 — Asset Pipeline + Quality + Vercel

- Favicon generation from logo
- Open Graph image generation (Pillow — brand colors + business name)
- Image optimization pipeline (Pillow → WebP)
- Critical CSS inlining
- Quality checker (HTML validation, link checking, basic Lighthouse via
  `lighthouse-ci` or Vercel Speed Insights)
- Vercel API integration: create project, deploy files, assign subdomain
- Test: full pipeline from brand + description → live URL

### Week 4 — Polish + Edge Cases

- Custom domain flow for premium plans
- Error handling: LLM generates invalid SiteSpec → retry with feedback
- Fallback: if generation fails 3 times, assign to human designer
- Site update flow (customer requests a change → regenerate specific page)
- Load test: generate and deploy 20 sites in sequence
- Final QA: test across 10 real Nigerian business types

---

## 10. Hosting Cost Analysis

### Vercel Pricing (Pro Plan — $20/month for the team)

| Resource | Free Tier | Pro Tier | Notes |
|----------|-----------|----------|-------|
| Projects | 200 | Unlimited | Each generated site = 1 project |
| Bandwidth | 100 GB/mo | 1 TB/mo | Static HTML sites use minimal bandwidth |
| Deployments | 100/day | 6,000/day | ~200 sites/day capacity on Pro |
| Custom domains | 50 per project | 50 per project | More than enough |
| Build minutes | 100 min/mo | 24,000 min/mo | We don't use builds (pre-rendered) |

### Cost Per Site Hosted

At 100 sites on Vercel Pro ($20/month):
- **$0.20/site/month** for hosting
- ~₦300/site/month at current exchange rates

At 1,000 sites, Vercel Enterprise pricing applies. **Mitigation:**
generated sites are static HTML — move to Cloudflare Pages (free for
unlimited sites, 500 deployments/month) or S3 + CloudFront before hitting
Vercel's limits.

### Cost Per Site Generated

| Line | Cost |
|------|------|
| LLM content generation (Claude Haiku, ~4,000 tokens out) | ~₦80 |
| OG image generation (Pillow, compute) | ~₦5 |
| Favicon generation | ~₦5 |
| Vercel deployment API call | Free |
| **Total per site generated** | **~₦90** |

Websites are effectively free to generate and host. The value — and the price
the customer pays — is in the brand package and the design quality, not the
hosting.

### Scaling Strategy

| Sites | Hosting | Cost |
|-------|---------|------|
| 1–200 | Vercel Pro | $20/mo total |
| 200–1,000 | Cloudflare Pages (free tier) | $0/mo |
| 1,000+ | S3 + CloudFront with custom deployment pipeline | ~$0.01/site/mo |

Static sites scale essentially for free. The constraint is generation
throughput (LLM API rate limits), not hosting.
