"""Platform adapter for brand assets rendered by the Branding Agent."""

import uuid
from typing import Any
from urllib.parse import urlparse

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.logging import get_logger
from app.models import Brand, Business
from app.services.storage import Storage

log = get_logger(__name__)


class AssetRenderError(RuntimeError):
    pass


async def _render_request(payload: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    if not settings.BRANDING_AGENT_API_KEY:
        raise AssetRenderError("Branding Agent credentials are not configured")

    try:
        async with httpx.AsyncClient(
            base_url=settings.BRANDING_AGENT_URL.rstrip("/"),
            headers={"X-Agent-Key": settings.BRANDING_AGENT_API_KEY},
            timeout=httpx.Timeout(300.0, connect=10.0),
        ) as client:
            response = await client.post("/v1/brand/render-assets", json=payload)
            response.raise_for_status()
            return response.json()
    except (httpx.HTTPError, ValueError) as exc:
        log.error("branding_agent_asset_render_failed", exc_info=True)
        raise AssetRenderError("Branding Agent could not render brand assets") from exc


async def render_brand_assets(db: AsyncSession, brand: Brand, storage: Storage) -> dict[str, Any]:
    business = await db.get(Business, brand.business_id)
    if business is None:
        raise AssetRenderError("Business not found for brand")

    rendered = await _render_request(
        {
            "brand_id": str(brand.id),
            "business_id": str(brand.business_id),
            "business_name": business.name,
            "version": brand.version,
            "strategy": brand.strategy or {},
            "logo_urls": brand.logo_urls or [],
            "colors": brand.colors or {},
            "fonts": brand.fonts or {},
            "copy": brand.copy or {},
        }
    )
    brand.logo_urls = rendered["logo_urls"]
    brand.guidelines_pdf = rendered["guidelines_pdf"]
    brand.kit_zip_url = rendered["kit_zip_url"]
    if brand.status == "generating":
        brand.status = "draft"
    await db.commit()
    await db.refresh(brand)

    kit_key = asset_key_from_url(
        brand.kit_zip_url,
        get_settings().R2_PUBLIC_URL,
    )
    if kit_key is None:
        raise AssetRenderError("Rendered brand kit is not in object storage")

    return {
        "brand_id": brand.id,
        "status": brand.status,
        "logo_urls": brand.logo_urls,
        "guidelines_pdf": brand.guidelines_pdf,
        "kit_zip_url": brand.kit_zip_url,
        "download_url": await storage.presigned_url(kit_key),
    }


def asset_key_from_url(url: str | None, public_base: str) -> str | None:
    if not url:
        return None
    base = public_base.rstrip("/")
    if base and url.startswith(base + "/"):
        return url[len(base) + 1 :]
    if "://" in url:
        path = urlparse(url).path.lstrip("/")
        return path or None
    return url.lstrip("/")


async def brand_for_render(db: AsyncSession, brand_id: uuid.UUID) -> Brand:
    brand = await db.get(Brand, brand_id)
    if brand is None:
        raise AssetRenderError("Brand not found")
    return brand
