# Social Media Integration — Implementation Plan

*Connect business social accounts. Generate branded content. Post with owner approval.*

**Last updated:** 2026-11-07
**Workstream:** Phase 2 feature (begins after core brand + website pipeline ships)
**Depends on:** Brand Generation Pipeline (brand guidelines feed content generation),
Billing Service (plan enforcement gates posting volume)

---

## 1. What This Delivers

A business owner connects their social media accounts to the platform. From that
point forward the AI agent:

- **Generates branded posts** — images with on-brand colors/typography plus
  platform-tailored captions — for each connected network.
- **Queues every post for review.** Nothing is published without the owner's
  explicit approval (approve, edit, reject, reschedule).
- **Publishes approved posts** to the connected accounts automatically, at the
  scheduled time or immediately.
- **Provides a content calendar** — a visual week/month view of planned,
  approved, and published posts across all platforms.
- **Tracks basic engagement** — likes, comments, shares, reach (where the
  platform API exposes it) — so the owner can see what lands.

### Supported Platforms (priority order for the Nigerian market)

| Priority | Platform | Why it matters |
|----------|----------|----------------|
| 1 | **Instagram** (Business / Creator) | THE primary sales channel for Nigerian small businesses — product showcase, DM orders, influencer culture |
| 2 | **Facebook** (Pages) | Still dominant for older demographics, local communities, event-driven businesses |
| 3 | **TikTok** (Business) | Fastest-growing platform for fashion, food, beauty — short-form video drives discovery |
| 4 | **X / Twitter** | News, tech, professional services, public discourse |
| 5 | **LinkedIn** | B2B, consulting, professional services, job seekers |

Instagram and Facebook ship together (same Meta API). TikTok and X follow.
LinkedIn is last.

---

## 2. Platform-by-Platform Integration

### 2.1 Instagram

**API:** Meta Graph API — Instagram Graph API for Business and Creator accounts.
An Instagram account must be linked to a Facebook Page to use the Content
Publishing API.

**OAuth flow:**

```
Owner clicks "Connect Instagram"
  → redirect to Facebook Login dialog
  → scopes requested:
      instagram_basic
      instagram_content_publish
      instagram_manage_comments
      instagram_manage_insights
      pages_show_list
      pages_read_engagement
      business_management
  → owner grants permissions
  → callback receives short-lived token (1 hour)
  → exchange for long-lived user token (60 days)
  → exchange user token for long-lived page token (never expires unless permissions revoked)
  → store page token + IG business account ID
```

**What we can publish:**

| Format | API Endpoint | Notes |
|--------|-------------|-------|
| Single image | `POST /{ig-user-id}/media` → `POST /{ig-user-id}/media_publish` | Two-step: create container, then publish |
| Carousel (up to 10 images) | Create child containers → create carousel container → publish | Each child is a separate `POST /{ig-user-id}/media` call |
| Reels (video) | `POST /{ig-user-id}/media` with `media_type=REELS` | Video must be hosted at a public URL; 3–90 seconds, MP4/MOV, aspect ratio 9:16 |
| Stories | **Not supported** by the Content Publishing API as of 2026 | Manual posting only — we generate the asset, owner posts it |

**What we CANNOT do:**
- Publish Stories via API
- Send or automate DMs (Messenger Platform is separate and heavily gated)
- Interact with Story replies/polls
- Post to personal (non-business) accounts

**Media requirements:**

| Format | Dimensions | Max size | File types |
|--------|-----------|----------|------------|
| Feed image | 1080×1080 (square), 1080×1350 (portrait), 1080×566 (landscape) | 8 MB | JPEG, PNG |
| Carousel image | Same as feed | 8 MB per image | JPEG, PNG |
| Reel video | 1080×1920 (9:16) | 1 GB | MP4, MOV |

**App Review:** Meta requires formal app review before any app can call
`instagram_content_publish` on behalf of other businesses. The review process:

1. Submit a screencast demo (2–5 min) showing the full flow: OAuth → content
   creation → preview → approval → publish.
2. Provide a test account the review team can log into.
3. Explain the business use case (brand management for small businesses).
4. Typical review time: **2–6 weeks.** Rejections are common on first attempt
   due to insufficient demo or missing use-case justification. Plan for 2
   submissions.
5. Once approved, the app is in **Development Mode** (limited to 5 test users)
   until you request **Live Mode** and pass a second review.

**Rate limits:**
- Content Publishing: 25 API calls per user per 24-hour period (effective limit:
  ~25 posts/day per connected account — more than sufficient).
- General Graph API: 200 calls per user per hour.

