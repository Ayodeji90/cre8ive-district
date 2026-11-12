import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BrandGenerateRequest(BaseModel):
    business_id: uuid.UUID


class BrandResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    business_id: uuid.UUID
    version: int
    strategy: dict[str, Any]
    logo_urls: list[dict[str, Any]]
    colors: dict[str, Any]
    fonts: dict[str, Any]
    copy: dict[str, Any]
    guidelines_pdf: str | None
    kit_zip_url: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class BrandAssetFiles(BaseModel):
    brand_id: uuid.UUID
    version: int
    logo_urls: list[dict[str, Any]]
    guidelines_pdf: str | None
    kit_zip_url: str | None
    palette: dict[str, Any]


class WebsiteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    business_id: uuid.UUID
    brand_id: uuid.UUID | None
    deployment_url: str | None
    custom_domain: str | None
    vercel_id: str | None
    pages: list[dict[str, Any]]
    lighthouse: dict[str, Any] | None
    status: str
    created_at: datetime
    updated_at: datetime


class RenderResponse(BaseModel):
    brand_id: uuid.UUID
    status: str
    logo_urls: list[dict[str, Any]]
    guidelines_pdf: str | None
    kit_zip_url: str | None
    download_url: str | None = None


class DownloadResponse(BaseModel):
    url: str
    expires_in: int = Field(description="Seconds until the signed URL expires")
