# Paystack Billing — Implementation Plan

*Standalone implementation plan for the billing and payment system powering
Cre8ive District's AI brand platform. Naira-denominated, Paystack-powered,
designed for how Nigerian businesses actually pay.*

---

## 1. What This Delivers

A billing system that:

- Accepts payment in **Nigerian Naira** via Paystack (bank transfer, card, USSD)
- Supports **one-time brand packages** and **monthly subscriptions**
- Sends **payment links via WhatsApp** (the primary payment trigger)
- Handles plan upgrades, downgrades, and cancellations
- Tracks what each customer has paid for and what they've received
- Provides a **revenue dashboard** for the Cre8ive District team
- Manages **referral credits and promo codes**

---

## 2. Pricing Structure

### One-Time Packages

| Package | Price | What's Included |
|---------|-------|-----------------|
| **Brand Starter** | ₦20,000 | Logo + color palette + typography pairing + brand guidelines PDF |
| **Brand + Web** | ₦60,000 | Everything in Starter + 3–5 page responsive website hosted on Vercel |
| **Brand Complete** | ₦120,000 | Everything in Brand + Web + social media kit (avatar, cover images, 5 post templates) + Google Business Profile setup + human designer review pass |

### Monthly Plans (Phase 2+)

| Plan | Price | What's Included |
|------|-------|-----------------|
| **Starter** | ₦5,000/mo | Hosted website + 2 design change requests/month |
| **Growth** | ₦15,000/mo | Starter + 8 social media posts/month + basic SEO monitoring |
| **Pro** | ₦30,000/mo | Growth + priority human designer access + Google Ads setup assistance |

### Price Justification

| Benchmark | Price Range | Comparison |
|-----------|-------------|------------|
| Cre8ive District manual packages (current) | ₦600,000–₦1,500,000 | Our AI packages are **10–30× cheaper** |
| Freelance designer in Lagos (logo + brand) | ₦50,000–₦200,000 | We match or beat while delivering a larger package |
| Bumpa / Catlog (commerce SaaS) | ₦5,000–₦25,000/mo | Similar range for our subscription tier; different product |
| AI compute cost per brand (see §10) | ~₦6,500 | **67–95% gross margin** across all packages |

---

## 3. Paystack Integration

### API Essentials

**Base URL:** `https://api.paystack.co`
**Auth:** `Authorization: Bearer sk_live_xxxxx` (secret key in env, never client-side)

### Initialize a Transaction (One-Time Package)

```http
POST /transaction/initialize
Content-Type: application/json
Authorization: Bearer sk_live_xxxxx

{
  "email": "customer@example.com",
  "amount": 6000000,
  "currency": "NGN",
  "reference": "cre8-ord-a1b2c3d4",
  "callback_url": "https://platform.cre8ive.ng/payments/callback",
  "metadata": {
    "order_id": "ord_a1b2c3d4",
    "business_id": "biz_x9y8z7",
    "package": "brand_web",
    "custom_fields": [
      { "display_name": "Business Name", "variable_name": "business_name", "value": "Ayo's Kitchen" }
    ]
  }
}
```

**Response:**
```json
{
  "status": true,
  "message": "Authorization URL created",
  "data": {
    "authorization_url": "https://checkout.paystack.com/abc123def456",
    "access_code": "abc123def456",
    "reference": "cre8-ord-a1b2c3d4"
  }
}
```

The `authorization_url` is what gets sent to the customer via WhatsApp.

### Create a Subscription Plan

```http
POST /plan
{
  "name": "Growth Monthly",
  "interval": "monthly",
  "amount": 1500000,
  "currency": "NGN",
  "description": "Hosted website + 8 social posts/month + SEO monitoring"
}
```

### Verify a Transaction

```http
GET /transaction/verify/cre8-ord-a1b2c3d4
```

Response includes `data.status` (`success`, `abandoned`, `failed`), `data.channel`
(`card`, `bank`, `ussd`, `bank_transfer`), and `data.paid_at`.

### Webhook Events

Register a webhook URL at `https://platform.cre8ive.ng/api/webhooks/paystack`.
Key events:

| Event | When | Action |
|-------|------|--------|
| `charge.success` | Payment confirmed | Unlock deliverables, mark order paid, trigger delivery |
| `subscription.create` | Subscription activated | Provision monthly features |
| `subscription.not_renew` | Auto-renew failed | Pause features, send WhatsApp reminder |
| `subscription.disable` | Subscription cancelled | Downgrade to free/archive |
| `refund.processed` | Refund completed | Update order status |
| `transfer.success` | Payout to team member (if applicable) | Log |

