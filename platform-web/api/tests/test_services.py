import uuid
from decimal import Decimal

from app.config import Settings
from app.deps import get_app_settings, get_storage
from app.main import app
from app.models import Brand, Business, Order
from app.services.assets import render_brand_assets
from tests.conftest import auth_headers


async def test_render_brand_assets_builds_kit(session_factory, storage, monkeypatch):
    async with session_factory() as db:
        business = Business(name="Render Co", slug="render-co", industry="Fashion", plan="starter")
        db.add(business)
        await db.commit()
        await db.refresh(business)
        brand = Brand(
            business_id=business.id,
            strategy={
                "tagline": "Made for what's next",
                "positioning": "A modern Lagos label",
                "brand_story": "Built for the city.",
                "voice_attributes": ["warm", "bold"],
            },
            colors={
                "palette": {
                    "primary": "#F36B35",
                    "secondary": "#2D2D2D",
                    "accent": "#F4B942",
                    "neutral": "#2D2D2D",
                    "background": "#F5F5EE",
                }
            },
            fonts={
                "heading": {"family": "Plus Jakarta Sans", "weight": 800},
                "body": {"family": "Plus Jakarta Sans", "weight": 400},
            },
            logo_urls=[{"url": "https://logos.test/logo.png"}],
            status="draft",
        )
        db.add(brand)
        await db.commit()
        await db.refresh(brand)

        async def fake_render(payload):
            assert payload["business_name"] == "Render Co"
            assert payload["version"] == 1
            return {
                "brand_id": str(brand.id),
                "logo_urls": [{"url": "https://assets.test/logo-1024.png"}],
                "guidelines_pdf": "https://assets.test/guidelines.pdf",
                "kit_zip_url": "https://assets.test/brand/kit.zip",
            }

        async def fake_presigned_url(path, expires_in=604800):
            assert path == "brand/kit.zip"
            return "https://signed.test/brand/kit.zip"

        monkeypatch.setattr("app.services.assets._render_request", fake_render)
        monkeypatch.setattr(storage, "presigned_url", fake_presigned_url)
        result = await render_brand_assets(db, brand, storage)

    assert result["kit_zip_url"] == "https://assets.test/brand/kit.zip"
    assert result["download_url"] == "https://signed.test/brand/kit.zip"
    assert result["logo_urls"] == [{"url": "https://assets.test/logo-1024.png"}]


async def test_delivery_marks_order_fulfilled(client, admin, storage, session_factory, monkeypatch):
    settings = Settings(
        R2_PUBLIC_URL="https://assets.test",
        RESEND_API_KEY="re_test",
        ENV="test",
    )
    app.dependency_overrides[get_storage] = lambda: storage
    app.dependency_overrides[get_app_settings] = lambda: settings

    async def fake_email(**kwargs) -> str:
        assert kwargs["download_url"] == "https://signed.test/brand/kit.zip?expires=604800"
        assert kwargs["to"] == "founder@lagosthreads.test"
        return "email_123"

    monkeypatch.setattr("app.services.delivery.send_brand_ready_email", fake_email)

    async with session_factory() as db:
        business = Business(
            name="Lagos Threads",
            slug="lagos-threads-delivery",
            contact_email="founder@lagosthreads.test",
            plan="starter",
            status="active",
        )
        db.add(business)
        await db.commit()
        await db.refresh(business)
        order = Order(
            business_id=business.id,
            plan="brand_starter",
            amount=Decimal("20000.00"),
            status="paid",
        )
        brand = Brand(
            business_id=business.id,
            strategy={"tagline": "Wear your story"},
            kit_zip_url="https://assets.test/brand/kit.zip",
            status="approved",
        )
        db.add_all([order, brand])
        await db.commit()
        await db.refresh(order)
        order_id = order.id

    try:
        response = await client.post(f"/api/delivery/{order_id}/send", headers=auth_headers(admin))
    finally:
        app.dependency_overrides.pop(get_storage, None)
        app.dependency_overrides.pop(get_app_settings, None)

    assert response.status_code == 200, response.text
    assert response.json()["email_id"] == "email_123"
    assert response.json()["status"] == "fulfilled"

    async with session_factory() as db:
        refreshed = await db.get(Order, uuid.UUID(str(order_id)))
        assert refreshed.fulfilled_at is not None
        assert refreshed.deliverables["email_id"] == "email_123"
