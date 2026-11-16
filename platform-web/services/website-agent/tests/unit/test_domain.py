from uuid import uuid4
from website_agent.domain.spec import (
    BrandInput,
    BrandPalette,
    BusinessInput,
    PageSpec,
    SectionSpec,
    SiteSpec,
    ThemeType,
    TypographyPair,
)


def test_site_spec_creation():
    brand = BrandInput(
        name="Lekki Coffee Club",
        tagline="Brewed with Soul",
        palette=BrandPalette(primary="#2C1810", accent="#D4A373"),
        typography=TypographyPair(heading_font="Playfair Display", body_font="Inter"),
    )
    business = BusinessInput(
        name="Lekki Coffee Club",
        description="Specialty coffee roasters in Lekki Phase 1, Lagos.",
        industry="Food & Beverage",
        whatsapp_number="2348011223344",
    )
    spec = SiteSpec(
        business_id=business.business_id,
        theme=ThemeType.WARM,
        brand=brand,
        business=business,
        subdomain="lekki-coffee",
    )
    assert spec.theme == ThemeType.WARM
    assert spec.subdomain == "lekki-coffee"
    assert spec.brand.name == "Lekki Coffee Club"
