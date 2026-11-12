import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_role
from app.config import Settings
from app.db import get_db
from app.deps import get_app_settings, get_storage
from app.models import User
from app.schemas.brand import BrandAssetFiles, DownloadResponse, RenderResponse
from app.services.assets import (
    AssetRenderError,
    asset_key_from_url,
    brand_for_render,
    render_brand_assets,
)
from app.services.storage import Storage

router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("/{brand_id}/render", response_model=RenderResponse)
async def render_assets(
    brand_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    storage: Storage = Depends(get_storage),
    user: User = Depends(require_role("admin", "designer")),
) -> RenderResponse:
    try:
        brand = await brand_for_render(db, brand_id)
        result = await render_brand_assets(db, brand, storage)
    except AssetRenderError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return RenderResponse(**result)


@router.get("/{brand_id}/files", response_model=BrandAssetFiles)
async def list_assets(
    brand_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "designer")),
) -> BrandAssetFiles:
    try:
        brand = await brand_for_render(db, brand_id)
    except AssetRenderError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return BrandAssetFiles(
        brand_id=brand.id,
        version=brand.version,
        logo_urls=brand.logo_urls,
        guidelines_pdf=brand.guidelines_pdf,
        kit_zip_url=brand.kit_zip_url,
        palette=brand.colors,
    )


@router.get("/{brand_id}/download", response_model=DownloadResponse)
async def download_assets(
    brand_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    storage: Storage = Depends(get_storage),
    settings: Settings = Depends(get_app_settings),
    user: User = Depends(require_role("admin", "designer")),
) -> DownloadResponse:
    try:
        brand = await brand_for_render(db, brand_id)
    except AssetRenderError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if not brand.kit_zip_url:
        raise HTTPException(status_code=409, detail="Brand kit has not been rendered yet")

    key = asset_key_from_url(brand.kit_zip_url, settings.R2_PUBLIC_URL)
    if key is None:
        raise HTTPException(status_code=409, detail="Brand kit is not in object storage")
    expires_in = 7 * 24 * 3600
    return DownloadResponse(
        url=await storage.presigned_url(key, expires_in=expires_in), expires_in=expires_in
    )