**Webhook signature verification:**
```python
import hmac, hashlib

def verify_paystack_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(), payload, hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

Always verify `X-Paystack-Signature` before processing. Return `200` immediately,
then process asynchronously.

### Generate a Payment Link

```http
POST /page
{
  "name": "Brand Starter — Ayo's Kitchen",
  "amount": 2000000,
  "description": "AI-generated brand identity package",
  "redirect_url": "https://platform.cre8ive.ng/payments/success",
  "metadata": { "order_id": "ord_a1b2c3d4" }
}
```

Returns a `slug` → customer URL: `https://paystack.com/pay/{slug}`.
Alternatively, use the `/transaction/initialize` authorization_url directly — it's
simpler and auto-expires.

---

## 4. Payment Flow

```
Customer approves brand concept (WhatsApp)
    ↓
System creates Order (status: pending_payment)
    ↓
System calls POST /transaction/initialize
    ↓
Paystack returns authorization_url
    ↓
WhatsApp sends payment link message:
  "Your brand package is ready! 🎨
   Package: Brand + Web — ₦60,000
   Pay here: https://checkout.paystack.com/abc123
   (Bank transfer, card, or USSD accepted)"
    ↓
Customer clicks link → Paystack checkout page
    ↓
Customer pays via bank transfer / card / USSD
    ↓
Paystack sends charge.success webhook
    ↓
System verifies webhook signature
    ↓
System updates Order (status: paid, channel, paid_at)
    ↓
Delivery pipeline triggered:
  → brand assets packaged (ZIP + individual files)
  → website deployed to Vercel
  → WhatsApp delivers final brand kit + website URL
    ↓
Order status → delivered
```

---

## 5. Bank Transfer Handling

Bank transfer is the dominant payment method in Nigeria. Paystack handles this
via **Dedicated Virtual Account Numbers (DVA)**.

**How it works:**

1. Customer selects "Pay with Bank Transfer" on Paystack checkout
2. Paystack generates a **one-time virtual account number** (any Nigerian bank)
3. Customer transfers from their bank app to that account number
4. Paystack confirms the transfer and fires `charge.success`

**Timing:** Most confirmations arrive within **1–5 minutes**. Occasionally up to
30 minutes for inter-bank transfers during peak hours.

**While waiting:**
```
WhatsApp message:
  "We've received your order! Waiting for payment confirmation
   from your bank. This usually takes a few minutes.
   We'll send your brand package as soon as it clears. ✓"
```

**Expiry:** Paystack virtual accounts expire after a set window (configurable,
default ~30 minutes). If expired without payment, send a gentle reminder via
WhatsApp with a fresh payment link.

**Edge case — "I've paid":**
If the customer messages "I've paid" before the webhook arrives:
1. Call `GET /transaction/verify/{reference}` to check status
2. If `success` → proceed with delivery
3. If still `pending` → reply: "Your bank is still processing. We'll notify you
   the moment it clears — usually under 5 minutes."
4. Never trust the customer's word alone — always verify via API

---

## 6. Data Model

```python
class Order(Base):
    __tablename__ = "orders"

    id: Mapped[UUID]                     # PK
    business_id: Mapped[UUID]            # FK → businesses
    package: Mapped[str]                 # brand_starter | brand_web | brand_complete
    amount: Mapped[int]                  # amount in kobo (₦60,000 = 6000000)
    currency: Mapped[str]                # NGN
    status: Mapped[str]                  # pending_payment | paid | delivering | delivered | refunded | expired
    paystack_reference: Mapped[str]      # our unique reference
    paystack_access_code: Mapped[str]    # Paystack checkout code
    paystack_authorization_url: Mapped[str]
    payment_channel: Mapped[str | None]  # card | bank | bank_transfer | ussd
    paid_at: Mapped[datetime | None]
    delivered_at: Mapped[datetime | None]
    deliverables: Mapped[dict]           # JSON: {"logo": true, "website_url": "...", "guidelines_pdf": "..."}
    promo_code: Mapped[str | None]
    referral_source: Mapped[UUID | None] # FK → businesses (referrer)
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[UUID]
    business_id: Mapped[UUID]            # FK → businesses
    plan: Mapped[str]                    # starter | growth | pro
    amount: Mapped[int]                  # kobo
    interval: Mapped[str]               # monthly
    status: Mapped[str]                  # active | paused | cancelled | past_due
    paystack_subscription_code: Mapped[str]
    paystack_customer_code: Mapped[str]
    paystack_plan_code: Mapped[str]
    paystack_email_token: Mapped[str]    # for managing subscription
    current_period_start: Mapped[datetime]
    current_period_end: Mapped[datetime]
    cancel_at_period_end: Mapped[bool]
    created_at: Mapped[datetime]


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[UUID]
    order_id: Mapped[UUID | None]        # FK → orders (NULL for subscription renewals)
    subscription_id: Mapped[UUID | None] # FK → subscriptions
    amount: Mapped[int]                  # kobo
    channel: Mapped[str]                 # card | bank | bank_transfer | ussd
    status: Mapped[str]                  # success | failed | abandoned | refunded
    paystack_reference: Mapped[str]
    paystack_transaction_id: Mapped[int]
    ip_address: Mapped[str | None]
    fees: Mapped[int]                    # Paystack fees in kobo
    metadata: Mapped[dict]
    created_at: Mapped[datetime]


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id: Mapped[UUID]
    code: Mapped[str]                    # UNIQUE, uppercase
    discount_type: Mapped[str]           # percent | fixed
    discount_value: Mapped[int]          # percent (0–100) or kobo
    max_uses: Mapped[int | None]
    uses: Mapped[int]
    valid_from: Mapped[datetime]
    valid_until: Mapped[datetime | None]
    applicable_packages: Mapped[list]    # JSON: ["brand_starter", "brand_web"] or [] for all
    active: Mapped[bool]
```

