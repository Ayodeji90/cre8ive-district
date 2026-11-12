"""Shared FastAPI dependencies.

Tests override these functions to inject fakes for Redis, storage, AI and
Paystack without touching business logic.
"""

from collections.abc import AsyncIterator

import redis.asyncio as aioredis
from fastapi import HTTPException, status

from app.config import Settings, get_settings
from app.events import EventBus
from app.llm.base import AIService
from app.logging import get_logger
from app.services.paystack import PaystackClient
from app.services.storage import Storage, StorageNotConfigured, build_storage

log = get_logger(__name__)

_redis: aioredis.Redis | None = None
_event_bus: EventBus | None = None


def get_app_settings() -> Settings:
    return get_settings()


async def get_redis() -> AsyncIterator[aioredis.Redis | None]:
    global _redis
    if _redis is None:
        try:
            client = aioredis.from_url(
                get_settings().REDIS_URL, encoding="utf-8", decode_responses=True
            )
            await client.ping()
            _redis = client
        except Exception:
            log.warning("redis_unavailable", exc_info=True)
            yield None
            return
    yield _redis


def get_event_bus() -> EventBus:
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus(_redis)
    return _event_bus


def get_storage() -> Storage:
    try:
        return build_storage(get_settings())
    except StorageNotConfigured as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Object storage is not configured",
        ) from exc


def get_paystack() -> PaystackClient:
    settings = get_settings()
    if not settings.PAYSTACK_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Paystack is not configured",
        )
    return PaystackClient(settings.PAYSTACK_SECRET_KEY, base_url=settings.PAYSTACK_BASE_URL)


def get_ai() -> AIService:
    from app.llm.factory import AIServiceNotConfigured, get_ai_service

    try:
        return get_ai_service(get_settings())
    except AIServiceNotConfigured as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI services are not configured",
        ) from exc
