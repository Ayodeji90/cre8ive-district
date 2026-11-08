# WhatsApp Intake Flow — Implementation Plan

*The primary interface for Cre8ive District's AI-powered brand platform. Nigerian
businesses describe what they do on WhatsApp, and the AI guides them from first
message to delivered brand package.*

**Last updated:** 2026-11-07

---

## 1. What This Delivers

A customer messages our WhatsApp Business number and receives a complete,
guided brand-building experience:

1. **Greeted** by our AI brand consultant
2. **Guided** through a conversational intake — business name, what they sell/do,
   target audience, style preferences, industry
3. **Receives brand concepts** for review — logo options, color palettes, and
   typography sent as images directly in-chat
4. **Approves or requests changes** via simple replies or interactive buttons
5. **Gets their brand package delivered** — guidelines PDF + logo files sent as
   WhatsApp documents, download link for full asset pack
6. **Receives a link** to their generated website (if included in their plan)
7. **Pays** via Paystack payment link sent in-chat
8. **Follow-up** sequence begins — check-ins at day 3 and day 7

**Target end-to-end time:** 15–30 minutes from first message to brand package
delivered. Website generation adds another 5–10 minutes.

---

## 2. Conversation Design — The State Machine

Every customer conversation follows a deterministic state machine. The AI
operates within each state's boundaries — it can be conversational and warm,
but the *transitions* between states are controlled by the system, not the LLM.

```
┌─────────┐
│  START   │ ← customer sends first message
└────┬─────┘
     ▼
┌──────────┐
│ GREETING │ → welcome, explain what we do, ask if they're ready
└────┬─────┘
     ▼
┌───────────────┐
│ BUSINESS_INFO │ → business name, what they sell/do, location
└────┬──────────┘
     ▼
┌──────────────────┐
│ INDUSTRY_DETAILS │ → industry category, target customers, competitors
└────┬─────────────┘
     ▼
┌─────────────────────┐
│ STYLE_PREFERENCES   │ → brand personality, color leanings, examples they like
└────┬────────────────┘
     ▼
┌────────────┐
│ PLAN_SELECT│ → show pricing options, customer picks a package
└────┬───────┘
     ▼
┌────────────┐
│ GENERATING │ → "building your brand now…" with progress updates
└────┬───────┘
     ▼
┌──────────────┐
│ REVIEW_BRAND │ → send logo concepts + palette, ask for approval
└────┬─────────┘
     │
     ├──→ APPROVED ──→ ┐
     │                  │
     └──→ CHANGES ──────┤ (loop back to GENERATING, max 3 rounds)
                        │
     ┌──────────────────┘
     ▼
┌──────────────────┐
│ GENERATING_SITE  │ → (if plan includes website) build + deploy
└────┬─────────────┘
     ▼
┌──────────┐
│ PAYMENT  │ → send Paystack link, wait for confirmation
└────┬─────┘
     ▼
┌──────────┐
│ DELIVERY │ → send final assets (PDF, images, links)
└────┬─────┘
     ▼
┌──────────┐
│ COMPLETE │ → thank you + schedule follow-ups
└──────────┘
```

### State Definitions

#### START
**Trigger:** Any inbound message to our WhatsApp number from a new sender.
**Action:** Create a session, transition to GREETING.

#### GREETING
**AI sends:**
```
Hey! 👋 Welcome to Cre8ive District.

We help businesses launch with a professional brand — logo, colors, website,
the works. And we do it fast, using AI + our design team.

Ready to build your brand? Just tell me a bit about your business and
we'll get started.

Or if you have questions first, ask away — I'm here.
```
**Expected input:** Anything — a business description, a question, "yes", etc.
**Transition:** If the message contains business info (detected by LLM), skip
to BUSINESS_INFO and extract what we can. If it's a question, answer it and
re-prompt. If it's affirmative ("yes", "let's go"), ask the first intake
question.