**Token refresh:** Long-lived page tokens do not expire under normal conditions.
Long-lived user tokens expire after 60 days — refresh proactively at day 50.
If refresh fails, notify the owner via WhatsApp to reconnect.

---

### 2.2 Facebook (Pages)

**API:** Meta Graph API — Pages API. Shares the same OAuth flow and app as
Instagram.

**OAuth flow:** Same as Instagram (§2.1). The `pages_manage_posts` and
`pages_read_engagement` permissions are requested alongside the IG permissions.
One OAuth grant covers both platforms.

**What we can publish:**

| Format | Endpoint | Notes |
|--------|----------|-------|
| Text post | `POST /{page-id}/feed` with `message` | Plain text |
| Photo post | `POST /{page-id}/photos` | Image + caption |
| Video post | `POST /{page-id}/videos` | Resumable upload for large files |
| Link post | `POST /{page-id}/feed` with `link` | URL preview auto-generated by Facebook |
| Multi-photo | Multiple `POST /{page-id}/photos` with `published=false` → attach IDs to a feed post | Carousel-like, up to 10 images |

**App Review:** Bundled with the Instagram review. No separate submission needed.

**Rate limits:** 200 calls per user per hour (same pool as Instagram Graph API).
Posting limit: ~25 posts per page per hour in practice.

**Media requirements:**
- Images: recommended 1200×630 (landscape); JPEG/PNG; max 10 MB.
- Video: MP4/MOV; max 10 GB; max 240 minutes.

---

### 2.3 TikTok

**API:** TikTok Content Posting API (part of the TikTok for Developers platform).

**OAuth flow:**

```
Owner clicks "Connect TikTok"
  → redirect to TikTok authorization page
  → scopes requested:
      user.info.basic
      video.publish
      video.upload
  → owner grants permissions
  → callback receives authorization code
  → exchange code for access_token (valid 24 hours) + refresh_token (valid 365 days)
  → store both tokens
  → refresh access_token proactively every 23 hours
```

**What we can publish:**

| Format | Method | Notes |
|--------|--------|-------|
| Video (direct upload) | `POST /v2/post/publish/video/init/` | Upload video file → TikTok processes → publishes |
| Video (pull from URL) | `POST /v2/post/publish/video/init/` with `source=PULL_FROM_URL` | TikTok fetches video from our CDN |
| Photo post (image slideshow) | `POST /v2/post/publish/content/init/` with `media_type=PHOTO` | 1–35 images as a slideshow with music; available since late 2024 |

**Critical limitations:**
- All posts published via API display **"Posted via [Your App Name]"** — this is
  mandatory and cannot be removed.
- TikTok requires **creator-level approval**: each user must individually
  authorize the app, AND TikTok reviews the app before granting production
  access. This is a **separate, slower process** than Meta's.
- Video-only for traditional posts (photo slideshows are newer and have separate
  API requirements).
- No scheduling built into the API — we manage scheduling ourselves.
- No DM access, no comment management via API.

**App registration:**
1. Register at TikTok for Developers.
2. Apply for Content Posting API access — requires a business justification and
   demo.
3. Review timeline: **4–8 weeks.** TikTok is the slowest to approve.
4. Sandbox testing available with limited accounts during review.

**Rate limits:**
- Video uploads: rate-limited per app and per user; documented as
  "requests per day" without specific numbers in public docs. In practice,
  ~10–20 posts per user per day is safe.
- API calls: standard OAuth-scoped rate limits apply.

**Media requirements:**
- Video: MP4/WebM; 1080×1920 (9:16) recommended; 3 seconds–10 minutes;
  max 4 GB; minimum 720p.
- Photo slideshow: JPEG/PNG/WebP; 1080×1920 recommended; 1–35 images.

**Cost:** TikTok API access is **free.** No per-call charges.

---

### 2.4 X / Twitter

**API:** X API v2.

**OAuth flow:**

```
Owner clicks "Connect X"
  → redirect to X authorization page (OAuth 2.0 with PKCE)
  → scopes requested:
      tweet.read
      tweet.write
      users.read
      offline.access (for refresh token)
  → owner grants permissions
  → callback receives authorization code
  → exchange for access_token + refresh_token
  → store both; refresh access_token before expiry (2 hours)
```

**What we can publish:**

| Format | Endpoint | Notes |
|--------|----------|-------|
| Text tweet | `POST /2/tweets` with `text` | Up to 280 characters (10,000 for Premium+) |
| Tweet + image | Upload media via `POST /1.1/media/upload` → attach `media_ids` to tweet | Up to 4 images |
| Tweet + video | Same upload flow | MP4; max 512 MB; max 140 seconds |
| Thread | Sequential `POST /2/tweets` with `reply.in_reply_to_tweet_id` | Chain of tweets |

