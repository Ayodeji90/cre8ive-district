from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.logging import get_logger
from app.models import Brand, Business, Website

log = get_logger(__name__)


class WebsiteGenerationError(Exception):
    pass


class WebsiteJobSuperseded(WebsiteGenerationError):
    pass


async def queue_website_generation(db: AsyncSession, business_id: uuid.UUID) -> dict[str, Any]:
    business = await db.scalar(
        select(Business).where(Business.id == business_id).with_for_update()
    )
    if business is None:
        raise WebsiteGenerationError(f"Business not found: {business_id}")
    result = await db.execute(
        select(Website).where(Website.business_id == business_id).order_by(Website.created_at.desc())
    )
    website = result.scalars().first()
    if website and website.status == "deployed":
        return {"business_id": str(business_id), "status": "deployed"}
    if website and website.status in {"generating", "deployed"}:
        if website.status == "deployed":
            return {"business_id": str(business_id), "status": "deployed"}
        return {"business_id": str(business_id), "status": website.status}
    if website is None:
        website = Website(
            business_id=business_id,
            status="queued",
            pages=[],
            job_token=str(uuid.uuid4()),
            attempt_count=0,
        )
        db.add(website)
    elif website.status != "queued":
        website.status = "queued"
        website.deployment_url = None
        website.custom_domain = None
        website.vercel_id = None
        website.pages = []
        website.job_token = str(uuid.uuid4())
        website.attempt_count = 0
        website.last_error = None
    elif not website.job_token:
        website.job_token = str(uuid.uuid4())
    await db.commit()
    from app.services.jobs import enqueue_website_job
    enqueued = await enqueue_website_job(website.id, website.job_token or str(uuid.uuid4()))
    if not enqueued:
        website.last_error = "Queue unavailable; this saved job will be retried automatically."
        await db.commit()
    return {
        "business_id": str(business_id),
        "status": "queued",
        "queue_pending": not enqueued,
    }