#### BUSINESS_INFO
**AI sends (if not already provided):**
```
Great — let's start with the basics:

1️⃣ What's the name of your business? (Or if you don't have one yet, tell me
   what you're thinking and I can suggest some)
2️⃣ What do you sell or do?
3️⃣ Where are you based?

You can answer all three at once or one at a time — however you like.
```
**Data extracted:** `business_name`, `business_description`, `location`
**Validation:** Business name must be non-empty. Description must be at least
10 words or the AI asks a follow-up.
**Transition:** Once all three fields are captured → INDUSTRY_DETAILS.

#### INDUSTRY_DETAILS
**AI sends:**
```
Nice — [business_name] sounds solid. A few more questions to make sure
your brand fits your market:

• Who are your ideal customers? (e.g. "young professionals in Lagos",
  "mothers looking for organic baby food")
• What makes you different from others doing the same thing?
• Any businesses you admire the look of? (can be Nigerian or international)
```
**Data extracted:** `target_audience`, `differentiator`, `brand_references`
**Transition:** Once sufficient detail captured → STYLE_PREFERENCES.

#### STYLE_PREFERENCES
**AI sends (using WhatsApp interactive list message):**
```
Now for the fun part — the look and feel of your brand.

Pick the style that feels closest to what you want:
```
**List options:**
- 🌿 *Clean & Minimal* — Simple, lots of space, modern
- 🔥 *Bold & Energetic* — Strong colors, loud presence
- ✨ *Warm & Friendly* — Soft, welcoming, approachable
- 🏛️ *Classic & Premium* — Sophisticated, refined, established
- 🎨 *Creative & Playful* — Fun, colorful, unique

**Follow-up:**
```
Any colors you love or hate? (e.g. "I love green" or "no pink please")
```
**Data extracted:** `style_direction`, `color_preferences`
**Transition:** → PLAN_SELECT.

#### PLAN_SELECT
**AI sends (using WhatsApp interactive buttons):**
```
Here's what I can build for you:

🟢 *Brand Starter* — ₦20,000
Logo + colors + fonts + brand guidelines PDF

🔵 *Brand + Website* — ₦60,000
Everything above + a 3-5 page website hosted for you

⭐ *Brand Complete* — ₦120,000
Everything above + social media kit + Google Business Profile
+ review by our human design team

Which one works for you?
```
**Buttons:** `Brand Starter ₦20k` | `Brand + Web ₦60k` | `Brand Complete ₦120k`
**Transition:** Customer selects → GENERATING.

#### GENERATING
**AI sends:**
```
Building your brand now — this usually takes about 3-5 minutes. ⏳

I'll send you the concepts as soon as they're ready. You can keep
chatting with me in the meantime if you want.
```
**System action:** Dispatch brand generation job to the Brand Generation
Service. Send progress updates at 30-second intervals:
```
🎨 Working on your color palette…
✏️ Designing logo concepts…
📐 Finalizing your brand system…
```
**Transition:** When generation completes → REVIEW_BRAND.

#### REVIEW_BRAND
**AI sends:** 2-3 logo concept images + a color palette image + a text
summary of the brand direction.
```
Here's what I've built for [business_name]:

[Image: Logo concept 1]
[Image: Logo concept 2]
[Image: Color palette card]

🎨 Colors: [primary] + [secondary] + [accent]
✏️ Fonts: [heading font] + [body font]

What do you think? You can:
• ✅ *Approve* — and I'll finalize everything
• 🔄 *Request changes* — tell me what to adjust
• 🔁 *Start over* — with a completely different direction
```
**Buttons:** `Approve ✅` | `Request changes 🔄` | `Start over 🔁`
**Transition:**
- Approve → GENERATING_SITE (if plan includes website) or PAYMENT
- Changes → AI asks what to change, re-enters GENERATING (max 3 revision
  rounds, then offer human designer escalation)
- Start over → back to STYLE_PREFERENCES