**API tier costs:**

| Tier | Monthly cost | Post limit | Read limit |
|------|-------------|------------|------------|
| Free | $0 | 1 app-wide tweet, 1 user write | 1 app-wide read |
| Basic | $100/month | 100 posts per user per month | 10,000 reads/month |
| Pro | $5,000/month | 300,000 posts per app/month | 1,000,000 reads/month |

**Recommendation:** Start on **Basic** ($100/month). 100 posts per user per month
is ~3 posts/day — adequate for small businesses. Upgrade to Pro only when
the platform serves 50+ active X-connected businesses.

**Important:** The Free tier is useless (1 tweet total). Basic is the minimum.
Factor $100/month into platform operating costs from day one of X integration.

**Rate limits (Basic):** 100 posts per user per month; 17 requests per 15 minutes
for tweet creation.

**Media requirements:**
- Images: JPEG/PNG/GIF/WebP; max 5 MB (images), 15 MB (GIF).
- Video: MP4; max 512 MB; 0.5–140 seconds.

---

### 2.5 LinkedIn

**API:** LinkedIn Community Management API (successor to the Marketing API for
organic posting).

**OAuth flow:**

```
Owner clicks "Connect LinkedIn"
  → redirect to LinkedIn authorization page (OAuth 2.0)
  → scopes requested:
      openid
      profile
      w_member_social (personal post)
      w_organization_social (company page post)
      r_organization_social
  → owner grants permissions
  → callback receives authorization code
  → exchange for access_token (60-day expiry) + refresh_token (365 days)
  → store both; refresh proactively at day 50
```

**What we can publish:**

| Format | Method | Notes |
|--------|--------|-------|
| Text post | `POST /rest/posts` with `commentary` | Plain text to personal profile or company page |
| Image post | Register upload → upload binary → create post with image URN | Single image + text |
| Multi-image | Register multiple uploads → create post with array of image URNs | Up to 9 images |
| Article share | `POST /rest/posts` with `content.article.source` | Share a URL with commentary |
| Document/carousel | Upload document (PDF) as media → create post | PDF pages display as swipeable carousel |

**Access requirements:**
- Personal posting (`w_member_social`): available to any LinkedIn app after
  completing LinkedIn's app verification.
- Company page posting (`w_organization_social`): requires the app to be
  associated with a LinkedIn Company Page AND the owner to be an admin of that
  page.
- LinkedIn's Community Management API access requires completing their
  **developer program application** — business justification + demo. Review
  time: **2–4 weeks.**

**Rate limits:** 100 API calls per user per day for posting; 500 for reads.

**Media requirements:**
- Images: JPEG/PNG; recommended 1200×627 (landscape) or 1080×1080 (square).
- Video: MP4; max 200 MB; 3 seconds–10 minutes; direct upload via
  `registerUpload`.

**Cost:** LinkedIn API is **free.** No per-call charges.

---

## 3. OAuth Architecture

### 3.1 Universal OAuth System

All five platforms follow the same abstract pattern. We build one framework and
plug in per-platform adapters.

```
┌─────────────────────────────────────────────────────┐
│  Owner Dashboard / WhatsApp link                     │
│  "Connect Instagram" → /api/social/connect/instagram │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  OAuth Controller                         │
│  1. Build authorization URL (per platform)│
│  2. Redirect owner to platform            │
│  3. Handle callback                       │
│  4. Exchange code for tokens              │
│  5. Store tokens (encrypted)              │
│  6. Confirm connection via WhatsApp       │
└──────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  Token Store (PostgreSQL, encrypted)      │
│  - AES-256 encryption for access_tokens   │
│  - Refresh schedule per platform          │
│  - Automatic refresh before expiry        │
│  - Alert owner on refresh failure         │
└──────────────────────────────────────────┘
```

### 3.2 File Structure

