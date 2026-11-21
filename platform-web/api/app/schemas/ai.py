"""Platform-side models for data returned by the Branding Agent."""

from pydantic import BaseModel, Field


class BrandBriefExtract(BaseModel):
    business_name: str | None = None
    description: str | None = None
    industry: str | None = None
    target_audience: str | None = None
    style_keywords: list[str] = Field(default_factory=list)
    mood: str | None = None
    conversation_stage: str = "greeting"
    ready_to_generate: bool = False


class BrandStrategy(BaseModel):
    primary_name: str
    name_alternatives: list[str] = Field(default_factory=list)
    positioning: str
    tagline: str
    voice_attributes: list[str] = Field(default_factory=list)
    brand_story: str
    elevator_pitch: str
    target_description: str
    industry_keywords: list[str] = Field(default_factory=list)


class ColorPalette(BaseModel):
    primary: str
    secondary: str
    accent: str
    neutral: str
    background: str


class PaletteResult(BaseModel):
    palette: ColorPalette
    contrast_scores: dict[str, float] = Field(default_factory=dict)
    passes_wcag_aa: bool = False


class FontSpec(BaseModel):
    family: str
    weight: int = 400


class FontPair(BaseModel):
    heading: FontSpec
    body: FontSpec


class BrandCopy(BaseModel):
    tagline_variants: list[str] = Field(default_factory=list)
    instagram_bio: str = ""
    linkedin_summary: str = ""
    whatsapp_status: str = ""
    elevator_pitch: str = ""
    one_liner: str = ""
    social_hashtags: list[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    passed: bool
    failures: list[str] = Field(default_factory=list)


class LogoAsset(BaseModel):
    url: str
    size: str | None = None
    format: str | None = None
