# Web Interface — Implementation Plan

*The primary interface for Cre8ive District's AI-powered brand launch platform.
Customers sign up on the web, describe their business in a conversational UI,
watch the AI build their brand in real-time, review outputs, manage everything
from one place. WhatsApp is the secondary channel.*

**Last updated:** 2026-11-08

---

## 1. What this delivers

A web application where a business owner can:

1. **Sign up** via Google, email magic-link, or phone OTP
2. **Describe their business** in a conversational chat interface with an AI assistant
3. **Watch their brand being built** in real-time — logo generating, colours selected, website assembling
4. **Review brand outputs** — logo options, colour palette, typography — displayed visually in the browser
5. **Approve or request changes** — "I like option 2 but make the green darker"
6. **See their website being built** — live preview in an iframe
7. **Publish** their website with one click
8. **Connect social media** accounts (Instagram, Facebook, TikTok, X, LinkedIn)
9. **Review AI-generated social posts** — approve, edit, schedule, or reject before anything goes live
10. **Manage billing** — Paystack-powered, Naira-denominated
11. **Access their brand kit** — download logos, guidelines PDF, social templates at any time

### Two modes

| Mode | Purpose |
|------|---------|
| **Chat mode** | Conversational interface on the left, live preview panel on the right (split-screen on desktop, stacked on mobile) |
| **Dashboard mode** | Overview of brand status, website, social posts, billing, downloads |

---

## 2. Information architecture

### Routes

```
/                          → Marketing landing page (public)
/pricing                   → Plan comparison (public)
/signup                    → Sign up (Google · email · phone)
/login                     → Log in
/onboarding                → Guided first-run flow
/chat                      → Main chat + live preview (the core screen)
/dashboard                 → Business overview
/brand                     → Brand kit (logos, colours, fonts, guidelines)
/brand/edit                → Opens chat with brand-editing context
/website                   → Website manager (preview, publish/unpublish, domain)
/website/preview           → Full-screen website preview
/social                    → Social media hub
/social/connect            → OAuth flows per platform
/social/posts              → Post queue (drafts → approved → scheduled → published)
/social/calendar           → Visual content calendar
/billing                   → Plan, payment history, upgrade/downgrade
/settings                  → Account, team, notifications
```

### Navigation

| Surface | Elements |
|---------|----------|
| **Top bar** | Cre8ive District logo · business name · global chat trigger · notification bell · account menu |
| **Sidebar** (desktop ≥ 1024 px) | Dashboard · Brand · Website · Social · Billing — collapsible to icon-only rail |
| **Bottom bar** (mobile < 1024 px) | Dashboard · Brand · Chat · Social · More (overflow) |

---

## 3. The chat interface — core UX

### Left panel — conversation

- **Message input** at the bottom: text field, image-upload button (`+`), voice-note button (records and auto-transcribes via Whisper)
- **Rich AI messages**:
  - Plain text (streaming token-by-token)
  - Inline image previews (logo concepts, social-post mock-ups)
  - Interactive cards — colour-palette picker, font selector, plan comparison table, mood-board grid
  - Action buttons — "Approve", "Try another", "Download", "Publish"
  - Progress cards — "Building your brand …" with animated step checklist
- **Conversation history** persisted across sessions (PostgreSQL `messages` table, paginated load)
- **Work vs Chat indicator** — when the AI is executing a generation job, a persistent status bar appears: "Working · 3 of 5 steps done" with elapsed time

### Right panel — live preview

Synced in real-time to whatever the chat is discussing.

| Tab | Content |
|-----|---------|
| **Brand** | Brand board: logo (with variant toggle), colour swatches, font specimens, tone keywords |
| **Website** | `<iframe>` of the generated site (sandboxed), refresh-on-change |
| **Social** | Platform-specific post mock-ups (IG feed card, X tweet card, etc.) |

On mobile the preview is a full-screen overlay with a "← Back to chat" header button.

### Real-time updates

| Channel | Purpose | Tech |
|---------|---------|------|
| **Chat streaming** | Token-by-token AI responses | Vercel AI SDK `useChat` → SSE from FastAPI `/api/chat/stream` |
| **Progress events** | Brand-gen / site-gen step updates | FastAPI SSE endpoint `/api/events/{business_id}` backed by Redis pub/sub |
| **Asset delivery** | New logo / site deploy URL ready | Same SSE channel; the client patches its local state on receipt |