```
cre8ive-platform/
  services/
    social/
      __init__.py
      oauth/
        __init__.py
        base.py            — AbstractOAuthProvider (authorize_url, exchange_code,
                             refresh_token, revoke)
        meta.py            — MetaOAuthProvider (Instagram + Facebook shared)
        tiktok.py          — TikTokOAuthProvider
        twitter.py         — XOAuthProvider (OAuth 2.0 PKCE)
        linkedin.py        — LinkedInOAuthProvider
      posting/
        __init__.py
        base.py            — AbstractPoster (publish_image, publish_video,
                             publish_text, publish_carousel, get_post_status)
        instagram.py       — InstagramPoster
        facebook.py        — FacebookPoster
        tiktok.py          — TikTokPoster
        twitter.py         — XPoster
        linkedin.py        — LinkedInPoster
      content/
        __init__.py
        generator.py       — AI content generation (prompt per platform)
        image_maker.py     — Branded image creation (overlay text on template)
        scheduler.py       — Cron-based post scheduling engine
        calendar.py        — Content calendar queries
      approval/
        __init__.py
        queue.py           — Social post approval queue
        notifications.py   — WhatsApp alerts for pending approvals
      analytics/
        __init__.py
        tracker.py         — Poll platform APIs for engagement metrics
        aggregator.py      — Roll up metrics per business
      models.py            — SocialAccount, SocialPost, PostMedia, PostMetric
      token_manager.py     — Background job: refresh tokens, alert on failure
  routers/
    social.py              — /api/social/* endpoints (connect, disconnect, posts, calendar)
    social_webhooks.py     — Platform-specific webhooks (deauthorize callbacks, etc.)
```

### 3.3 Data Model

```python
class SocialAccount(Base):
    """A connected social media account for a business."""
    __tablename__ = "social_accounts"

    id              = Column(UUID, primary_key=True, default=uuid4)
    business_id     = Column(UUID, ForeignKey("businesses.id"), nullable=False, index=True)
    platform        = Column(String(20), nullable=False)       # instagram | facebook | tiktok | x | linkedin
    platform_user_id = Column(String(120), nullable=False)     # platform's user/page ID
    account_name    = Column(String(200))                      # display name (@handle or page name)
    account_url     = Column(String(500))                      # profile URL
    access_token    = Column(Text, nullable=False)             # AES-256 encrypted
    refresh_token   = Column(Text)                             # AES-256 encrypted; NULL for Meta page tokens
    token_expires_at = Column(DateTime(timezone=True))         # NULL = never expires (Meta page tokens)
    scopes          = Column(JSONB, default=list)              # granted scopes
    status          = Column(String(20), default="active")     # active | expired | revoked | error
    connected_at    = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at    = Column(DateTime(timezone=True))
    metadata        = Column(JSONB, default=dict)              # platform-specific data (page_id for IG, etc.)

    __table_args__ = (
        UniqueConstraint("business_id", "platform", "platform_user_id"),
    )


class SocialPost(Base):
    """A social media post — generated, queued, approved, or published."""
    __tablename__ = "social_posts"

    id              = Column(UUID, primary_key=True, default=uuid4)
    business_id     = Column(UUID, ForeignKey("businesses.id"), nullable=False, index=True)
    account_id      = Column(UUID, ForeignKey("social_accounts.id"), nullable=False)
    platform        = Column(String(20), nullable=False)
    post_type       = Column(String(20), nullable=False)       # image | carousel | video | text | link
    caption         = Column(Text)                             # post text/caption
    media_urls      = Column(JSONB, default=list)              # list of S3/R2 URLs for images/videos
    hashtags        = Column(JSONB, default=list)
    status          = Column(String(20), default="draft")      # draft | queued | approved | publishing | posted | failed | rejected
    scheduled_at    = Column(DateTime(timezone=True))           # when to post (NULL = immediate on approval)
    approved_at     = Column(DateTime(timezone=True))
    approved_by     = Column(UUID)                              # user who approved
    posted_at       = Column(DateTime(timezone=True))
    platform_post_id = Column(String(200))                     # ID returned by platform after publish
    platform_post_url = Column(String(500))                    # direct URL to the live post
    error_message   = Column(Text)                             # if status=failed
    generation_prompt = Column(Text)                           # the prompt used to generate this post
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("ix_social_posts_business_status", "business_id", "status"),
        Index("ix_social_posts_scheduled", "status", "scheduled_at"),
    )


class PostMetric(Base):
    """Engagement metrics for a published post — polled periodically."""
    __tablename__ = "post_metrics"

    id              = Column(UUID, primary_key=True, default=uuid4)
    post_id         = Column(UUID, ForeignKey("social_posts.id"), nullable=False, unique=True)
    likes           = Column(Integer, default=0)
    comments        = Column(Integer, default=0)
    shares          = Column(Integer, default=0)
    reach           = Column(Integer, default=0)               # NULL if platform doesn't expose
    impressions     = Column(Integer, default=0)
    saves           = Column(Integer, default=0)               # Instagram-specific
    clicks          = Column(Integer, default=0)
    polled_at       = Column(DateTime(timezone=True))
```

---

## 4. Content Generation Pipeline

### 4.1 How the AI Generates Platform-Specific Content

