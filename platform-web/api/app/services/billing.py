"""Paystack billing: order creation, initialization, webhooks, verification."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.logging import get_logger
from app.models import Business, Order
from app.schemas.billing import BillingInitializeRequest
from app.services.paystack import PLAN_AMOUNTS, PaystackClient, PaystackError
from app.services.storage import Storage

log = get_logger(__name__)

PAID_STATUSES = {"paid", "fulfilled"}


class BillingError(RuntimeError):
    pass


def callback_url(settings: Settings) -> str:
    origin = settings.cors_origins[0] if settings.cors_origins else "http://localhost:3000"
    return f"{origin}/account?payment=success"


async def initialize_payment(
    db: AsyncSession,
    paystack: PaystackClient,
    settings: Settings,
    payload: BillingInitializeRequest,
) -> tuple[Order, dict]:
    if payload.plan not in PLAN_AMOUNTS:
        raise BillingError(f"Unknown plan: {payload.plan}")

    business = await db.get(Business, payload.business_id)
    if business is None:
        raise BillingError("Business not found")

    amount = PLAN_AMOUNTS[payload.plan]
    order = Order(
        business_id=business.id,
        plan=payload.plan,
        amount=amount,
        currency="NGN",
        status="pending",
        deliverables={},
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    try:
        data = await paystack.initialize_transaction(
            email=payload.email,
            amount_naira=amount,
            reference=str(order.id),
            callback_url=callback_url(settings),
            metadata={
                "order_id": str(order.id),
                "plan": order.plan,
                "business_id": str(business.id),
            },
        )
    except PaystackError:
        order.status = "failed"
        await db.commit()
        raise

    order.paystack_ref = data.get("reference") or str(order.id)
    await db.commit()
    await db.refresh(order)
    return order, data


async def apply_charge_success(
    db: AsyncSession, reference: str, *, storage: Storage | None = None
) -> Order | None:
    """Idempotently mark an order paid and kick off generation."""
    order_id = _as_uuid(reference)
    order = await db.get(Order, order_id) if order_id else None
    if order is None:
        order = (
            await db.execute(select(Order).where(Order.paystack_ref == reference))
        ).scalar_one_or_none()

    if order is None:
        log.warning("charge_for_unknown_order", reference=reference)
        return None

    if order.status in PAID_STATUSES:
        return order

    order.status = "paid"
    order.paystack_ref = order.paystack_ref or reference
    order.paid_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(order)
    log.info("order_paid", order_id=str(order.id), plan=order.plan)

    await refresh_business_plan(db, order.business_id)

    from app.services.paystack import PLAN_CREDITS
    credits_to_grant = PLAN_CREDITS.get(order.plan, 0)
    if credits_to_grant > 0:
        from app.services import credits as credits_service
        try:
            await credits_service.add_credits(
                db,
                order.business_id,
                credits_to_grant,
                transaction_type="topup" if order.plan.startswith("credits_") else "plan_grant",
                description=f"Payment for {order.plan}: +{credits_to_grant} credits",
                reference_id=str(order.id),
            )
        except Exception:
            log.warning("credit_grant_failed_for_order", order_id=str(order.id), exc_info=True)

    try:
        from app.services.jobs import enqueue_brand_generation

        await enqueue_brand_generation(order.business_id)
    except Exception:  # pragma: no cover - enqueue already logs
        log.warning("post_payment_generation_enqueue_failed", order_id=str(order.id))
    return order


async def refresh_business_plan(db: AsyncSession, business_id: uuid.UUID) -> None:
    business = await db.get(Business, business_id)
    if business is None:
        return
    business.plan = "starter" if business.plan == "free" else business.plan
    if business.status == "onboarding":
        business.status = "active"
    await db.commit()


async def verify_payment(
    db: AsyncSession, paystack: PaystackClient, reference: str
) -> tuple[str, Order | None]:
    try:
        data = await paystack.verify_transaction(reference)
    except PaystackError:
        raise

    paystack_status = data.get("status", "failed")
    order: Order | None = None
    if paystack_status == "success":
        verified_reference = data.get("reference") or reference
        if verified_reference != reference:
            raise PaystackError("Paystack returned a mismatched payment reference")
        order = await apply_charge_success(db, verified_reference)
    else:
        candidate = (
            await db.execute(select(Order).where(Order.paystack_ref == reference))
        ).scalar_one_or_none()
        order = candidate
    return paystack_status, order


def _as_uuid(value: str) -> uuid.UUID | None:
    try:
        return uuid.UUID(value)
    except (ValueError, TypeError):
        return None
