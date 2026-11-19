import pytest

from website_agent.application.generator import (
    ContentGenerator,
    select_theme_for_industry,
    slugify,
)
from website_agent.domain.spec import (
    BrandInput,
    BusinessInput,
    ThemeType,
)


def test_slugify():
    assert slugify("Adé Beads & Crafts") == "ade-beads-crafts"
    assert slugify("Lagos Tech Studio!") == "lagos-tech-studio"


def test_theme_selection_by_industry():
    assert select_theme_for_industry("Software & AI Platform") == ThemeType.CLEAN
    assert select_theme_for_industry("Fashion and Streetwear") == ThemeType.BOLD
    assert select_theme_for_industry("Artisan Bakery & Cafe") == ThemeType.WARM
    assert select_theme_for_industry("Luxury Real Estate & Hotels") == ThemeType.CLASSIC


@pytest.mark.asyncio
async def test_content_generator_creates_complete_site_spec():
    generator = ContentGenerator(stub_mode=True)
    brand = BrandInput(name="Yaba Design Studio", tagline="Smart Design for Growing Brands")
    business = BusinessInput(
        name="Yaba Design Studio",
        description="Branding, digital strategy, and website design agency.",
        industry="Design & Technology",
        services=["Brand Strategy", "Website Design", "Packaging"],
        whatsapp_number="2348099887766",
    )

    spec = await generator.generate_site_spec(brand, business)

    assert spec.brand.name == "Yaba Design Studio"
    assert spec.subdomain == "yaba-design-studio"
    assert len(spec.pages) == 4

    slugs = [p.slug for p in spec.pages]
    assert "index" in slugs
    assert "about" in slugs
    assert "services" in slugs
    assert "contact" in slugs