#### PAYMENT
**AI sends:**
```
Your brand package is ready! 🎉

To get your files, here's your payment link:

💳 [Paystack payment link]

You can pay by bank transfer, card, or USSD — whatever works for you.
I'll send everything the moment payment confirms.
```
**Transition:** Paystack webhook confirms payment → DELIVERY. If no payment
after 1 hour, send a reminder. After 24 hours, send a final nudge. After
72 hours, mark session as `payment_pending` and stop messaging.

#### DELIVERY
**AI sends:**
```
Payment confirmed — thank you! 💪

Here's your complete brand package:

📄 [Document: Brand Guidelines PDF]
🖼️ [Image: Primary logo (high-res)]
🖼️ [Image: Logo icon mark]
🔗 Download all files: [link to hosted asset pack]
```
If website was generated:
```
And your website is live! 🌐
👉 [website URL]

You can share this link anywhere — it works on all devices.
```
**Transition:** → COMPLETE.

#### COMPLETE
**AI sends:**
```
You're all set! Welcome to the Cre8ive District family. 🙌

If you need any changes or have questions, just message me here anytime.

We'll check in with you in a few days to see how everything's working.
```
**System action:** Schedule follow-up messages:
- Day 3: "Hey [name]! How's the new brand working out? Need any changes?"
- Day 7: "Quick check-in — has anyone commented on the new look? If you
  need tweaks to the website or brand materials, just say the word."

### Handling Edge Cases

**Voice notes:** Transcribe using OpenAI Whisper API. Prepend `[Voice note
transcription]:` to the text and process as normal. If transcription
confidence is low, ask the customer to type it out.

