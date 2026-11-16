from __future__ import annotations

import enum
from datetime import datetime, timezone
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ThemeType(str, enum.Enum):
    CLEAN = "clean"
    BOLD = "bold"
    WARM = "warm"
    CLASSIC = "classic"
    VIBRANT = "vibrant"


class BrandPalette(BaseModel):
    primary: str = "#1A1A1A"
    secondary: str = "#8B6914"
    accent: str = "#FF6B35"
    neutral_900: str = "#111111"
    neutral_700: str = "#444444"
    neutral_100: str = "#F8F8F5"
    bg: str = "#FFFFFF"
    surface: str = "#FAFAF7"


class TypographyPair(BaseModel):
    heading_font: str = "Plus Jakarta Sans"
    body_font: str = "Inter"


class BrandInput(BaseModel):
    brand_id: UUID = Field(default_factory=uuid4)
    name: str
    tagline: str = ""
    logo_svg: str | None = None
    palette: BrandPalette = Field(default_factory=BrandPalette)
    typography: TypographyPair = Field(default_factory=TypographyPair)


class BusinessInput(BaseModel):
    business_id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    industry: str = ""
    services: list[str] = Field(default_factory=list)
    location: str = "Lagos, Nigeria"
    whatsapp_number: str = "2348000000000"
    email: str = ""
    social_links: dict[str, str] = Field(default_factory=dict)


class SectionSpec(BaseModel):
    component: str  # e.g. "hero_centered", "services_grid", "contact_whatsapp"
    variant: str | None = None
    props: dict = Field(default_factory=dict)


class PageSpec(BaseModel):
    slug: str  # "index", "about", "services", "contact"
    title: str
    meta_description: str
    sections: list[SectionSpec] = Field(default_factory=list)


class SiteSpec(BaseModel):
    site_id: UUID = Field(default_factory=uuid4)
    business_id: UUID
    theme: ThemeType = ThemeType.WARM
    brand: BrandInput
    business: BusinessInput
    pages: list[PageSpec] = Field(default_factory=list)
    custom_domain: str | None = None
    subdomain: str = ""
    created_at: datetime = Field(default_factory=utc_now)


class QualityIssue(BaseModel):
    severity: str  # "error", "warning"
    check: str
    message: str


class QualityReport(BaseModel):
    passed: bool
    score: int  # 0 - 100 estimated lighthouse
    issues: list[QualityIssue] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=utc_now)


class DeploymentResult(BaseModel):
    site_id: UUID
    project_id: str
    deployment_id: str
    live_url: str
    subdomain: str
    files_count: int
    deployed_at: datetime = Field(default_factory=utc_now)
    ready_state: str = "READY"


class GenerateWebsiteRequest(BaseModel):
    business: BusinessInput
    brand: BrandInput
    theme: ThemeType | None = None
    subdomain: str | None = None


class GenerateWebsiteResponse(BaseModel):
    site_id: UUID
    spec: SiteSpec
    pages: list[str]  # list of slugs
    quality: QualityReport
    preview_url: str | None = None
    deployment: DeploymentResult | None = None