async def reconcile_website_jobs(
    *, stale_after_seconds: int = 900, queued_after_seconds: int = 45, limit: int = 100
) -> dict[str, int]:
    """Re-enqueue saved jobs and recover jobs abandoned by a dead worker."""
    from sqlalchemy import and_, or_

    from app.db import async_session_factory
    from app.services.jobs import enqueue_website_job

    now = datetime.now(timezone.utc)
    stale_before = now.timestamp() - stale_after_seconds
    queued_before = now.timestamp() - queued_after_seconds
    async with async_session_factory() as db:
        stmt = (
            select(Website)
            .where(
                or_(
                    and_(Website.status == "queued", Website.updated_at <= datetime.fromtimestamp(queued_before, timezone.utc)),
                    and_(
                        Website.status == "generating",
                        Website.updated_at <= datetime.fromtimestamp(stale_before, timezone.utc),
                        or_(
                            Website.last_attempt_at.is_(None),
                            Website.last_attempt_at <= datetime.fromtimestamp(stale_before, timezone.utc),
                        ),
                    ),
                )
            )
            .order_by(Website.updated_at.asc())
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        websites = list((await db.execute(stmt)).scalars().all())
        jobs: list[tuple[uuid.UUID, str]] = []
        for website in websites:
            if website.status == "generating":
                website.status = "queued"
                website.job_token = str(uuid.uuid4())
                website.attempt_count = 0
                website.last_error = "Worker stopped before reporting a result; job was recovered."
            elif not website.job_token:
                website.job_token = str(uuid.uuid4())
            website.updated_at = now
            jobs.append((website.id, website.job_token or str(uuid.uuid4())))
        if jobs:
            await db.commit()
        else:
            await db.rollback()

    enqueued_count = 0
    for website_id, job_token in jobs:
        if await enqueue_website_job(website_id, job_token):
            enqueued_count += 1
        else:
            async with async_session_factory() as db:
                website = await db.get(Website, website_id)
                if website and website.job_token == job_token:
                    website.last_error = "Queue unavailable; automatic recovery will retry."
                    await db.commit()
    return {"found": len(jobs), "enqueued": enqueued_count}


async def generate_and_deploy_for_business(
    db: AsyncSession,
    business_id: uuid.UUID,
    *,
    website_id: uuid.UUID | None = None,
    expected_job_token: str | None = None,
) -> dict[str, Any]:
    """Orchestrate website generation and deployment via website-agent microservice,

    and persist the resulting Website record in the database.
    """
    settings = get_settings()
    business = await db.get(Business, business_id)
    if not business:
        raise WebsiteGenerationError(f"Business not found: {business_id}")

    # Load associated brand if available
    brand_res = await db.execute(
        select(Brand).where(Brand.business_id == business_id).order_by(Brand.created_at.desc())
    )
    brand = brand_res.scalars().first()

    colors = brand.colors if brand and brand.colors else {}
    fonts = brand.fonts if brand and brand.fonts else {}
    strategy = brand.strategy if brand and brand.strategy else {}
    copy = brand.copy if brand and brand.copy else {}

    payload = {
        "brand": {
            "name": business.name,
            "tagline": strategy.get("tagline") or copy.get("tagline") or "",
            "palette": {
                "primary": colors.get("primary", "#F36B35"),
                "secondary": colors.get("secondary", "#2D2D2D"),
                "accent": colors.get("accent", "#F4B942"),
            },
            "typography": {
                "heading_font": fonts.get("heading", "Plus Jakarta Sans"),
                "body_font": fonts.get("body", "Inter"),
            },
        },
        "business": {
            "business_id": str(business.id),
            "name": business.name,
            "description": business.description or business.name,
            "industry": business.industry or "",
            "location": business.location or "",
            "whatsapp_number": business.contact_phone or "",
            "email": business.contact_email or "",
            "services": business.preferences.get("services", []) if business.preferences else [],
        },
        "subdomain": business.slug,
    }

    headers: dict[str, str] = {}
    if settings.WEBSITE_AGENT_API_KEY:
        headers["X-Agent-Key"] = settings.WEBSITE_AGENT_API_KEY

    try:
        async with httpx.AsyncClient(timeout=240.0) as client:
            resp = await client.post(
                f"{settings.WEBSITE_AGENT_URL}/v1/websites/generate-and-deploy",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
            deployment = data.get("deployment") or {}
            live_url = deployment.get("live_url")
            if not live_url:
                raise WebsiteGenerationError("Website agent returned no deployed URL.")
            actual_domain = urlparse(live_url).hostname
            if not actual_domain:
                raise WebsiteGenerationError("Website agent returned an invalid deployment URL.")
            site_id = data["site_id"]
            pages = data.get("pages", [])
            deployment_id = deployment.get("deployment_id")
    except WebsiteGenerationError:
        raise
    except Exception as exc:
        log.warning("website_agent_call_failed", exc_info=True)
        raise WebsiteGenerationError(f"Website generation service failed: {exc}") from exc

    # Persist or update Website record in DB
    site_query = select(Website).where(Website.business_id == business_id)
    if website_id is not None:
        site_query = site_query.where(Website.id == website_id)
    site_query = site_query.order_by(Website.created_at.desc())
    existing_site_res = await db.execute(site_query)
    website = existing_site_res.scalars().first()
    if expected_job_token is not None and (
        website is None or website.job_token != expected_job_token
    ):
        raise WebsiteJobSuperseded("This website job was replaced by a newer retry.")
    if website is None:
        website = Website(
            business_id=business_id,
            brand_id=brand.id if brand else None,
            deployment_url=live_url,
            custom_domain=actual_domain,
            vercel_id=deployment_id,
            pages=[{"slug": p} for p in pages],
            status="deployed",
        )
        db.add(website)
    else:
        website.deployment_url = live_url
        website.custom_domain = actual_domain
        website.vercel_id = deployment_id
        website.pages = [{"slug": p} for p in pages]
        website.status = "deployed"

    await db.commit()
    await db.refresh(website)

    return {
        "site_id": site_id,
        "business_id": str(business.id),
        "status": "deployed",
        "live_url": live_url,
        "pages": pages,
    }