```
Brand Guidelines (colors, fonts, tone, logo)
  + Business Info (name, products, audience)
  + Platform context (format, character limits, hashtag culture)
      ↓
  Content Strategy LLM Call
      → decides: what to post about this week (product spotlight,
        behind-the-scenes, customer story, promo, educational)
      → outputs: 5–7 content briefs with topic, angle, CTA
      ↓
  Per-Post Generation (one LLM call per post)
      → platform-specific caption (length, tone, hashtag style)
      → image prompt (for image generation API)
      ↓
  Image Generation
      → image gen API (DALL-E 3 / Ideogram / Flux)
      → prompt includes brand colors, style direction, product context
      → output: 1024×1024 raw image
      ↓
  Image Post-Processing
      → resize to platform dimensions (1080×1080 IG, 1200×630 FB, etc.)
      → optional: overlay brand logo watermark (subtle, corner)
      → optional: add text overlay for promotional posts
      → upload to S3/R2
      ↓
  Draft Created
      → SocialPost row with status=draft
      → notification to owner via WhatsApp
```

### 4.2 Platform-Specific Content Formats

**Instagram:**
```
System prompt: "You are a social media manager for {business_name}, a {industry}
business in {location}. Write an Instagram caption. Tone: {brand_tone}. Include
3-5 relevant hashtags (mix of popular Nigerian hashtags and niche ones). Include
a call to action. Max 2200 characters but keep the hook in the first 125
(before 'more' truncation)."
```

**Facebook:**
```
System prompt: "Write a Facebook Page post for {business_name}. Tone: {brand_tone}.
Facebook audiences prefer slightly longer, more informative posts than Instagram.
Include a question or CTA to drive engagement. No hashtag flooding — 1-2 max.
Can be up to 500 words but 100-200 is the sweet spot."
```

**TikTok:**
```
System prompt: "Write a TikTok video concept and caption for {business_name}.
The caption should be punchy, trend-aware, and under 300 characters. Include
2-3 trending TikTok hashtags. Suggest a video concept: what to show, music style,
hook in first 2 seconds. Nigerian TikTok culture is key — reference local trends."
```

**X / Twitter:**
```
System prompt: "Write a tweet for {business_name}. Max 280 characters. Be concise,
opinionated, or witty. 1-2 hashtags max. Nigerian Twitter tone: direct, sometimes
humorous, always authentic. No corporate speak."
```

**LinkedIn:**
```
System prompt: "Write a LinkedIn post for {business_name}. Professional tone but
not stiff. Story-driven format works best (hook → context → insight → CTA).
300-600 words. 3-5 relevant hashtags. This is B2B — focus on value, expertise,
or behind-the-scenes insights."
```

### 4.3 Image Generation Per Platform

| Platform | Primary format | Dimensions | Style notes |
|----------|---------------|------------|-------------|
| Instagram feed | Square or portrait | 1080×1080 or 1080×1350 | Clean, branded, product-focused |
| Instagram story/reel cover | Portrait | 1080×1920 | Bold text, high contrast |
| Facebook | Landscape | 1200×630 | Informative, can include more text |
| X | Landscape | 1600×900 | Eye-catching, minimal text |
| LinkedIn | Landscape or square | 1200×627 or 1080×1080 | Professional, clean |
| TikTok cover | Portrait | 1080×1920 | Energetic, bold, trend-aware |

---

## 5. Approval Flow

### 5.1 Draft → Publish Lifecycle

```
DRAFT → QUEUED → APPROVED → PUBLISHING → POSTED
  │        │         │           │
  │        │         │           └→ FAILED (retry or manual fix)
  │        │         └→ (scheduled_at reached → publishing begins)
  │        └→ REJECTED (owner declines; stays in library for later)
  └→ (AI generates; enters queue for review)
```

### 5.2 Approval Interface

**Dashboard (primary):**
- Approval queue page showing all posts with status `queued`
- Preview card per post: image thumbnail, caption text, target platform icon,
  scheduled date/time
- Actions: **Approve** (green), **Edit** (pencil — opens caption/schedule editor),
  **Reject** (red), **Reschedule** (calendar picker)
- Batch mode: checkbox per post → "Approve selected" / "Approve all"

**WhatsApp (secondary, for quick decisions):**
- Notification: "You have 5 posts ready for review for {business_name}. [Review
  now →]" with a link to the dashboard.
- For single posts: send image preview + caption as a WhatsApp message, with
  interactive buttons: **Approve** / **Reject** / **View in dashboard**
- Only simple approve/reject via WhatsApp; editing requires the dashboard.