---

## 4. Technical architecture

### Frontend stack

| Layer | Choice | Reason |
|-------|--------|--------|
| Framework | **Next.js 15 (App Router)** | RSC for marketing pages, client components for the app shell; Vercel-native |
| Styling | **Tailwind CSS v4** | Utility-first; consistent with the existing Cre8ive District site's design tokens |
| Components | **shadcn/ui** (Radix primitives) | Accessible, composable, no vendor lock-in |
| Animations | **Framer Motion** | Brand reveals, page transitions, progress bars |
| AI streaming | **Vercel AI SDK v7** `useChat` / `useCompletion` | First-class SSE streaming, built-in message management |
| Data fetching | **SWR** | Lightweight, cache-aware, works well with the dashboard's polling pattern |
| Auth | **NextAuth.js v5** | Google OAuth, email magic-link (Resend), phone OTP (custom provider via Termii/Africa's Talking SMS gateway) |
| Forms | **React Hook Form + Zod** | Validated inputs for settings, billing, onboarding |
| Rich chat cards | Custom React components rendered inside the message list | Colour-picker card, font-preview card, action-button row, progress-step card |

### Backend integration

The web app talks to the **FastAPI platform backend** (the same service that powers brand gen, website gen, billing, social posting). The Next.js app is a thin presentation layer — it never generates brands or calls image APIs directly.

```
Browser  ──►  Next.js (Vercel)
               │
               ├── RSC pages: marketing, dashboard (fetch from FastAPI at request time)
               ├── Client components: chat, preview, social queue (client-side fetches)
               ├── API routes:
               │    /api/auth/*         → NextAuth (session management)
               │    /api/chat           → proxy to FastAPI /api/chat/stream
               │    /api/webhooks/*     → Paystack, social OAuth callbacks
               │
               └──►  FastAPI backend (Railway / Hetzner)
                      ├── /api/chat/stream      (SSE)
                      ├── /api/events/{biz}     (SSE — progress)
                      ├── /api/brand/*
                      ├── /api/website/*
                      ├── /api/social/*
                      ├── /api/billing/*
                      └── /api/auth/phone-otp   (sends OTP via SMS gateway)
```

### Key interaction: chat → generation → live preview

```
1. User types "Build my brand" in chat UI
2. Next.js client POSTs to /api/chat (proxied to FastAPI)
3. FastAPI orchestrator:
   a. Streams a text reply: "Let's do this. Building your brand now …"
   b. Enqueues a brand-generation background job (Celery / arq / in-process asyncio task)
   c. The job publishes progress events to Redis pub/sub:
      { step: "strategy", status: "done" }
      { step: "colours",  status: "running" }
      …
4. Client's EventSource on /api/events/{biz} receives each event
5. ProgressCard component updates in the chat; PreviewPanel re-renders the brand board
6. When the logo step completes, the event includes { logo_url: "…" }
7. PreviewPanel.Brand shows the logo; chat appends an ImageCard with approve/retry buttons
8. User presses "Approve" → PATCH /api/brand/{id}/approve → triggers website-gen job
9. Cycle repeats for the website
```

---

## 5. Onboarding flow — first-time user experience

### Step 1 — Welcome (route: `/onboarding`)

Full-screen card with the Cre8ive District logo and three large buttons:

| Option | What happens |
|--------|-------------|
| **"I have an idea"** | Proceeds to business-description chat |
| **"I have an existing business"** | Same chat, but the AI asks for the business name and existing brand assets first |
| **"Surprise me"** | The AI picks an industry and generates a demo brand — user can claim or start over |

### Step 2 — Describe your business (chat)

The AI greets the user and asks a maximum of **four questions** (one at a time):

```
AI:  Welcome to Cre8ive District. I'm going to build your brand.
     What's the name of your business? (If you don't have one yet, tell me
     what you do and I'll suggest a few.)

User:  Iya Bose Kitchen

AI:  Great name. What does Iya Bose Kitchen do — and who are your customers?

User:  I sell jollof rice and small chops for events in Surulere

AI:  Got it — event catering in Surulere, jollof rice and small chops.
     One more question: do you have a style preference? For example:
     • Bold and colourful
     • Clean and modern
     • Warm and traditional
     Or just tell me in your own words.

User:  warm and traditional

AI:  Perfect. Building your brand now — this takes about two minutes.
     [ProgressCard appears]
```

Each answer is extracted into structured fields by the orchestrator and stored:

```python
class BusinessIntake(BaseModel):
    name: str
    description: str
    industry: str          # inferred by AI
    location: str | None
    target_audience: str
    style_direction: str   # mapped to one of 5 themes
```

### Step 3 — Watch it build

A `ProgressCard` component fills the chat, with steps that check off live:

```
✓  Brand strategy        — 4 s
✓  Colour palette         — 2 s
✓  Typography             — 1 s
◎  Logo concepts          — generating …
○  Brand guidelines
```

The right panel simultaneously populates: colours appear, then fonts, then the logo fades in.

### Step 4 — Review

The chat appends a `BrandReviewCard`:

```
AI:  Here's your brand for Iya Bose Kitchen. Take a look →

     [BrandReviewCard]
     ┌──────────────────────────────────┐
     │  🟤 🟠 🟡 ⬜  Colour palette     │
     │  Fraunces + Inter  Typography    │
     │  [Logo image]                    │
     │                                  │
     │  [ Love it ]  [ Change something ] │
     └──────────────────────────────────┘
```

- **"Love it"** → marks the brand approved; if the user's plan includes a website, the AI immediately starts building it.
- **"Change something"** → the AI asks what to change. The user types a free-form instruction ("make the orange deeper", "try a different font"). The pipeline re-runs only the affected stages.

### Step 5 — Website (if applicable)

Same pattern: progress card → live preview fills the right panel → user publishes with one button.

### Step 6 — Payment

If the user is on the free tier and wants to publish or download, a `PlanCard` appears in the chat with Paystack checkout. On paid plans this step is skipped.

---

## 6. Dashboard design (route: `/dashboard`)

### Overview grid — four cards

| Card | Content |
|------|---------|
| **Brand health** | Completion checklist: logo ✓, colours ✓, guidelines ✓, social templates ○. Progress ring. |
| **Website** | Status badge (Live / Draft / Not started), thumbnail, visit count (last 7 days via Vercel Analytics) |
| **Social** | Connected-platform icons with status dots, "3 posts scheduled this week", next post time |
| **Quick actions** | "Chat with AI" · "Download brand kit" · "Create a post" · "Invite team member" |

### Brand section (`/brand`)

A visual brand board rendered as a styled card grid:

- **Logo**: primary mark displayed large, toggle to switch between icon / wordmark / horizontal / stacked variants. Download dropdown: SVG, PNG 512, PNG 256, PNG 64, favicon ICO.
- **Colours**: swatches with hex codes; click to copy. Light and dark background previews.
- **Typography**: heading + body font specimens with the actual Google Fonts loaded. Size/weight scale reference.
- **Guidelines PDF**: thumbnail + download button.
- **"Request changes"** button → navigates to `/chat` with the context pre-loaded ("The user wants to change their brand. Current brand: …").

### Website section (`/website`)

- Full-width preview thumbnail (auto-captured via Vercel OG or Puppeteer screenshot)
- Live URL with copy button
- Action bar: "Edit" (→ chat), "Publish" / "Unpublish", "Connect domain", "Open site ↗"
- Analytics strip: unique visitors, page views (last 7 / 30 days) — pulled from Vercel Analytics API

### Social section (`/social`)

- **Connected platforms** row: Instagram, Facebook, TikTok, X, LinkedIn — each shows avatar + handle or a "Connect" button
- **Post queue** table: status (draft / approved / scheduled / posted / failed), platform icon, thumbnail, caption preview, scheduled time, engagement metrics (impressions, likes — populated after posting)
- **Calendar view** (`/social/calendar`): month grid with dots per scheduled post; click a day to see/edit that day's posts

---

## 7. Mobile experience

Over 80 % of Nigerian internet users access via phone. The web app must be mobile-first.

| Element | Mobile behaviour |
|---------|-----------------|
| **Navigation** | Bottom tab bar: Dashboard · Brand · Chat (centred, accent-coloured) · Social · More |
| **Chat** | Full-screen. Preview accessible via a "Preview ↑" pull-up sheet or a toggle button in the top bar |
| **Brand kit** | Horizontally swipeable cards: Logo → Colours → Fonts → Guidelines |
| **Social approval** | Each pending post is a card; swipe right = approve, left = decline (with haptic feedback) |
| **Paystack checkout** | Opens Paystack's mobile-optimised inline checkout (not a redirect — stays in-app) |
| **Onboarding** | Same chat flow, full-screen; progress card is a sticky banner at the top |

### Progressive Web App (PWA)

Ship a `manifest.json` + service worker so the app can be "installed" to the home screen on Android. This matters in Nigeria — home-screen apps get 3× the return-visit rate of bookmarked sites.

```json
{
  "name": "Cre8ive District",
  "short_name": "Cre8ive",
  "start_url": "/dashboard",
  "display": "standalone",
  "theme_color": "#f36b35",
  "background_color": "#f5f5ee",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

---

## 8. Authentication

### Three providers via NextAuth.js v5

| Provider | Implementation | Why |
|----------|---------------|-----|
| **Google OAuth** | `GoogleProvider` — standard | Quick signup for users with Google accounts |
| **Email magic link** | `EmailProvider` with **Resend** as the transport | No password to remember; works for everyone with email |
| **Phone OTP** | Custom `CredentialsProvider`: client submits phone → API route calls Termii (or Africa's Talking) to send a 6-digit OTP via SMS → user submits OTP → API route verifies → creates session | Critical for Nigerian market — many business owners don't use email as their primary identity |

### Session strategy

- **JWT-based** sessions (not database sessions) for speed
- Access token: 15-minute expiry; refresh token: 30-day expiry
- Stored in an `httpOnly` cookie — no localStorage tokens
- FastAPI backend validates JWTs using the same signing secret

### Account linking

If a user signs up with phone and later adds Google (or vice versa), NextAuth links the accounts by matching on a verified phone number or email. The `accounts` table stores multiple providers per user.

---

## 9. Real-time architecture

### Chat streaming

```typescript
// app/(app)/chat/page.tsx
import { useChat } from "ai/react";

const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
  api: "/api/chat",
  body: { businessId },
  onFinish: (message) => {
    // If message contains a work trigger, start listening for progress events
    if (message.toolInvocations?.some(t => t.toolName === "generate_brand")) {
      subscribeToProgress(businessId);
    }
  },
});
```

### Progress events

```typescript
// lib/hooks/useProgress.ts
function useProgress(businessId: string) {
  const [steps, setSteps] = useState<ProgressStep[]>([]);

  useEffect(() => {
    const source = new EventSource(`/api/events/${businessId}`);
    source.onmessage = (event) => {
      const data = JSON.parse(event.data) as ProgressEvent;
      setSteps((prev) => upsertStep(prev, data));

      // When an asset is ready, update the preview panel
      if (data.type === "asset_ready") {
        mutate(`/api/brand/${businessId}`); // SWR revalidation
      }
    };
    return () => source.close();
  }, [businessId]);

  return steps;
}
```

### Backend SSE endpoint (FastAPI)

```python
# platform/routers/events.py
@router.get("/api/events/{business_id}")
async def event_stream(business_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    async def generate():
        pubsub = redis.pubsub()
        await pubsub.subscribe(f"progress:{business_id}")
        async for message in pubsub.listen():
            if message["type"] == "message":
                yield f"data: {message['data'].decode()}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")