---

## 7. WhatsApp Payment Flow

### Sending a Payment Link

After the customer approves a brand concept:

```python
async def send_payment_link(session: ConversationSession, order: Order):
    message = (
        f"Your brand package is ready!\n\n"
        f"📦 *{order.package_display_name}*\n"
        f"💰 ₦{order.amount_naira:,.0f}\n\n"
        f"Pay here: {order.paystack_authorization_url}\n\n"
        f"Bank transfer, card, or USSD — whichever you prefer.\n"
        f"We'll start building the moment it clears."
    )
    await whatsapp.send_text(session.phone, message)
    order.payment_link_sent_at = utcnow()
```

### Abandoned Payment Reminders

| Trigger | Delay | Message |
|---------|-------|---------|
| Link sent, no payment | 2 hours | "Still thinking? Your brand package is waiting — pay when you're ready: {link}" |
| Still no payment | 24 hours | "Just checking in — your brand concept is saved. Here's the link if you'd like to proceed: {link}" |
| Still no payment | 72 hours | "Your payment link has expired. Message us anytime to pick up where you left off." |

After 72 hours, expire the order and archive. If the customer returns, create a
fresh order with a new payment link.

### Payment Confirmation Receipt

On `charge.success` webhook:
```
WhatsApp message:
  "Payment confirmed! ✓
   ₦60,000 received for Brand + Web package.

   We're generating your brand now — you'll have it
   within the hour. Sit tight. 🎨"
```

---

## 8. Pricing Logic

### Package Selection

The AI assistant recommends a package based on the conversation:

```python
def recommend_package(business_info: BusinessInfo) -> str:
    if business_info.needs_website and business_info.needs_social:
        return "brand_complete"
    elif business_info.needs_website:
        return "brand_web"
    else:
        return "brand_starter"
```

The customer always sees all options and chooses. The recommendation is a nudge,
not a gate.

### Promo Codes

Applied during checkout:
```python
def apply_promo(order: Order, code: str) -> Order:
    promo = db.query(PromoCode).filter_by(code=code.upper(), active=True).first()
    if not promo or promo.uses >= (promo.max_uses or float("inf")):
        raise InvalidPromoCode()
    if promo.applicable_packages and order.package not in promo.applicable_packages:
        raise PromoNotApplicable()

    if promo.discount_type == "percent":
        discount = order.amount * promo.discount_value // 100
    else:
        discount = promo.discount_value

    order.amount -= discount
    order.promo_code = promo.code
    promo.uses += 1
    return order
```

### Referral Credits

"Refer a business, both of you get ₦5,000 off."
- Referrer gets a credit stored on their `business.referral_balance` (kobo)
- Referred business gets ₦5,000 discount on first order automatically
- Credit applied at next order or subscription renewal
- Tracked via `order.referral_source`

---

## 9. Financial Dashboard

Accessible to the Cre8ive District team at `/admin/billing`.

### Key Views

**Revenue overview:**
- Daily / weekly / monthly revenue (chart)
- Revenue by package type (pie chart)
- Revenue by payment channel (card vs bank transfer vs USSD)

**Conversion funnel:**
```
Conversations started → Brand generated → Payment link sent →
Payment completed → Delivered
```
Each step shows count and drop-off rate.