### 5.3 Scheduling Engine

A background worker runs every 60 seconds:

```python
async def publish_due_posts():
    """Find approved posts whose scheduled_at has passed and publish them."""
    due = await db.execute(
        select(SocialPost)
        .where(SocialPost.status == "approved")
        .where(SocialPost.scheduled_at <= func.now())
        .order_by(SocialPost.scheduled_at)
        .limit(10)
    )
    for post in due.scalars():
        post.status = "publishing"
        await db.commit()
        try:
            poster = get_poster(post.platform)
            result = await poster.publish(post)
            post.platform_post_id = result.post_id
            post.platform_post_url = result.url
            post.posted_at = func.now()
            post.status = "posted"
        except PlatformError as e:
            post.status = "failed"
            post.error_message = str(e)
            # notify owner
        await db.commit()
```

---

## 6. Connection Flow (User Experience)

### 6.1 Via Dashboard

```
1. Owner opens dashboard → "Social Accounts" section
2. Sees available platforms with "Connect" buttons
3. Clicks "Connect Instagram"
4. Redirected to Facebook Login (Meta handles auth)
5. Owner grants permissions to Cre8ive District app
6. Redirected back to dashboard callback URL
7. System exchanges code for tokens, stores encrypted
8. Dashboard shows: "✓ Instagram connected — @business_handle"
9. WhatsApp confirmation: "Your Instagram account @business_handle is now connected!"
```

### 6.2 Via WhatsApp (Mobile-First Flow)

```
Owner messages: "I want to connect my Instagram"
  → AI responds: "Great! Tap this link to connect your Instagram account.
     You'll be asked to log in and grant permission — it takes about 30 seconds."
     [Connect Instagram →] (link to dashboard OAuth start page)
  → Owner taps link → opens phone browser → completes OAuth on phone
  → Callback page shows "Connected!" and suggests returning to WhatsApp
  → WhatsApp: "Done! Your Instagram @business_handle is connected.
     I'll start creating posts for you. Would you like me to generate
     your first week of content?"
```

### 6.3 Token Management

| Platform | Access token life | Refresh method | Our refresh schedule |
|----------|------------------|----------------|---------------------|
| Instagram/Facebook (page token) | Never expires | N/A (exchanged from long-lived user token) | Check validity weekly; re-auth if Page disconnected |
| Instagram/Facebook (user token) | 60 days | `GET /oauth/access_token?grant_type=fb_exchange_token` | Refresh at day 50 |
| TikTok | 24 hours | `POST /v2/oauth/token` with refresh_token (365-day life) | Refresh every 23 hours via cron |
| X / Twitter | 2 hours | `POST /2/oauth2/token` with refresh_token (6-month life) | Refresh every 110 minutes via cron |
| LinkedIn | 60 days | `POST /oauth/v2/accessToken` with refresh_token (365 days) | Refresh at day 50 |

**Failure handling:** If a token refresh fails (owner revoked access, password
changed, etc.):
1. Mark `SocialAccount.status = "expired"`
2. Pause all scheduled posts for that account
3. Send WhatsApp: "Your Instagram connection expired. Tap here to reconnect →"
4. Retry refresh once more after 1 hour before alerting

### 6.4 Disconnection

- Owner clicks "Disconnect" in dashboard or says "disconnect my Instagram" on WhatsApp
- Revoke token via platform's API where supported
- Delete stored tokens
- Mark `SocialAccount.status = "revoked"`
- Cancel all scheduled posts for that account
- Confirm via WhatsApp: "Instagram disconnected. Your posts and data are still saved."

---

## 7. WhatsApp Notification Integration

| Trigger | WhatsApp message | Timing |
|---------|-----------------|--------|
| Weekly content batch ready | "Your posts for this week are ready for review! 7 posts across Instagram and Facebook. [Review now →]" | Monday 9 AM (configurable) |
| Single post pending | Image preview + caption + [Approve] [Reject] buttons | As generated, during business hours |
| Post published | "Just posted to your Instagram! [View post →]" | Immediately after successful publish |
| Post failed | "Couldn't post to Instagram — {error reason}. [Retry] [View in dashboard →]" | Immediately |
| Token expired | "Your {platform} connection needs refreshing. [Reconnect →]" | After failed refresh attempt |
| Weekly performance summary | "This week: 5 posts, 342 likes, 28 comments, 12 shares. Top post: {preview}. [See full report →]" | Sunday 6 PM |

---

## 8. Phasing

### Phase 2A — Instagram + Facebook (Weeks 9–12)

**Why first:** Same Meta API covers both. Instagram is the #1 priority for
Nigerian businesses. One app review process.

