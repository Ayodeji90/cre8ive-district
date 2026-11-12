"""Brand kit delivery: signed download link + email + order fulfilment."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.logging import get_logger
from app.models import Brand, Business, Order
from app.services.assets import asset_key_from_url
from app.services.email import EmailError, send_brand_ready_email
from app.services.storage import Storage, StorageError

log = get_logger(__name__)


class DeliveryError(RuntimeError):
    pass


async def send_delivery(
    db: AsyncSession,
    order_id: uuid.UUID,
    *,
    storage: Storage,
    settings: Settings,
    email_override: str | None = None,
) -> dict:
    order = await db.get(Order, order_id)
    if order is None:
        raise DeliveryError("Order not found")
    if order.status == "refunded":
        raise DeliveryError("Order was refunded")

    business = await db.get(Business, order.business_id)
    if business is None:
        raise DeliveryError("Business not found")

    brand = (
        await db.execute(
            select(Brand)
            .where(Brand.business_id == business.id, Brand.status == "approved")
            .order_by(Brand.version.desc())
        )
    ).scalars().first()
    if brand is None:
        brand = (
            await db.execute(
                select(Brand)
                .where(Brand.business_id == business.id)
                .order_by(Brand.version.desc())
            )
        ).scalars().first()
    if brand is None or not brand.kit_zip_url:
        raise DeliveryError("Brand kit has not been rendered yet")

    destination = email_override or business.contact_email
    if not destination:
        raise DeliveryError("Business has no contact email")

    key = asset_key_from_url(brand.kit_zip_url, settings.R2_PUBLIC_URL)
    if not key:
        raise DeliveryError("Brand kit is not stored in configured object storage")
    try:
        download_url = await storage.presigned_url(key)
    except StorageError as exc:
        raise DeliveryError("Could not sign the download URL") from exc

    tagline = (brand.strategy or {}).get("tagline", "")
    try:
        email_id = await send_brand_ready_email(
            api_key=settings.RESEND_API_KEY,
            sender=settings.EMAIL_FROM,
            to=destination,
            business_name=business.name,
            tagline=tagline,
            download_url=download_url,
        )
    except EmailError as exc:
        raise DeliveryError(str(exc)) from exc

    order.status = "fulfilled"
    order.fulfilled_at = datetime.now(UTC)
    order.deliverables = {
        **(order.deliverables or {}),
        "brand_id": str(brand.id),
        "zip_url": brand.kit_zip_url,
        "pdf_url": brand.guidelines_pdf,
        "sent_at": datetime.now(UTC).isoformat(),
        "email_id": email_id,
        "sent_to": destination,
    }
    brand.status = "delivered"
    await db.commit()
    await db.refresh(order)

    log.info("delivery_sent", order_id=str(order.id), email_id=email_id)
    return {
        "order_id": order.id,
        "status": order.status,
        "email_id": email_id,
        "download_url": download_url,
    }
