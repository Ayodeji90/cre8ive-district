import io

import pytest
from PIL import Image

from branding_agent.rendering import assets


class FakeStorage:
    def __init__(self) -> None:
        self.files: dict[str, bytes] = {}

    async def upload_bytes(self, path: str, data: bytes, content_type: str) -> str:
        self.files[path] = data
        return f"https://assets.test/{path}"


def test_image_variants_have_expected_dimensions():
    source = io.BytesIO()
    Image.new("RGB", (1024, 1024), (243, 107, 53)).save(source, format="PNG")

    variants = assets.render_image_variants(source.getvalue())

    for size in (1024, 512, 256, 128, 64):
        assert Image.open(io.BytesIO(variants[f"logo-{size}.png"])).size == (size, size)
    assert variants["favicon.ico"][:4] == b"\x00\x00\x01\x00"
    assert Image.open(io.BytesIO(variants["avatar-400.png"])).size == (400, 400)


@pytest.mark.asyncio
async def test_render_brand_assets_uploads_versioned_kit(monkeypatch):
    source = io.BytesIO()
    Image.new("RGB", (1024, 1024), (243, 107, 53)).save(source, format="PNG")
    storage = FakeStorage()

    async def fake_download(url: str) -> bytes:
        assert url == "https://logos.test/logo.png"
        return source.getvalue()

    monkeypatch.setattr(assets, "_download", fake_download)
    monkeypatch.setattr(assets, "render_guidelines_pdf", lambda name, data: b"%PDF-test")

    result = await assets.render_brand_assets(
        {
            "brand_id": "brand-id",
            "business_id": "business-id",
            "business_name": "Render Co",
            "version": 2,
            "strategy": {"tagline": "Made for what's next"},
            "logo_urls": [{"url": "https://logos.test/logo.png"}],
            "colors": {"palette": {"primary": "#123456"}},
            "fonts": {"heading": {"family": "Inter", "weight": 700}},
            "copy": {},
        },
        storage,
    )

    prefix = "business-id/brand/v2/"
    assert result["brand_id"] == "brand-id"
    assert result["kit_zip_url"] == f"https://assets.test/{prefix}kit.zip"
    assert storage.files[f"{prefix}guidelines.pdf"] == b"%PDF-test"
    assert f"{prefix}logo-1024.png" in storage.files
    assert f"{prefix}palette.json" in storage.files