```

---

## 10. File structure

```
cre8ive-platform-web/
├── app/
│   ├── (marketing)/                # Public, no auth required
│   │   ├── page.tsx                # Landing page
│   │   ├── pricing/page.tsx
│   │   └── layout.tsx              # Marketing header/footer
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   ├── signup/page.tsx
│   │   └── layout.tsx              # Centred card layout
│   ├── (app)/                      # Authenticated app shell
│   │   ├── layout.tsx              # Sidebar + top bar + mobile nav
│   │   ├── dashboard/page.tsx
│   │   ├── chat/page.tsx           # Split: ChatPanel + PreviewPanel
│   │   ├── brand/
│   │   │   ├── page.tsx            # Brand kit viewer
│   │   │   └── edit/page.tsx       # Redirects to /chat with brand context
│   │   ├── website/
│   │   │   ├── page.tsx            # Website manager
│   │   │   └── preview/page.tsx    # Full-screen iframe
│   │   ├── social/
│   │   │   ├── page.tsx            # Social hub overview
│   │   │   ├── connect/page.tsx    # OAuth connection flows
│   │   │   ├── posts/page.tsx      # Post queue + approval
│   │   │   └── calendar/page.tsx   # Content calendar
│   │   ├── billing/page.tsx
│   │   ├── settings/page.tsx
│   │   └── onboarding/page.tsx     # First-run guided flow
│   ├── api/
│   │   ├── auth/[...nextauth]/route.ts
│   │   ├── chat/route.ts           # Proxies to FastAPI /api/chat/stream
│   │   ├── events/[businessId]/route.ts  # Proxies SSE from FastAPI
│   │   └── webhooks/
│   │       ├── paystack/route.ts
│   │       └── social/[platform]/route.ts  # OAuth callbacks
│   ├── manifest.json               # PWA manifest
│   └── globals.css                 # Tailwind base + design tokens
├── components/
│   ├── chat/
│   │   ├── ChatPanel.tsx           # Message list + input
│   │   ├── MessageBubble.tsx       # Text message
│   │   ├── ImageCard.tsx           # Logo/post preview with actions
│   │   ├── ProgressCard.tsx        # Step-by-step generation progress
│   │   ├── ActionCard.tsx          # Approve / retry / download buttons
│   │   ├── PlanCard.tsx            # Inline plan upgrade prompt
│   │   ├── ColourPickerCard.tsx    # Interactive palette selector
│   │   ├── FontPreviewCard.tsx     # Typography comparison
│   │   └── MoodBoardCard.tsx       # Style-direction picker (onboarding)
│   ├── preview/
│   │   ├── PreviewPanel.tsx        # Tabbed: Brand | Website | Social
│   │   ├── BrandBoard.tsx          # Logo + colours + fonts layout
│   │   ├── SitePreview.tsx         # Sandboxed iframe
│   │   └── SocialMockup.tsx        # Platform-specific post preview
│   ├── brand/
│   │   ├── LogoDisplay.tsx         # With variant toggle + download
│   │   ├── ColourSwatches.tsx      # Click-to-copy hex
│   │   ├── FontSpecimen.tsx        # Live Google Fonts specimen
│   │   └── GuidelinesDownload.tsx  # PDF thumbnail + button
│   ├── social/
│   │   ├── PlatformConnect.tsx     # OAuth button per platform
│   │   ├── PostCard.tsx            # Swipeable approval card
│   │   └── CalendarGrid.tsx        # Month view with post dots
│   ├── billing/
│   │   ├── PlanComparison.tsx      # Three-column plan grid
│   │   └── PaystackCheckout.tsx    # Inline Paystack popup trigger
│   ├── layout/
│   │   ├── Sidebar.tsx             # Desktop nav rail
│   │   ├── TopBar.tsx              # Logo + biz name + bell + avatar
│   │   ├── MobileNav.tsx           # Bottom tab bar
│   │   └── NotificationBell.tsx    # Dropdown with recent events
│   └── ui/                         # shadcn/ui primitives
│       ├── button.tsx
│       ├── card.tsx
│       ├── dialog.tsx
│       ├── dropdown-menu.tsx
│       ├── input.tsx
│       ├── tabs.tsx
│       ├── toast.tsx
│       └── ...
├── lib/
│   ├── api.ts                      # Typed FastAPI client (fetch wrapper)
│   ├── auth.ts                     # NextAuth config + providers
│   ├── hooks/
│   │   ├── useChat.ts              # Wraps Vercel AI SDK useChat
│   │   ├── useProgress.ts          # SSE progress subscription
│   │   ├── useBrand.ts             # SWR hook for brand data
│   │   ├── useWebsite.ts           # SWR hook for website data
│   │   └── useSocial.ts            # SWR hook for social accounts + posts
│   ├── types.ts                    # Shared TypeScript interfaces
│   └── utils.ts                    # Helpers (formatNaira, timeAgo, etc.)
├── public/
│   ├── icon-192.png
│   ├── icon-512.png
│   └── og-image.png
├── tailwind.config.ts
├── next.config.ts
├── package.json
└── tsconfig.json
```

---

## 11. Deployment

| Item | Detail |
|------|--------|
| **Host** | Vercel (same team/account as the Cre8ive District marketing site) |
| **Domains** | `app.cre8ivedistrict.com` (production), `staging-app.cre8ivedistrict.com` (preview) |
| **Environment variables** | `NEXTAUTH_SECRET`, `GOOGLE_CLIENT_ID/SECRET`, `RESEND_API_KEY`, `TERMII_API_KEY`, `FASTAPI_URL`, `PAYSTACK_PUBLIC_KEY`, `PAYSTACK_SECRET_KEY` |
| **CI** | Vercel's Git integration — push to `main` deploys production; push to any branch creates a preview deployment |
| **Monitoring** | Vercel Analytics (Core Web Vitals) + Vercel Speed Insights |

---

## 12. Deliverables checklist

| # | Deliverable | Done when |
|---|------------|-----------|
| 1 | Auth flow (Google + email + phone OTP) | User can sign up and log in with all three providers; sessions persist across browser restarts |
| 2 | Onboarding flow | New user completes 4-question intake and sees a generated brand in < 4 minutes |
| 3 | Chat interface with streaming | AI responses stream token-by-token; rich cards render inline (images, actions, progress) |
| 4 | Preview panel — brand | Logo, colours, fonts update live as the generation progresses |
| 5 | Preview panel — website | Sandboxed iframe loads the generated site; updates after edits |
| 6 | Brand kit page | All assets viewable and downloadable (SVG, PNG, PDF) |
| 7 | Website manager | Publish/unpublish, show live URL, connect custom domain |
| 8 | Social connection | OAuth flow works for Instagram + Facebook (Phase 1) |
| 9 | Social post queue | AI-generated posts appear for review; approve/edit/reject/schedule works |
| 10 | Billing page | Paystack inline checkout, plan display, payment history |
| 11 | Dashboard | Overview cards populated with real data |
| 12 | Mobile responsive | All screens work on 375 px width; bottom nav; swipe gestures |
| 13 | PWA | `manifest.json` + service worker; installable on Android home screen |
| 14 | Lighthouse > 90 | Performance, accessibility, best practices, SEO — all above 90 on mobile |

---

## 13. Estimated timeline

### Weeks 1–2: Shell + auth + onboarding

- Next.js project scaffold with App Router, Tailwind, shadcn/ui
- Layout: sidebar, top bar, mobile bottom nav, route structure
- NextAuth with Google + email magic-link + phone OTP
- Onboarding flow: welcome screen → chat intake → style picker
- Connect to FastAPI `/api/chat/stream` — basic streaming works

### Weeks 3–4: Chat + preview + brand kit

- Full chat UI: message list, rich cards (image, progress, action, colour-picker, font-preview)
- SSE progress subscription (`useProgress` hook)
- Preview panel with Brand / Website / Social tabs
- Brand board component with live updates during generation
- Brand kit page: all assets viewable + downloadable
- Website preview iframe + publish button (calls Vercel deploy API via FastAPI)

### Week 5: Social + billing

- Social connection page (Instagram + Facebook OAuth)
- Post queue: list, approve/edit/reject, schedule
- Content calendar (month view)
- Billing page: Paystack inline checkout, plan cards, payment history
- Dashboard overview with real data

### Week 6: Mobile polish + PWA + QA

- Mobile responsive pass on every screen
- Bottom navigation, swipe gestures, pull-up preview sheet
- PWA manifest + service worker
- Lighthouse audit and fixes
- End-to-end testing: signup → intake → brand gen → website publish → social post
- Load testing the SSE connections (100 concurrent users)

**Total: 6 weeks for MVP web interface.**

After MVP: iterate based on user feedback. The chat interface and preview panel are the surfaces that will evolve fastest — keep them component-based and easy to extend.

---

## 14. Relationship to WhatsApp

The web interface is the **primary** channel. WhatsApp is **secondary** and serves:

| WhatsApp role | How it works |
|---------------|-------------|
| **Discovery** | Users who find us via WhatsApp (common in Nigeria) get a link to sign up on the web: "Start here → app.cre8ivedistrict.com" |
| **Quick interactions** | "Check my brand status", "Approve that post" — short replies that don't need the full UI |
| **Notifications** | "Your brand is ready — view it here [link]", "3 social posts need your approval [link]" |
| **Fallback for low-data users** | Users on expensive data plans can do basic interactions via WhatsApp without loading the full web app |
| **Delivery** | Brand package PDF and logo images sent directly in chat for immediate access |

The WhatsApp adapter and web app share the **same backend** — same FastAPI services, same database, same generation pipeline. The difference is only the presentation layer. A conversation started on WhatsApp can be continued on the web (and vice versa) because both are tied to the same `business_id` and `conversation` record.

The onboarding flow on WhatsApp mirrors the web version but uses text messages and WhatsApp interactive buttons instead of the rich chat cards. When the brand is ready, WhatsApp sends a link to the web app for the full visual review experience.