**Per-customer view:**
- Order history, payment status, deliverables
- Subscription status and renewal history
- Lifetime value

**Paystack fee tracking:**
- Gross revenue vs net revenue (after Paystack fees)
- Average fee per transaction
- Monthly fee total

---

## 10. Paystack Fees & Margin Analysis

### Fee Schedule (Paystack Nigeria, current)

| Channel | Fee | Cap |
|---------|-----|-----|
| Local card | 1.5% + ₦100 | Capped at ₦2,000 |
| Bank transfer | Flat ~₦50–₦100 | — |
| USSD | 1.5% + ₦100 | Capped at ₦2,000 |

### Margin Per Package

| Package | Price | AI Cost | Paystack Fee (card) | Net Revenue | Gross Margin |
|---------|-------|---------|---------------------|-------------|-------------|
| Brand Starter | ₦20,000 | ~₦3,500 | ₦400 | ₦16,100 | **80%** |
| Brand + Web | ₦60,000 | ~₦6,500 | ₦1,000 | ₦52,500 | **87%** |
| Brand Complete | ₦120,000 | ~₦10,000 | ₦1,900 | ₦108,100 | **90%** |

AI cost breakdown per brand: ~₦2,000 LLM calls (Claude/GPT-4o-mini for copy +
strategy) + ~₦1,500 image generation (logo, 3–4 generation rounds) +
~₦500 embeddings/storage + ~₦2,500 website generation (LLM + Vercel deploy).
Figures based on current API pricing at ₦1,500/$ and conservative token estimates.

**Bank transfer drops the fee to ₦50–₦100**, adding another ₦900–₦1,900 to margin.
Since most Nigerian customers will pay by transfer, real-world margins will be
higher than the card-based estimates above.

---

## 11. File Structure

```
platform/
  services/
    billing/
      __init__.py
      paystack.py         — Paystack API client (init transaction, verify,
                            create plan, create subscription, refund)
      plans.py            — plan/package definitions, pricing logic
      orders.py           — order CRUD, status transitions, delivery trigger
      subscriptions.py    — subscription lifecycle (create, pause, cancel, renew)
      webhooks.py         — webhook handler + signature verification
      links.py            — payment link generation + WhatsApp message formatting
      promos.py           — promo code validation + application
      referrals.py        — referral tracking + credit ledger
      dashboard.py        — aggregation queries for the admin dashboard
  models/
    order.py
    subscription.py
    payment.py
    promo_code.py
  routers/
    billing.py            — customer-facing endpoints (create order, apply promo)
    webhooks.py           — POST /api/webhooks/paystack
    admin_billing.py      — admin dashboard endpoints
```

---

## 12. Deliverables Checklist

- [ ] Paystack API client with init, verify, plan, subscription, refund methods
- [ ] Webhook receiver with signature verification and async processing
- [ ] Order model + CRUD + status state machine
- [ ] Subscription model + lifecycle management
- [ ] Payment link generation → WhatsApp delivery integration
- [ ] Bank transfer waiting-state handling ("I've paid" flow)
- [ ] Abandoned payment reminder sequence (2h / 24h / 72h)
- [ ] Payment confirmation receipt via WhatsApp
- [ ] Promo code system (create, validate, apply)
- [ ] Referral credit tracking and application
- [ ] Admin revenue dashboard (daily/weekly/monthly, by package, by channel)
- [ ] Conversion funnel analytics
- [ ] Integration tests: full payment flow (init → webhook → delivery trigger)
- [ ] Paystack test mode configuration for development

---

## 13. Estimated Timeline

| Week | Tasks |
|------|-------|
| **Week 1** | Paystack API client, webhook handler + signature verification, Order model + migrations, payment link generation |
| **Week 2** | WhatsApp payment link delivery, bank transfer waiting flow, confirmation receipts, abandoned payment reminders, promo code system, referral tracking, admin dashboard queries, integration tests |

**Total: 2 weeks** to a working billing system.

---

## 14. Security

- **Webhook signature verification** on every incoming Paystack event (HMAC SHA-512)
- **Secret key** stored in environment variable, never in code or client-side
- **Idempotent processing**: deduplicate webhooks by `reference` — process
  `charge.success` only once per order (check `order.status != paid` before
  transitioning)
- **PCI compliance** handled by Paystack — we never see or store card numbers;
  Paystack's checkout page handles all sensitive payment data
- **HTTPS only** on all webhook and callback URLs
- **Rate limiting** on the order creation endpoint to prevent abuse
- **Audit log**: every payment event (success, failure, refund) logged with
  timestamp, reference, amount, and channel for reconciliation
