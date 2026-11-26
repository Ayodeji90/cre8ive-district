"""arq background worker.

Run with: `arq app.worker.WorkerSettings`
"""

import asyncio
import re
import uuid
from datetime import UTC, datetime

import redis.asyncio as aioredis
from arq.connections import RedisSettings
from sqlalchemy import select

from app.config import get_settings
from app.db import async_session_factory
from app.events import EventBus
from app.llm.factory import get_ai_service
from app.logging import configure_logging, get_logger
from app.models import Brand, Review, Website
from app.services.assets import render_brand_assets
from app.services.brand_gen import generate_brand
from app.services.delivery import DeliveryError, send_delivery
from app.services.jobs import enqueue_asset_render
from app.services.storage import build_storage
from app.services.website_gen import (
    WebsiteJobSuperseded,
    generate_and_deploy_for_business,
    reconcile_website_jobs,
)

log = get_logger(__name__)
WEBSITE_MAX_JOB_ATTEMPTS = 3


async def startup(ctx: dict) -> None:
    settings = get_settings()
    configure_logging(settings.ENV)
    ctx["settings"] = settings
    ctx["storage"] = build_storage(settings)
    ctx["ai"] = get_ai_service(settings)
    redis = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    ctx["redis"] = redis
    ctx["event_bus"] = EventBus(redis)
    ctx["website_recovery_task"] = asyncio.create_task(_website_recovery_loop())


async def shutdown(ctx: dict) -> None:
    recovery_task = ctx.get("website_recovery_task")
    if recovery_task is not None:
        recovery_task.cancel()
        await asyncio.gather(recovery_task, return_exceptions=True)
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


async def generate_website_job(ctx: dict, website_id: str, job_token: str) -> str:
    website_uuid = uuid.UUID(website_id)
    async with async_session_factory() as db:
        website = await db.scalar(
            select(Website).where(Website.id == website_uuid).with_for_update()
        )
        if website is None:
            log.error("website_job_row_missing", website_id=website_id)
            return "missing"
        if website.job_token != job_token or website.status == "deployed":
            log.info("website_job_superseded", website_id=website_id)
            return "superseded"
        if website.status != "queued":
            return website.status
        website.status = "generating"
        website.attempt_count += 1
        website.last_attempt_at = datetime.now(UTC)
        website.last_error = None
        await db.commit()
        try:
            business_uuid = website.business_id
            brands = (
                (
                    await db.execute(
                        select(Brand)
                        .where(Brand.business_id == business_uuid)
                        .order_by(Brand.created_at.desc())
                    )
                )
                .scalars()
                .first()
            )
            if brands is None:
                await generate_brand(db, ctx["ai"], business_uuid, event_bus=ctx["event_bus"])
            result = await generate_and_deploy_for_business(
                db,
                business_uuid,
                website_id=website_uuid,
                expected_job_token=job_token,
            )
            return result["status"]
        except WebsiteJobSuperseded:
            return "superseded"
        except Exception:
            error = _website_error_summary(ctx.get("settings"))
            await db.rollback()
            current = await db.scalar(
                select(Website).where(Website.id == website_uuid).with_for_update()
            )
            if current is not None and current.job_token == job_token:
                if current.status == "deployed":
                    return "deployed"
                current.last_error = error
                current.status = (
                    "failed" if current.attempt_count >= WEBSITE_MAX_JOB_ATTEMPTS else "queued"
                )
                await db.commit()
            log.exception(
                "website_generation_failed",
                website_id=website_id,
                attempt_count=current.attempt_count if current else None,
            )
            raise


def _website_error_summary(settings=None) -> str:
    import sys

    exc = sys.exc_info()[1]
    if exc is None:
        return "Website generation failed."
    detail = " ".join(str(exc).split())
    detail = re.sub(r"(?i)(bearer\s+)[^\s,;]+", r"\1[redacted]", detail)
    detail = re.sub(r"(?i)(token=)[^&\s]+", r"\1[redacted]", detail)
    detail = re.sub(r"(?i)(api[_-]?key=)[^&\s]+", r"\1[redacted]", detail)
    for secret in (
        getattr(settings, "OPENROUTER_API_KEY", ""),
        getattr(settings, "VERCEL_TOKEN", ""),
        getattr(settings, "SERVICE_API_KEY", ""),
        getattr(settings, "DATABASE_URL", ""),
    ):
        if secret:
            detail = detail.replace(secret, "[redacted]")
    return f"{type(exc).__name__}: {detail[:700]}" if detail else type(exc).__name__


async def _website_recovery_loop() -> None:
    while True:
        try:
            result = await reconcile_website_jobs()
            if result["found"]:
                log.info("website_jobs_reconciled", **result)
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("website_job_reconciliation_failed")
        await asyncio.sleep(30)


async def render_assets_job(ctx: dict, brand_id: str) -> str:
    async with async_session_factory() as db:
        brand = await db.get(Brand, uuid.UUID(brand_id))
        if brand is None:
            raise ValueError(f"Brand {brand_id} not found")
        await render_brand_assets(db, brand, ctx["storage"])

        review = (
            (
                await db.execute(
                    select(Review)
                    .where(Review.brand_id == brand.id, Review.status == "approved")
                    .order_by(Review.created_at.desc())
                )
            )
            .scalars()
            .first()
        )
        order_id = review.order_id if review else None

    if order_id is not None:
        async with async_session_factory() as db:
            try:
                await send_delivery(db, order_id, storage=ctx["storage"], settings=ctx["settings"])
            except DeliveryError:
                log.warning("auto_delivery_failed", order_id=str(order_id), exc_info=True)
    return brand_id


async def send_delivery_job(ctx: dict, order_id: str) -> str:
    async with async_session_factory() as db:
        result = await send_delivery(
            db, uuid.UUID(order_id), storage=ctx["storage"], settings=ctx["settings"]
        )
    return result["status"]


class WorkerSettings:
    functions = [generate_brand_job, generate_website_job, render_assets_job, send_delivery_job]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(get_settings().REDIS_URL)
    max_tries = WEBSITE_MAX_JOB_ATTEMPTS
    job_timeout = 600