**Images sent by customer:** If customer sends a reference image ("I want
something like this"), store it and pass to the brand generation pipeline
as a style reference. Acknowledge: "Got it — I'll use that as inspiration."

**Off-topic messages:** The LLM handles casual conversation naturally. If
the customer goes far off-topic, gently steer back: "Ha — good question!
But let's get your brand sorted first. Where were we?"

**"How much?" before intake:** Jump to PLAN_SELECT, then loop back to
BUSINESS_INFO after they choose a plan.

**Multiple people from same business:** Session is tied to the phone number.
If a different person messages, the AI asks if they're continuing the
existing brand project or starting a new one.

**Customer goes silent:** Timeouts per state:
- During intake (GREETING through STYLE_PREFERENCES): 1 hour → gentle
  nudge. 24 hours → "No rush — your progress is saved. Message me whenever
  you're ready to continue."
- During GENERATING/REVIEW: No timeout (we're working).
- During PAYMENT: 1 hour → reminder. 24 hours → final nudge. 72 hours → stop.

---

## 3. WhatsApp Business API Integration

### BSP Recommendation: **WhatsApp Cloud API (direct)**

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| WhatsApp Cloud API (direct) | Free, no BSP markup, Meta-hosted, most up-to-date features | Requires Meta Business verification; rate limits are per-phone-number | **★★★★★ Recommended** |
| 360dialog | Fast onboarding, good African support | Monthly fee + per-conversation markup | ★★★★☆ Fallback |
| Twilio | Well-documented, reliable | Expensive markup per message, US-centric support | ★★★☆☆ |

**Why Cloud API direct:** Zero per-message cost for service conversations
(customer-initiated, 24-hour window). We only pay for template messages
(outbound-initiated), which are ~$0.004 each. At our scale (<1,000
conversations/month initially), the cost is negligible.

### Webhook Architecture

```python
# routers/whatsapp.py

@router.post("/webhooks/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Receives all inbound WhatsApp events from the Cloud API.
    Verifies the webhook signature, then dispatches to handlers.
    """
    body = await request.json()
    
    # Verify webhook signature (X-Hub-Signature-256 header)
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not verify_signature(body, signature, settings.WA_APP_SECRET):
        raise HTTPException(403, "Invalid signature")
    
    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            if change["field"] == "messages":
                value = change["value"]
                for message in value.get("messages", []):
                    await handle_inbound_message(
                        phone=message["from"],
                        message=message,
                        metadata=value["metadata"],
                    )
                for status in value.get("statuses", []):
                    await handle_status_update(status)
    
    return {"status": "ok"}
```

### Message Types Used

| Type | WhatsApp API Type | When Used |
|------|------------------|-----------|
| Text | `text` | Most conversation messages |
| Image | `image` | Sending logo concepts, palette cards |
| Document | `document` | Sending brand guidelines PDF |
| Interactive buttons | `interactive.button` | Approve/change/start-over choices |
| Interactive list | `interactive.list` | Style preference selection, plan selection |
| Template | `template` | Follow-up messages (outside 24h window), payment reminders |

### Template Messages (Pre-Approved)

These must be submitted to Meta for approval before use:

**`brand_followup_day3`**
```
Hi {{1}}! 👋 It's been a few days since we delivered your brand package
for {{2}}. How's everything looking? Need any tweaks?

Reply here anytime — we're ready to help.
```

**`payment_reminder`**
```
Hi {{1}}! Your brand package for {{2}} is ready and waiting. 💼

Pay here to get your files: {{3}}

Questions? Just reply to this message.
```

**`brand_delivery_complete`**
```
Great news, {{1}}! 🎉 Your brand package for {{2}} is complete.

📄 Brand guidelines: {{3}}
🌐 Your website: {{4}}

Message us anytime if you need changes.
```

### Media Handling

**Sending images (logo concepts):**
```python
async def send_image(phone: str, image_url: str, caption: str):
    """Send a logo concept or palette card via WhatsApp."""
    await wa_client.post(f"{WA_API_URL}/{PHONE_NUMBER_ID}/messages", json={
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "image",
        "image": {
            "link": image_url,  # publicly accessible URL (S3/R2)
            "caption": caption,
        },
    })
```

**Sending documents (PDF):**
```python
async def send_document(phone: str, doc_url: str, filename: str):
    await wa_client.post(f"{WA_API_URL}/{PHONE_NUMBER_ID}/messages", json={
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "document",
        "document": {
            "link": doc_url,
            "filename": filename,
            "caption": "Your brand guidelines — tap to download",
        },
    })
```

**Receiving voice notes:**
```python
async def handle_voice_note(message: dict) -> str:
    """Download and transcribe a customer's voice note."""
    media_id = message["audio"]["id"]
    media_url = await get_media_url(media_id)
    audio_bytes = await download_media(media_url)
    
    transcript = await openai_client.audio.transcriptions.create(
        model="whisper-1",
        file=("voice.ogg", audio_bytes, "audio/ogg"),
        language="en",  # or detect; Whisper handles Pidgin reasonably well
    )
    return transcript.text
```

### Rate Limits

WhatsApp Cloud API enforces messaging limits based on phone number quality:
- **Tier 1 (new):** 1,000 unique customers/24h
- **Tier 2:** 10,000/24h
- **Tier 3:** 100,000/24h

For launch phase (<100 conversations/day), Tier 1 is sufficient. Quality
rating must stay "Green" — which means low block/report rate.

### Approval Process & Timeline

1. Create a Meta Business account (if not existing) — **1 day**
2. Create a WhatsApp Business account in Meta Business Manager — **1 day**
3. Verify the business (requires business documents) — **3-14 days**
4. Register a phone number — **1 day**
5. Submit message templates for approval — **1-3 days per template**

**Total: 1-3 weeks.** Start this process immediately — it's the longest
lead time in the entire project.

**Fallback while waiting:** Launch with a web chat widget on the Cre8ive
District website. The conversation flow is identical; only the transport
layer differs. Swap to WhatsApp when approved.

---

## 4. AI Orchestration

### System Prompt — Brand Consultant Persona

```
You are the Cre8ive District brand consultant, speaking with customers on
WhatsApp. You help Nigerian businesses build their brand identity.

YOUR PERSONALITY:
- Warm, professional, and encouraging — like a friend who happens to be
  a great designer
- Speak naturally in English. If the customer writes in Pidgin, match
  their energy and respond in Pidgin too
- Keep messages SHORT — this is WhatsApp, not email. 2-4 sentences max
  per message. Use line breaks
- Use emojis sparingly — one or two per message, not every sentence

YOUR JOB:
- Guide the customer through the brand intake process
- Collect: business name, what they do, location, target audience,
  differentiator, style preferences, color leanings
- Be conversational — don't make it feel like a form. React to what
  they tell you. Show genuine interest in their business
- When you have enough information, summarize what you've learned and
  confirm before we start generating

RULES:
- Never make up information about Cre8ive District's services or pricing.
  If unsure, say "let me check with my team"
- Never promise delivery times you can't keep. Brand generation takes
  3-5 minutes. Website generation takes 5-10 minutes
- If the customer asks about something outside brand services (e.g.
  accounting, legal), acknowledge it and steer back: "That's outside
  what we do, but for your brand — let's keep going"
- If the customer is frustrated or unhappy with a concept, be
  understanding. Offer to adjust or escalate to a human designer
- After 3 revision rounds, offer to connect them with a human designer
  from our team

CURRENT STATE: {{current_state}}
COLLECTED DATA SO FAR: {{session_data}}
CONVERSATION HISTORY: {{recent_messages}}

Respond to the customer's latest message. Keep it short and natural.
If you have enough data to move to the next step, do so — but confirm
with the customer first.
```

### Context Maintenance

Each WhatsApp conversation maps to a session stored in Redis (hot) and
PostgreSQL (persistent):

```python
@dataclass
class ConversationSession:
    id: str                          # UUID
    phone: str                       # customer's WhatsApp number
    state: ConversationState         # current state machine state
    business_data: BusinessIntake    # collected intake data
    messages: list[Message]          # last 20 messages (context window)
    brand_job_id: str | None         # if brand generation is in progress
    site_job_id: str | None          # if website generation is in progress
    order_id: str | None             # if payment initiated
    revision_count: int              # number of brand revision rounds
    created_at: datetime
    last_activity: datetime
    
    # Redis key: f"session:{phone}"
    # TTL: 72 hours (reset on each message)
```

```python
class BusinessIntake(BaseModel):
    """Structured data extracted from conversation."""
    business_name: str | None = None
    description: str | None = None
    location: str | None = None
    industry: str | None = None
    target_audience: str | None = None
    differentiator: str | None = None
    style_direction: str | None = None  # clean|bold|warm|classic|creative
    color_preferences: str | None = None
    color_avoidances: str | None = None
    brand_references: list[str] = []  # URLs or descriptions of brands they like
    reference_images: list[str] = []  # media IDs of images customer sent
    selected_plan: str | None = None  # starter|web|complete
    
    def is_ready_for_generation(self) -> bool:
        """Minimum viable intake for brand generation."""
        return all([
            self.business_name,
            self.description,
            self.style_direction or self.color_preferences,
        ])
```

### Structured Data Extraction

After each customer message, the LLM extracts any new structured fields:

```python
EXTRACTION_PROMPT = """
Given this customer message in a brand-building conversation, extract
any business information mentioned. Return JSON with only the fields
that are NEW or UPDATED in this message. Omit fields not mentioned.

Customer message: "{message}"

Current known data: {current_data}

Extract into: {{
  "business_name": "...",
  "description": "...",
  "location": "...",
  "industry": "...",
  "target_audience": "...",
  "differentiator": "...",
  "color_preferences": "...",
  "color_avoidances": "..."
}}

Return ONLY the JSON object with fields that were mentioned or updated
in this specific message. Return {{}} if nothing new was mentioned.
"""
```

This extraction runs in parallel with the conversational response —
the customer gets a natural reply while the system quietly updates the
structured intake data.

### Multi-Language Support

The LLM naturally handles code-switching (English ↔ Pidgin is extremely
common among Nigerian business owners). The system prompt instructs it
to match the customer's register.

Example Pidgin interaction:
```
Customer: "I dey sell ankara fabric for Balogun market"
AI: "Ankara fabric! That's a strong market. Your customers — na mostly
    women wey dey sew, or you dey sell retail too?"
```

No separate language detection step needed — the LLM handles this
natively. For Yoruba/Haiku/Igbo, the LLM responds in English with the
occasional term in the customer's language where natural.

### Triggering Brand Generation

```python
async def check_and_trigger_generation(session: ConversationSession):
    """
    Called after every message in STYLE_PREFERENCES state.
    If we have enough data, confirm with customer and start generating.
    """
    if session.business_data.is_ready_for_generation():
        # Ask LLM to generate a confirmation summary
        summary = await generate_intake_summary(session.business_data)
        
        await send_text(session.phone, f"""
Here's what I've got so far:

📋 *{session.business_data.business_name}*
{summary}

Does that sound right? I'll start building your brand once you confirm.
""")
        
        session.state = ConversationState.CONFIRM_INTAKE
        # Customer confirms → transition to GENERATING → dispatch job
```

---

## 5. Session Management

### Storage Architecture

```
┌─────────────────┐     ┌──────────────────┐
│  Redis           │     │  PostgreSQL       │
│  (hot sessions)  │     │  (permanent)      │
│                  │     │                   │
│  session:{phone} │────▶│  conversations    │
│  TTL: 72h        │     │  messages         │
│  (full session   │     │  businesses       │
│   state + last   │     │  orders           │
│   20 messages)   │     │                   │
└─────────────────┘     └──────────────────┘
```

- **Redis:** Active session state. Every message reads from Redis first.
  If the key has expired, check PostgreSQL for a recent conversation
  and resume it.
- **PostgreSQL:** Every message is persisted (for analytics, support,
  and conversation continuity). Business intake data is saved after
  each extraction update.

### Timeout Rules

| State | Nudge after | Final message after | Close after |
|-------|-------------|--------------------|----|
| GREETING → STYLE_PREFERENCES | 1 hour | 24 hours | 7 days |
| GENERATING / REVIEW_BRAND | No timeout | — | — |
| PAYMENT | 1 hour | 24 hours | 72 hours |
| COMPLETE | — | — | — |

Nudge messages are sent as regular messages (within the 24h window). If
outside the 24h window, use the approved template message.

### Human Handoff

Triggered when:
- Customer explicitly asks for a human ("can I talk to someone?")
- 3 brand revision rounds exhausted
- Customer expresses strong frustration (LLM sentiment detection)
- Customer asks about custom work outside standard packages

```python
async def escalate_to_human(session: ConversationSession, reason: str):
    session.state = ConversationState.HUMAN_HANDOFF
    
    await send_text(session.phone,
        "Let me connect you with one of our designers — they'll take it "
        "from here. Someone will message you within the hour. 🙌"
    )
    
    # Notify the Cre8ive District team (internal WhatsApp group or dashboard)
    await notify_team(
        f"🔔 Human handoff requested\n"
        f"Customer: {session.phone}\n"
        f"Business: {session.business_data.business_name}\n"
        f"Reason: {reason}\n"
        f"Conversation: [link to dashboard]"
    )
```

### Resuming Interrupted Conversations

When a customer returns after going silent:

```python
async def handle_returning_customer(phone: str, message: dict):
    # 1. Check Redis for active session
    session = await redis.get(f"session:{phone}")
    
    if session:
        # Session still active — continue where we left off
        return await process_message(session, message)
    
    # 2. Check PostgreSQL for recent conversation
    last_convo = await db.get_latest_conversation(phone)
    
    if last_convo and last_convo.state != ConversationState.COMPLETE:
        # Restore session to Redis
        session = restore_session(last_convo)
        
        await send_text(phone,
            f"Welcome back! 👋 We were working on the brand for "
            f"*{session.business_data.business_name}*. "
            f"Want to pick up where we left off?"
        )
        return
    
    # 3. Completely new conversation
    return await start_new_session(phone, message)
```

---

## 6. Delivery Flow

### Brand Package Delivery

When the brand is approved and payment confirmed:

```python
async def deliver_brand_package(session: ConversationSession):
    brand = await get_brand(session.brand_job_id)
    
    # 1. Send logo as image (in-chat preview)
    await send_image(
        session.phone,
        brand.primary_logo_url,
        f"Your logo for {session.business_data.business_name} ✨"
    )
    
    # 2. Send color palette card
    await send_image(
        session.phone,
        brand.palette_card_url,
        f"Your brand colors: {brand.color_summary}"
    )
    
    # 3. Send brand guidelines PDF
    pdf_size = await get_file_size(brand.guidelines_pdf_url)
    
    if pdf_size < 16 * 1024 * 1024:  # WhatsApp 16MB limit
        await send_document(
            session.phone,
            brand.guidelines_pdf_url,
            f"{session.business_data.business_name}_Brand_Guidelines.pdf"
        )
    else:
        # Compressed version for WhatsApp + full version via link
        await send_document(
            session.phone,
            brand.guidelines_pdf_compressed_url,
            f"{session.business_data.business_name}_Brand_Guidelines.pdf"
        )
        await send_text(session.phone,
            f"📦 Full resolution files: {brand.download_link}\n"
            f"(Link expires in 30 days)"
        )
    
    # 4. Send download link for complete asset pack
    await send_text(session.phone,
        f"📦 Download your complete brand pack here:\n"
        f"{brand.download_link}\n\n"
        f"Includes: logo (SVG, PNG in all sizes), color specs, "
        f"font files, and your guidelines PDF.\n\n"
        f"This link is yours forever — save it somewhere safe. 🔒"
    )
    
    # 5. If website was generated
    if session.site_job_id:
        site = await get_site(session.site_job_id)
        await send_text(session.phone,
            f"🌐 Your website is live!\n"
            f"👉 {site.url}\n\n"
            f"Share this link anywhere — it works on all devices.\n"
            f"Need changes? Just message me here."
        )
```

### Follow-Up Sequence

Scheduled via the platform's task queue:

```python
FOLLOW_UP_SEQUENCE = [
    {
        "delay_days": 3,
        "template": "brand_followup_day3",
        "params": ["{{business_name}}"],
    },
    {
        "delay_days": 7,
        "message": (
            "Quick check-in on {business_name} — has anyone noticed the "
            "new brand? 👀\n\nIf you need tweaks to anything — logo, "
            "website, colors — just send me a message. First round of "
            "changes is on us."
        ),
    },
    {
        "delay_days": 30,
        "template": "brand_upsell_month1",
        "params": ["{{business_name}}"],
        "condition": "plan != 'complete'",  # only upsell if not on top plan
    },
]
```

---

## 7. Web Fallback

For customers who find Cre8ive District via the website:

### Web Chat Widget

A lightweight chat widget embedded on the Cre8ive District website that
runs the exact same conversation flow:

```html
<!-- Embedded on every page of cre8ivedistrict.com -->
<script src="/assets/chat-widget.js" defer></script>
```

The widget opens a WebSocket connection to the same orchestrator service.
The conversation state machine is transport-agnostic — it doesn't know
whether the customer is on WhatsApp or web chat.

### Click-to-WhatsApp

Every CTA on the website includes a WhatsApp option:

```html
<a href="https://wa.me/2349XXXXXXXXX?text=Hi%2C%20I%20want%20to%20build%20a%20brand"
   class="button">
  Build your brand on WhatsApp →
</a>
```

The pre-filled text ("Hi, I want to build a brand") triggers the GREETING
state immediately.

---

## 8. File Structure

```
platform/
  services/
    whatsapp/
      __init__.py
      client.py          — WhatsApp Cloud API HTTP client
      webhook.py         — inbound webhook handler + signature verification
      sender.py          — send text/image/document/interactive messages
      templates.py       — template message definitions + parameter injection
      media.py           — upload/download media (images, voice notes, PDFs)
    conversation/
      __init__.py
      orchestrator.py    — main message handler: load session → LLM → extract → respond → save
      states.py          — ConversationState enum + transition rules
      flow.py            — state machine: which state handles which input
      intake.py          — BusinessIntake model + extraction prompt
      review.py          — brand review conversation logic (approve/change/start-over)
      delivery.py        — asset delivery flow
      handoff.py         — human escalation logic
      followup.py        — scheduled follow-up messages
    session/
      __init__.py
      manager.py         — Redis read/write + PostgreSQL fallback
      models.py          — ConversationSession dataclass
  routers/
    whatsapp.py          — POST /webhooks/whatsapp + GET (verification)
    chat.py              — WebSocket endpoint for web chat fallback
```

---

## 9. Deliverables Checklist

- [ ] WhatsApp Cloud API integration (send + receive all message types)
- [ ] Webhook endpoint with signature verification
- [ ] Conversation state machine (all 11 states)
- [ ] AI orchestrator with brand consultant persona
- [ ] Structured data extraction from unstructured conversation
- [ ] Voice note transcription (Whisper)
- [ ] Interactive message support (buttons + lists)
- [ ] Session management (Redis hot + PostgreSQL persistent)
- [ ] Session resume for returning customers
- [ ] Brand concept delivery (images + PDF + download link)
- [ ] Website URL delivery
- [ ] Paystack payment link integration
- [ ] Human handoff flow
- [ ] Follow-up message scheduling
- [ ] 3 approved template messages submitted to Meta
- [ ] Web chat fallback widget
- [ ] Click-to-WhatsApp links on website
- [ ] Timeout handling for all states
- [ ] Pidgin English support verified
- [ ] End-to-end test: first message → brand delivered

---

## 10. Estimated Timeline

| Week | Tasks |
|------|-------|
| **1** | WhatsApp Cloud API setup (Meta Business verification started, webhook endpoint, send/receive text + images). Session management (Redis + PostgreSQL). Basic conversation loop. |
| **2** | State machine implementation (all 11 states). AI orchestrator with intake extraction. Interactive messages (buttons + lists). Voice note transcription. |
| **3** | Integration with Brand Generation Service (trigger generation, receive results, send concepts). Review flow (approve / change / start-over). Payment link integration. |
| **4** | Delivery flow (send assets via WhatsApp). Follow-up scheduling. Human handoff. Web chat fallback widget. Template message submission + approval. |
| **5** | End-to-end testing. Pidgin English testing. Edge case handling (timeouts, voice notes, returning customers). Performance optimization. |

**Total: 5 weeks** (with Meta Business verification running in parallel
from day 1 — it's the long-lead item).

---

## 11. WhatsApp API Costs

### Conversation Pricing (Cloud API, Nigeria)

| Type | Cost per 24h conversation |
|------|--------------------------|
| **Service** (customer-initiated) | Free |
| **Marketing** (business-initiated, templates) | ~$0.049 / ₦75 |
| **Utility** (transactional templates) | ~$0.008 / ₦12 |

### Monthly Cost Projections

| Scale | Conversations | Follow-ups (template) | Est. Monthly Cost |
|-------|-------------|----------------------|-------------------|
| **Launch** (50 customers/mo) | 50 service (free) | 100 templates | ~₦7,500 |
| **Growth** (200 customers/mo) | 200 service (free) | 400 templates | ~₦30,000 |
| **Scale** (1,000 customers/mo) | 1,000 service (free) | 2,000 templates | ~₦150,000 |

The key insight: **customer-initiated conversations are free.** Since
customers message us first (they want a brand), 90%+ of our conversations
cost nothing. We only pay for follow-up templates sent outside the 24-hour
window.

### Voice Note Transcription (Whisper)

~$0.006 per minute of audio. At 20% of customers sending voice notes,
averaging 30 seconds each: negligible (<₦500/month at 200 customers).

### Total WhatsApp Channel Cost Per Customer

At launch scale: **~₦150 per customer** (essentially free). The AI
compute costs for the conversation (LLM calls) dwarf the WhatsApp costs
— those are accounted for in the Brand Generation plan.
