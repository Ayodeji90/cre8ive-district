import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_role
from app.config import Settings
from app.db import get_db
from app.deps import get_app_settings, get_storage
from app.models import Order, User
from app.schemas.delivery import DeliveryRequest, DeliveryResponse
from app.services import delivery as delivery_service
from app.services.storage import Storage

router = APIRouter(prefix="/delivery", tags=["delivery"])


@router.post("/{order_id}/send", response_model=DeliveryResponse)
async def send_delivery(
    order_id: uuid.UUID,
    payload: DeliveryRequest | None = None,
    db: AsyncSession = Depends(get_db),
    storage: Storage = Depends(get_storage),
    settings: Settings = Depends(get_app_settings),
    user: User = Depends(require_role("admin", "designer")),
) -> DeliveryResponse:
    try:
        result = await delivery_service.send_delivery(
            db,
            order_id,
            storage=storage,
            settings=settings,
            email_override=payload.email if payload else None,
        )
    except delivery_service.DeliveryError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return DeliveryResponse(**result)


@router.get("/{order_id}/status", response_model=dict)
async def delivery_status(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "designer")),
) -> dict:
    order = await db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return {
        "order_id": str(order.id),
        "status": order.status,
        "deliverables": order.deliverables,
        "fulfilled_at": order.fulfilled_at,
    }
