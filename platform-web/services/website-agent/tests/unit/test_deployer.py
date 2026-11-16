import pytest
from website_agent.domain.spec import BrandInput, BusinessInput
from website_agent.application.generator import ContentGenerator
from website_agent.providers.vercel import MockVercelDeployer
from website_agent.rendering.assembler import LayoutAssembler


@pytest.mark.asyncio
async def test_mock_vercel_deployer():
    generator = ContentGenerator(stub_mode=True)
    assembler = LayoutAssembler()
    deployer = MockVercelDeployer(domain_suffix="cre8ive.ng")

    brand = BrandInput(name="Eko Logistics", tagline="Fast Delivery")
    business = BusinessInput(
        name="Eko Logistics",
        description="Courier and freight delivery services across Lagos state.",
        whatsapp_number="2348123456789",
    )

    spec = await generator.generate_site_spec(brand, business)
    files = assembler.assemble(spec)

    result = await deployer.deploy(spec, files)
    assert result.site_id == spec.site_id
    assert result.ready_state == "READY"
    assert "eko-logistics.cre8ive.ng" in result.live_url
    assert result.files_count == len(files)
