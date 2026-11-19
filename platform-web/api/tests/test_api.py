import json
import uuid
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.config import get_settings
from app.deps import get_app_settings, get_paystack, get_storage
from app.main import app
from app.models import Brand, Business, Conversation, Order, Review, User
from app.services.paystack import verify_webhook_signature
from tests.conftest import auth_headers


class FakePaystack:
    def __init__(self) -> None:
        self.initialized: list[dict] = []
        self.verified: list[str] = []

    async def initialize_transaction(self, **kwargs) -> dict:
        self.initialized.append(kwargs)
        ref = kwargs["reference"]
        return {
            "authorization_url": f"https://checkout.paystack.com/{ref}",
            "access_code": "access-code",
            "reference": ref,
        }

    async def verify_transaction(self, reference: str) -> dict:
        self.verified.append(reference)
        return {"status": "success", "reference": reference}


@pytest.fixture
def paystack() -> FakePaystack:
    fake = FakePaystack()
    app.dependency_overrides[get_paystack] = lambda: fake
    yield fake
    app.dependency_overrides.pop(get_paystack, None)


async def create_business(client, headers) -> dict:
    response = await client.post(
        "/api/businesses",
        json={
            "name": "Lagos Threads",
            "description": "Contemporary Nigerian fashion for young professionals",
            "industry": "Fashion",
            "contact_email": "hello@lagosthreads.test",
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}
    assert response.headers["X-Request-ID"]


async def test_health_deps_reports_each_dependency(client, monkeypatch):
    from app.routers import health as health_router

    async def ok_database() -> dict:
        return {"status": "ok", "latency_ms": 0.1}

    async def ok_redis() -> dict:
        return {"status": "ok", "latency_ms": 0.1}

    async def ok_http(_client, name, _base_url, _api_key) -> dict:
        return {"status": "ok", "service": name}

    monkeypatch.setattr(health_router, "_check_database", ok_database)
    monkeypatch.setattr(health_router, "_check_redis", ok_redis)
    monkeypatch.setattr(health_router, "_check_http", ok_http)

    response = await client.get("/health/deps")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert set(body["dependencies"]) == {
        "database",
        "redis",
        "branding-agent",
        "website-agent",
        "run-engine",
    }


async def test_health_deps_is_503_when_a_dependency_is_down(client, monkeypatch):
    from app.routers import health as health_router

    async def ok_database() -> dict:
        return {"status": "ok"}

    async def broken_redis() -> dict:
        return {"status": "error", "error": "connection refused"}

    async def ok_http(_client, name, _base_url, _api_key) -> dict:
        return {"status": "ok", "service": name}

    monkeypatch.setattr(health_router, "_check_database", ok_database)
    monkeypatch.setattr(health_router, "_check_redis", broken_redis)
    monkeypatch.setattr(health_router, "_check_http", ok_http)

    response = await client.get("/health/deps")
    assert response.status_code == 503
    assert response.json()["status"] == "degraded"
    assert response.json()["dependencies"]["redis"]["status"] == "error"


async def test_me_requires_token(client):
    response = await client.get("/api/me")
    assert response.status_code == 401


async def test_me_returns_user(client, customer):
    response = await client.get("/api/me", headers=auth_headers(customer))
    assert response.status_code == 200
    assert response.json()["email"] == "customer@example.com"
    assert response.json()["role"] == "customer"


async def test_business_create_and_update(client, customer):
    headers = auth_headers(customer)
    business = await create_business(client, headers)
    assert business["slug"] == "lagos-threads"
    assert business["owner_id"] == str(customer.id)

    patched = await client.patch(
        f"/api/businesses/{business['id']}",
        json={"location": "Lekki, Lagos"},
        headers=headers,
    )
    assert patched.status_code == 200
    assert patched.json()["location"] == "Lekki, Lagos"


async def test_list_businesses_scoped_to_owner(client, customer, admin):
    """A user only sees their own businesses."""
    customer_headers = auth_headers(customer)
    admin_headers = auth_headers(admin)

    biz = await create_business(client, customer_headers)

    # Customer sees their business
    res = await client.get("/api/businesses", headers=customer_headers)
    assert res.status_code == 200
    ids = [b["id"] for b in res.json()]
    assert biz["id"] in ids

    # Admin (different user) sees none of the customer's businesses
    admin_res = await client.get("/api/businesses", headers=admin_headers)
    assert admin_res.status_code == 200
    admin_ids = [b["id"] for b in admin_res.json()]
    assert biz["id"] not in admin_ids


async def test_business_get_requires_ownership(client, customer, admin):
    """Cannot read another user's business."""
    biz = await create_business(client, auth_headers(customer))
    res = await client.get(f"/api/businesses/{biz['id']}", headers=auth_headers(admin))
    assert res.status_code == 403


async def test_business_patch_requires_ownership(client, customer, admin):
    """Cannot update another user's business."""
    biz = await create_business(client, auth_headers(customer))
    res = await client.patch(
        f"/api/businesses/{biz['id']}",
        json={"name": "Stolen Name"},
        headers=auth_headers(admin),
    )
    assert res.status_code == 403


async def test_customer_cannot_change_business_plan_or_status(client, customer):
    headers = auth_headers(customer)
    biz = await create_business(client, headers)
    response = await client.patch(
        f"/api/businesses/{biz['id']}",
        json={"plan": "brand_complete", "status": "active"},
        headers=headers,
    )
    assert response.status_code == 422

    unchanged = await client.get(f"/api/businesses/{biz['id']}", headers=headers)
    assert unchanged.status_code == 200
    assert unchanged.json()["plan"] == "free"
    assert unchanged.json()["status"] == "onboarding"


async def test_business_create_rejects_caller_supplied_owner_and_plan(client, customer):
    response = await client.post(
        "/api/businesses",
        json={"name": "Owner Spoof", "owner_id": str(uuid.uuid4()), "plan": "pro"},
        headers=auth_headers(customer),
    )
    assert response.status_code == 422


async def test_chat_start_with_foreign_business_is_forbidden(client, customer, admin):
    """Cannot start a chat using another user's business_id."""
    biz = await create_business(client, auth_headers(customer))
    res = await client.post(
        "/api/chat/start",
        json={"business_id": biz["id"]},
        headers=auth_headers(admin),
    )
    assert res.status_code == 403


async def test_chat_rejects_conversation_attached_to_foreign_business(
    client, customer, admin, session_factory
):
    foreign_business = await create_business(client, auth_headers(admin))
    started = await client.post("/api/chat/start", json={}, headers=auth_headers(customer))
    assert started.status_code == 200
    conversation_id = uuid.UUID(started.json()["conversation_id"])

    async with session_factory() as db:
        conversation = await db.get(Conversation, conversation_id)
        conversation.business_id = uuid.UUID(foreign_business["id"])
        await db.commit()

    history = await client.get(
        f"/api/chat/{conversation_id}/history", headers=auth_headers(customer)
    )
    assert history.status_code == 403


async def test_billing_forbidden_on_foreign_business(client, customer, admin, paystack):
    """Cannot access billing routes for another user's business."""
    biz = await create_business(client, auth_headers(customer))
    res = await client.get(
        f"/api/billing/{biz['id']}/credits",
        headers=auth_headers(admin),
    )
    assert res.status_code == 403


async def test_payment_verify_checks_order_owner_before_provider_call(
    client, customer, admin, paystack
):
    business = await create_business(client, auth_headers(customer))
    initialized = await client.post(
        "/api/billing/initialize",
        json={
            "plan": "brand_starter",
            "business_id": business["id"],
            "email": "customer@example.com",
        },
        headers=auth_headers(customer),
    )
    assert initialized.status_code == 200

    response = await client.post(
        f"/api/billing/verify/{initialized.json()['reference']}",
        headers=auth_headers(admin),
    )
    assert response.status_code == 403
    assert paystack.verified == []


async def test_chat_start_and_history(client, customer):
    headers = auth_headers(customer)
    response = await client.post("/api/chat/start", json={}, headers=headers)
    assert response.status_code == 200, response.text
    body = response.json()
    conversation_id = body["conversation_id"]
    assert "Abija" in body["greeting_message"]

    history = await client.get(f"/api/chat/{conversation_id}/history", headers=headers)
    assert history.status_code == 200
    assert history.json()["total"] == 1
    assert history.json()["messages"][0]["role"] == "assistant"


async def test_billing_initialize_creates_order(client, customer, paystack):
    headers = auth_headers(customer)
    business = await create_business(client, headers)

    response = await client.post(
        "/api/billing/initialize",
        json={
            "plan": "brand_starter",
            "business_id": business["id"],
            "email": "customer@example.com",
        },
        headers=headers,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["amount"] == 20000.0
    assert body["authorization_url"].startswith("https://checkout.paystack.com/")
    assert paystack.initialized[0]["amount_naira"] == 20000.00

    history = await client.get(f"/api/billing/{business['id']}/history", headers=headers)
    assert history.status_code == 200
    assert len(history.json()) == 1
    assert history.json()[0]["status"] == "pending"


async def test_paystack_webhook_is_signed_and_idempotent(client, customer, session_factory):
    settings = get_settings()
    async with session_factory() as db:
        # Business requires owner_id — use the customer fixture
        business = Business(
            name="Webhook Co",
            slug="webhook-co",
            plan="free",
            status="onboarding",
            owner_id=customer.id,
        )
        db.add(business)
        await db.commit()
        await db.refresh(business)
        order = Order(
            business_id=business.id,
            plan="brand_web",
            amount=Decimal("60000.00"),
            status="pending",
        )
        db.add(order)
        await db.commit()
        await db.refresh(order)
        reference = str(order.id)

    payload = json.dumps({"event": "charge.success", "data": {"reference": reference}}).encode()
    signature = (
        __import__("hmac")
        .new(settings.PAYSTACK_SECRET_KEY.encode(), payload, __import__("hashlib").sha512)
        .hexdigest()
    )
    assert verify_webhook_signature(payload, signature, settings.PAYSTACK_SECRET_KEY)

    app.dependency_overrides[get_app_settings] = lambda: settings
    try:
        for _ in range(2):
            response = await client.post(
                "/api/webhooks/paystack",
                content=payload,
                headers={"x-paystack-signature": signature, "content-type": "application/json"},
            )
            assert response.status_code == 200, response.text
    finally:
        app.dependency_overrides.pop(get_app_settings, None)

    async with session_factory() as db:
        refreshed = await db.get(Order, order.id)
        assert refreshed.status == "paid"
        assert refreshed.paid_at is not None

    bad = await client.post(
        "/api/webhooks/paystack",
        content=payload,
        headers={"x-paystack-signature": "nope", "content-type": "application/json"},
    )
    assert bad.status_code == 401


async def test_brand_generation_requires_paid_order(client, customer, session_factory):
    headers = auth_headers(customer)
    business = await create_business(client, headers)

    blocked = await client.post(
        "/api/brands/generate", json={"business_id": business["id"]}, headers=headers
    )
    assert blocked.status_code == 402

    async with session_factory() as db:
        db.add(
            Order(
                business_id=uuid.UUID(business["id"]),
                plan="brand_starter",
                amount=Decimal("20000.00"),
                status="paid",
            )
        )
        await db.commit()

    created = await client.post(
        "/api/brands/generate", json={"business_id": business["id"]}, headers=headers
    )
    assert created.status_code == 201, created.text
    assert created.json()["status"] == "draft"

    async with session_factory() as db:
        reviews = (await db.execute(select(Review))).scalars().all()
        assert len(reviews) == 1
        assert reviews[0].status == "pending"


async def test_brand_generation_forbidden_on_foreign_business(
    client, customer, admin, session_factory
):
    """Cannot generate a brand for another user's business."""
    headers = auth_headers(customer)
    business = await create_business(client, headers)
    res = await client.post(
        "/api/brands/generate",
        json={"business_id": business["id"]},
        headers=auth_headers(admin),
    )
    assert res.status_code == 403


async def test_review_workflow(client, customer, admin, session_factory):
    headers = auth_headers(customer)
    admin_headers = auth_headers(admin)
    business = await create_business(client, headers)

    async with session_factory() as db:
        brand = Brand(
            business_id=uuid.UUID(business["id"]),
            strategy={"tagline": "Wear your story"},
            logo_urls=[{"url": "https://assets.test/logo.png"}],
            status="draft",
        )
        db.add(brand)
        await db.commit()
        await db.refresh(brand)
        review = Review(brand_id=brand.id, status="pending")
        db.add(review)
        await db.commit()
        await db.refresh(review)
        review_id = review.id

    forbidden = await client.get("/api/admin/reviews", headers=headers)
    assert forbidden.status_code == 403

    listing = await client.get("/api/admin/reviews?status=pending", headers=admin_headers)
    assert listing.status_code == 200
    assert listing.json()["total"] == 1
    assert listing.json()["items"][0]["business_name"] == "Lagos Threads"

    detail = await client.get(f"/api/admin/reviews/{review_id}", headers=admin_headers)
    assert detail.status_code == 200
    assert detail.json()["brand"]["strategy"]["tagline"] == "Wear your story"

    claimed = await client.post(f"/api/admin/reviews/{review_id}/claim", headers=admin_headers)
    assert claimed.status_code == 200
    assert claimed.json()["status"] == "in_progress"
    assert claimed.json()["reviewer_id"] == str(admin.id)

    approved = await client.post(f"/api/admin/reviews/{review_id}/approve", headers=admin_headers)
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    async with session_factory() as db:
        brand_row = await db.get(Brand, uuid.UUID(detail.json()["brand"]["id"]))
        assert brand_row.status == "approved"


async def test_asset_download_uses_signed_url(client, admin, customer, storage, session_factory):
    async with session_factory() as db:
        business = Business(
            name="Assets Co",
            slug="assets-co",
            plan="starter",
            status="active",
            owner_id=customer.id,  # business needs an owner
        )
        db.add(business)
        await db.commit()
        await db.refresh(business)
        brand = Brand(
            business_id=business.id,
            colors={"palette": {"primary": "#F36B35"}},
            kit_zip_url="https://assets.test/brand/kit.zip",
            status="draft",
        )
        db.add(brand)
        await db.commit()
        await db.refresh(brand)
        brand_id = brand.id

    app.dependency_overrides[get_storage] = lambda: storage
    try:
        response = await client.get(f"/api/assets/{brand_id}/download", headers=auth_headers(admin))
    finally:
        app.dependency_overrides.pop(get_storage, None)

    assert response.status_code == 200, response.text
    assert response.json()["url"] == "https://signed.test/brand/kit.zip?expires=604800"
    assert response.json()["expires_in"] == 604800


async def test_customer_can_access_own_assets_but_not_another_business(
    client, customer, admin, storage, session_factory
):
    async with session_factory() as db:
        business = Business(
            name="Customer Assets",
            slug="customer-assets",
            plan="free",
            status="onboarding",
            owner_id=customer.id,
        )
        db.add(business)
        await db.commit()
        await db.refresh(business)
        brand = Brand(
            business_id=business.id,
            colors={"palette": {"primary": "#F36B35"}},
            kit_zip_url="https://assets.test/customer/kit.zip",
            status="draft",
        )
        db.add(brand)
        await db.commit()
        await db.refresh(brand)
        brand_id = brand.id
        other_customer = User(
            id=uuid.uuid4(), email="other-customer@example.com", name="Other", role="customer"
        )
        db.add(other_customer)
        await db.commit()

    app.dependency_overrides[get_storage] = lambda: storage
    try:
        owned = await client.get(f"/api/assets/{brand_id}/download", headers=auth_headers(customer))
        foreign = await client.get(
            f"/api/assets/{brand_id}/files", headers=auth_headers(other_customer)
        )
    finally:
        app.dependency_overrides.pop(get_storage, None)

    assert owned.status_code == 200, owned.text
    assert owned.json()["url"].startswith("https://signed.test/customer/kit.zip")
    assert foreign.status_code == 403
