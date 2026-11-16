import pytest
from website_agent.application.generator import ContentGenerator
from website_agent.domain.spec import (
    BrandInput,
    BusinessInput,
    ThemeType,
)
from website_agent.rendering.assembler import LayoutAssembler


@pytest.mark.asyncio
async def test_layout_assembler_renders_full_file_tree():
    generator = ContentGenerator(stub_mode=True)
    assembler = LayoutAssembler()

    brand = BrandInput(name="AfroCraft", tagline="Authentic African Crafts")
    business = BusinessInput(
        name="AfroCraft",
        description="Handcrafted woven baskets and homeware made in Nigeria.",
        industry="Retail",
        whatsapp_number="2348012345678",
    )

    spec = await generator.generate_site_spec(brand, business, theme=ThemeType.WARM)
    files = assembler.assemble(spec)

    # Core pages
    assert "index.html" in files
    assert "about.html" in files
    assert "services.html" in files
    assert "contact.html" in files

    # Metadata & SEO files
    assert "robots.txt" in files
    assert "sitemap.xml" in files
    assert "assets/site.css" in files

    # Inspect index.html contents
    index_html = files["index.html"]
    assert "<!DOCTYPE html>" in index_html
    assert "AfroCraft" in index_html
    assert "wa.me/2348012345678" in index_html
    assert "--brand-primary:" in index_html
