import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.config import Settings
from app.db import get_db
from app.deps import get_app_settings, get_paystack
from app.logging import get_logger
from app.models import Order, User
from app.schemas.billing import (
    BillingInitializeRequest,
    BillingInitializeResponse,
    BillingVerifyResponse,
)
from app.schemas.order import OrderResponse
from app.services import billing as billing_service
from app.services.paystack import PaystackClient, PaystackError, verify_webhook_signature

log = get_logger(__name__)
router = APIRouter(prefix="/billing", tags=["billing"])
webhook_router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/initialize", response_model=BillingInitializeResponse)
async def initialize(
    payload: BillingInitializeRequest,
    db: AsyncSession = Depends(get_db),
    paystack: PaystackClient = Depends(get_paystack),
    settings: Settings = Depends(get_app_settings),
    user: User = Depends(get_current_user),
) -> BillingInitializeResponse:
    try:
        order, data = await billing_service.initialize_payment(db, paystack, settings, payload)
    except billing_service.BillingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PaystackError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return BillingInitializeResponse(
        authorization_url=data["authorization_url"],
        access_code=data["access_code"],
        reference=order.paystack_ref or str(order.id),
        amount=float(order.amount),
        currency=order.currency,
    )


@router.post("/verify/{reference}", response_model=BillingVerifyResponse)
async def verify(
    reference: str,
    db: AsyncSession = Depends(get_db),
    paystack: PaystackClient = Depends(get_paystack),
    user: User = Depends(get_current_user),
) -> BillingVerifyResponse:
    try:
        paystack_status, order = await billing_service.verify_payment(db, paystack, reference)
    except PaystackError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return BillingVerifyResponse(
        reference=reference,
        status=paystack_status,
        order_id=order.id if order else None,
    )


@router.get("/{business_id}/history", response_model=list[OrderResponse])
async def history(
    business_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Order]:
    result = await db.execute(
        select(Order).where(Order.business_id == business_id).order_by(Order.created_at.desc())
    )
    return list(result.scalars().all())


@webhook_router.post("/paystack", status_code=status.HTTP_200_OK)
async def paystack_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
) -> dict:
    body = await request.body()
    signature = request.headers.get("x-paystack-signature")
    if not verify_webhook_signature(body, signature, settings.PAYSTACK_SECRET_KEY):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        event = json.loads(body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid payload") from exc

    event_type = event.get("event")
    data = event.get("data") or {}
    reference = str(data.get("reference") or "")

    try:
        if event_type == "charge.success":
            await billing_service.apply_charge_success(db, reference)
        elif event_type == "refund.processed":
            await _apply_refund(db, reference)
        elif event_type == "transfer.success":
            log.info("transfer_success", reference=reference)
        else:
            log.info("unhandled_paystack_event", event_type=event_type)
    except ValidationError as exc:  # pragma: no cover - defensive
        log.error("paystack_event_invalid", event_type=event_type, exc_info=True)
        raise HTTPException(status_code=422, detail="Invalid event payload") from exc

    return {"status": "ok"}


async def _apply_refund(db: AsyncSession, reference: str) -> None:
    order = (
        await db.execute(select(Order).where(Order.paystack_ref == reference))
    ).scalar_one_or_none()
    if order is None:
        try:
            order = await db.get(Order, uuid.UUID(reference))
        except ValueError:
            order = None
    if order is not None and order.status != "refunded":
        order.status = "refunded"
        await db.commit()
