"""arq background worker.

Run with: `arq app.worker.WorkerSettings`
"""

import uuid

import redis.asyncio as aioredis
from arq.connections import RedisSettings
from sqlalchemy import select

from app.config import get_settings
from app.db import async_session_factory
from app.events import EventBus
from app.llm.factory import get_ai_service
from app.logging import configure_logging, get_logger
from app.models import Brand, Review
from app.services.assets import render_brand_assets
from app.services.brand_gen import generate_brand
from app.services.delivery import DeliveryError, send_delivery
from app.services.jobs import enqueue_asset_render
from app.services.storage import build_storage

log = get_logger(__name__)


async def startup(ctx: dict) -> None:
    settings = get_settings()
    configure_logging(settings.ENV)
    ctx["settings"] = settings
    ctx["storage"] = build_storage(settings)
    ctx["ai"] = get_ai_service(settings)
    redis = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    ctx["redis"] = redis
    ctx["event_bus"] = EventBus(redis)


async def shutdown(ctx: dict) -> None:
    redis = ctx.get("redis")
    if redis is not None:
        await redis.aclose()


async def generate_brand_job(ctx: dict, business_id: str) -> str:
    async with async_session_factory() as db:
        brand = await generate_brand(
            db, ctx["ai"], uuid.UUID(business_id), event_bus=ctx["event_bus"]
        )
    await enqueue_asset_render(brand.id)
    return str(brand.id)


async def render_assets_job(ctx: dict, brand_id: str) -> str:
    async with async_session_factory() as db:
        brand = await db.get(Brand, uuid.UUID(brand_id))
        if brand is None:
            raise ValueError(f"Brand {brand_id} not found")
        await render_brand_assets(db, brand, ctx["storage"])

        review = (
            await db.execute(
                select(Review)
                .where(Review.brand_id == brand.id, Review.status == "approved")
                .order_by(Review.created_at.desc())
            )
        ).scalars().first()
        order_id = review.order_id if review else None

    if order_id is not None:
        async with async_session_factory() as db:
            try:
                await send_delivery(
                    db, order_id, storage=ctx["storage"], settings=ctx["settings"]
                )
            except DeliveryError:
                log.warning(
                    "auto_delivery_failed", order_id=str(order_id), exc_info=True
                )
    return brand_id


async def send_delivery_job(ctx: dict, order_id: str) -> str:
    async with async_session_factory() as db:
        result = await send_delivery(
            db, uuid.UUID(order_id), storage=ctx["storage"], settings=ctx["settings"]
        )
    return result["status"]


class WorkerSettings:
    functions = [generate_brand_job, render_assets_job, send_delivery_job]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(get_settings().REDIS_URL)
    max_tries = 3
    job_timeout = 600
