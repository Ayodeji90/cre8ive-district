from website_agent.domain.spec import (
    BrandInput,
    BusinessInput,
)
from website_agent.application.generator import ContentGenerator
from website_agent.quality.checker import WebsiteQualityChecker
from website_agent.rendering.assembler import LayoutAssembler
import pytest


@pytest.mark.asyncio
async def test_quality_checker_passes_valid_site():
    generator = ContentGenerator(stub_mode=True)
    assembler = LayoutAssembler()
    checker = WebsiteQualityChecker()

    brand = BrandInput(name="Naija Soles", tagline="Premium Footwear")
    business = BusinessInput(
        name="Naija Soles",
        description="Custom handcrafted shoes tailored in Lagos.",
        industry="Fashion",
        whatsapp_number="2348000001122",
    )

    spec = await generator.generate_site_spec(brand, business)
    files = assembler.assemble(spec)

    report = checker.check(files)
    assert report.passed is True
    assert report.score >= 90
    assert not any(i.severity == "error" for i in report.issues)


def test_quality_checker_flags_missing_index():
    checker = WebsiteQualityChecker()
    report = checker.check({"about.html": "<html><body>About</body></html>"})
    assert report.passed is False
    assert any(i.check == "entrypoint" for i in report.issues)