| Week | Deliverable |
|------|------------|
| 9 | Meta OAuth integration (connect/disconnect/refresh), SocialAccount storage, dashboard UI for connection management |
| 10 | Instagram posting (single image + carousel), Facebook posting (photo + text), content generation prompts per platform |
| 11 | Approval queue (dashboard + WhatsApp notifications), scheduling engine, content calendar view |
| 12 | Image generation pipeline for social posts (branded images using the business's brand guidelines), testing with real Meta accounts, submit Meta app review |

**Deliverables:**
- [ ] Meta OAuth connect/disconnect flow (dashboard + WhatsApp-initiated)
- [ ] Token storage (AES-256 encrypted) + automatic refresh
- [ ] Instagram single image + carousel publishing
- [ ] Facebook photo + text + link publishing
- [ ] AI content generation with platform-specific prompts
- [ ] Branded image generation for social posts
- [ ] Approval queue with approve/edit/reject/reschedule
- [ ] WhatsApp notification for pending approvals
- [ ] Post scheduling (pick date/time, auto-publish)
- [ ] Content calendar (week view, showing draft/approved/posted)
- [ ] Basic engagement tracking (likes, comments, shares)
- [ ] Meta App Review submission (may take 2–6 weeks to clear)

### Phase 2B — TikTok + X (Weeks 13–16)

| Week | Deliverable |
|------|------------|
| 13 | TikTok OAuth + Content Posting API integration, video concept generation |
| 14 | X OAuth (PKCE) + tweet posting (text, image, threads), API tier management |
| 15 | Cross-platform content calendar (unified view across all connected platforms), batch scheduling |
| 16 | Testing, TikTok app review submission, polish |

**Deliverables:**
- [ ] TikTok OAuth + video/photo slideshow posting
- [ ] X/Twitter OAuth + tweet/thread posting
- [ ] TikTok video concept generation (script + style direction — actual video gen is Phase 3)
- [ ] Photo slideshow posting for TikTok (product showcase format)
- [ ] Unified content calendar across all 4 platforms
- [ ] Batch content generation ("generate a week of posts for all my platforms")
- [ ] X API Basic tier subscription management ($100/month platform cost)

### Phase 3 — LinkedIn + Advanced Features (Weeks 17–20)

| Week | Deliverable |
|------|------------|
| 17 | LinkedIn OAuth + posting (text, image, document/carousel) |
| 18 | Video generation for TikTok/Reels (AI video from product images + music) |
| 19 | Analytics dashboard (engagement trends, best-performing posts, platform comparison) |
| 20 | Content AI improvements: auto-suggest trending topics, repurpose one post across platforms, A/B caption testing |

**Deliverables:**
- [ ] LinkedIn OAuth + posting to profiles and company pages
- [ ] AI video generation (product images → short video with music + transitions)
- [ ] Analytics dashboard with engagement trends
- [ ] Content repurposing: one brief → posts for all connected platforms
- [ ] Auto-suggest topics based on trending hashtags/topics in Nigeria
- [ ] Performance-based learning: prioritize content types that get more engagement

---

## 9. API Costs and Limits

| Platform | API cost | Rate limits (posting) | Notes |
|----------|---------|----------------------|-------|
| **Instagram** | Free | 25 posts/user/day | Must pass Meta app review |
| **Facebook** | Free | 25 posts/page/hour | Bundled with IG review |
| **TikTok** | Free | ~10–20 videos/user/day | Slowest app review (4–8 weeks) |
| **X / Twitter** | **$100/month** (Basic) | 100 posts/user/month | Only platform with a hard API cost; Free tier is unusable |
| **LinkedIn** | Free | 100 posts/user/day | Requires developer program access |

**Monthly platform costs at scale:**

| Scale | X API | Image gen (est. 5 posts/business/week) | Total social infra |
|-------|-------|---------------------------------------|-------------------|
| 50 businesses | $100 | ~$75 (750 images × $0.10) | ~$175/month |
| 200 businesses | $100 | ~$300 (3,000 images × $0.10) | ~$400/month |
| 500 businesses | $100 (or $5,000 Pro) | ~$750 | ~$850–$5,750/month |

X API cost is fixed regardless of user count (until you hit Pro-tier limits).
Image generation is the variable cost.

---

## 10. Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Meta app review rejection** | High | Prepare thorough submission with screencast, test accounts, clear use-case doc. Budget for 2 submission attempts. Start review process in Week 9 even if features aren't complete — the review assesses the concept, not finished polish. |
| **TikTok API access delay** | High | TikTok is 4–8 weeks for review. Submit early. In the interim, generate TikTok-ready content (video concepts + images) that owners can manually post — still valuable. |
| **Token expiration / revocation** | Medium | Proactive refresh cron. Immediate WhatsApp alert on failure. Graceful degradation: posts pause, owner is prompted to reconnect, nothing is lost. |
| **Platform API changes** | Medium | Abstract `Poster` interface means swapping one adapter doesn't touch others. Pin API versions. Monitor platform changelogs. |
| **Content policy violations** | Medium | Pre-check captions for prohibited content before publishing. Image generation prompts include safety guidelines. If a platform rejects a post, capture the error and notify the owner with the reason. |
| **X API cost at scale** | Low | $100/month is manageable. Defer X integration if budget is tight — Instagram + Facebook cover 80% of Nigerian small business social needs. |
| **Rate limit hitting** | Low | At 25 posts/user/day on Instagram, even aggressive posting won't hit limits. Implement exponential backoff + per-user rate tracking as insurance. |
| **Image generation quality** | Medium | Brand consistency is hard with AI images. Use the brand color palette in every prompt. Post-process to add logo watermark. Have the human review queue catch poor generations before they reach the owner. |

---

## 11. Deliverables Checklist (Full Feature)

### Infrastructure
- [ ] `SocialAccount` model + migrations
- [ ] `SocialPost` model + migrations
- [ ] `PostMetric` model + migrations
- [ ] AES-256 token encryption/decryption utility
- [ ] Token refresh background worker (per-platform schedules)
- [ ] Token expiry alerting (WhatsApp notification)

### OAuth (per platform)
- [ ] Meta OAuth (Instagram + Facebook) — connect, disconnect, refresh
- [ ] TikTok OAuth — connect, disconnect, refresh
- [ ] X OAuth (PKCE) — connect, disconnect, refresh
- [ ] LinkedIn OAuth — connect, disconnect, refresh
- [ ] Dashboard UI: connection management page

### Posting (per platform)
- [ ] Instagram: single image, carousel
- [ ] Facebook: photo, text, link
- [ ] TikTok: video upload, photo slideshow
- [ ] X: tweet (text + image), threads
- [ ] LinkedIn: text, image, document carousel

### Content Generation
- [ ] Platform-specific caption generation prompts
- [ ] Branded image generation (using brand guidelines)
- [ ] Weekly content batch generation ("generate this week's posts")
- [ ] Content repurposing (one brief → all platforms)

### Approval & Scheduling
- [ ] Approval queue (dashboard)
- [ ] WhatsApp approval notifications (with interactive buttons)
- [ ] Scheduling engine (background worker publishes at scheduled time)
- [ ] Content calendar (week/month view, all platforms)
- [ ] Batch approve/reject

### Analytics
- [ ] Post engagement polling (likes, comments, shares, reach)
- [ ] Weekly performance summary (WhatsApp + dashboard)
- [ ] Best-performing post tracking

### Platform Registrations (non-code, owner tasks)
- [ ] Meta App Review submission (Instagram + Facebook)
- [ ] TikTok Developer app + Content Posting API review
- [ ] X API Basic tier subscription ($100/month)
- [ ] LinkedIn Developer Program application

---

## 12. Estimated Timeline

| Week | Focus | Milestone |
|------|-------|-----------|
| **9** | Meta OAuth + token storage + dashboard connection UI | Owners can connect/disconnect Instagram & Facebook |
| **10** | IG + FB posting adapters + content generation prompts | First AI-generated post published to a test IG account |
| **11** | Approval queue + scheduling engine + WhatsApp notifications | Full draft → approve → publish flow working end-to-end |
| **12** | Branded image generation + content calendar + Meta app review submission | Social media feature complete for IG + FB; review submitted |
| **13** | TikTok OAuth + posting + video concept generation | TikTok connected; photo slideshow posts working |
| **14** | X OAuth + tweet posting + thread support | X connected; tweets publishing |
| **15** | Unified cross-platform calendar + batch generation | One button generates a full week of posts for all platforms |
| **16** | Testing + polish + TikTok app review submission | Phase 2B complete; TikTok review in progress |
| **17** | LinkedIn OAuth + posting | LinkedIn connected; posts publishing |
| **18** | AI video generation (product images → short video) | TikTok Reels / IG Reels video content |
| **19** | Analytics dashboard + engagement tracking | Owner sees how posts perform |
| **20** | Auto-suggest topics + content learning + polish | Phase 3 complete |

**Total: 12 weeks** (Weeks 9–20 of the overall project timeline, starting after
the core brand + website pipeline ships in Weeks 1–8).