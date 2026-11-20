import asyncio
import io
import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import httpx
from jinja2 import Environment, FileSystemLoader, select_autoescape

from branding_agent.logging import get_logger
from branding_agent.storage import Storage, StorageError, storage_path

log = get_logger(__name__)

LOGO_SIZES = (1024, 512, 256, 128, 64)
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)


class AssetRenderError(RuntimeError):
    pass


async def _download(url: str) -> bytes:
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content
    except httpx.HTTPError as exc:
        raise AssetRenderError(f"Could not download source logo: {url}") from exc


def _to_png_bytes(source: bytes, size: int = 1024) -> bytes:
    from PIL import Image

    if b"<svg" in source[:2048].lower() or source.lstrip()[:5] == b"<?xml":
        try:
            import cairosvg
        except ImportError as exc:
            raise AssetRenderError("cairosvg is required to rasterise SVG logos") from exc
        png = cairosvg.svg2png(bytestring=source, output_width=size, output_height=size)
        if png is None:
            raise AssetRenderError("cairosvg could not rasterise the logo")
        return png

    image = Image.open(io.BytesIO(source)).convert("RGBA")
    image = image.resize((size, size), Image.Resampling.LANCZOS)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def render_image_variants(png_bytes: bytes) -> dict[str, bytes]:
    from PIL import Image

    base = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    variants: dict[str, bytes] = {}
    for size in LOGO_SIZES:
        buffer = io.BytesIO()
        base.resize((size, size), Image.Resampling.LANCZOS).save(buffer, format="PNG")
        variants[f"logo-{size}.png"] = buffer.getvalue()

    favicon = io.BytesIO()
    base.resize((64, 64), Image.Resampling.LANCZOS).save(
        favicon, format="ICO", sizes=[(64, 64), (32, 32), (16, 16)]
    )
    variants["favicon.ico"] = favicon.getvalue()

    side = min(base.size)
    left = (base.width - side) // 2
    top = (base.height - side) // 2
    avatar = io.BytesIO()
    base.crop((left, top, left + side, top + side)).resize(
        (400, 400), Image.Resampling.LANCZOS
    ).save(avatar, format="PNG")
    variants["avatar-400.png"] = avatar.getvalue()
    return variants


def _namespace(value: Any) -> Any:
    if isinstance(value, dict):
        return SimpleNamespace(**{key: _namespace(item) for key, item in value.items()})
    if isinstance(value, list):
        return [_namespace(item) for item in value]
    return value


def render_guidelines_pdf(business_name: str, brand_data: dict[str, Any]) -> bytes:
    try:
        from weasyprint import HTML
    except ImportError as exc:
        raise AssetRenderError("WeasyPrint is not installed") from exc

    template = _env.get_template("brand_guidelines.html")
    business = SimpleNamespace(name=business_name)
    brand = _namespace(brand_data)
    pdf = HTML(
        string=template.render(
            business=business,
            brand=brand,
            generated_at=datetime.now(UTC).strftime("%d %B %Y"),
        )
    ).write_pdf()
    if pdf is None:
        raise AssetRenderError("WeasyPrint returned no PDF")
    return pdf


def build_zip(files: dict[str, bytes], fonts_text: str) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in files.items():
            archive.writestr(name, data)
        archive.writestr("fonts.txt", fonts_text)
    return buffer.getvalue()


def fonts_manifest(fonts: dict[str, Any]) -> str:
    lines = ["Cre8ive District — Brand typography", ""]
    for role in ("heading", "body"):
        spec = fonts.get(role) or {}
        if spec:
            lines.append(f"{role.title()}: {spec.get('family')} {spec.get('weight', 400)}")
    lines.extend(["", "All families are available on Google Fonts."])
    return "\n".join(lines)


async def render_brand_assets(request: dict[str, Any], storage: Storage) -> dict[str, Any]:
    source_url = next(
        (
            entry.get("url") if isinstance(entry, dict) else str(entry)
            for entry in request["logo_urls"]
            if (entry.get("url") if isinstance(entry, dict) else entry)
        ),
        None,
    )
    if not source_url:
        raise AssetRenderError("Brand has no logo to render")

    brand_id = str(request["brand_id"])
    version = int(request["version"])
    base_key = storage_path(str(request["business_id"]), "brand", f"v{version}")
    source = await _download(source_url)
    brand_data = {
        "version": version,
        "strategy": request.get("strategy") or {},
        "colors": request.get("colors") or {},
        "fonts": request.get("fonts") or {},
        "copy": request.get("copy") or {},
    }

    try:
        png_bytes = await asyncio.to_thread(_to_png_bytes, source, 1024)
        variants = await asyncio.to_thread(render_image_variants, png_bytes)
        pdf_bytes = await asyncio.to_thread(
            render_guidelines_pdf, request["business_name"], brand_data
        )
    except AssetRenderError:
        raise
    except Exception as exc:
        log.exception("asset_render_failed", brand_id=brand_id)
        raise AssetRenderError("Failed to render brand assets") from exc

    logo_entries: list[dict[str, Any]] = []
    zip_files: dict[str, bytes] = {}
    try:
        for name, data in variants.items():
            content_type = "image/x-icon" if name.endswith(".ico") else "image/png"
            url = await storage.upload_bytes(storage_path(base_key, name), data, content_type)
            zip_files[name] = data
            logo_entries.append({"url": url, "size": name, "format": name.rsplit(".", 1)[-1]})

        palette_bytes = json.dumps(brand_data["colors"], indent=2).encode()
        await storage.upload_bytes(
            storage_path(base_key, "palette.json"), palette_bytes, "application/json"
        )
        zip_files["palette.json"] = palette_bytes

        guidelines_url = await storage.upload_bytes(
            storage_path(base_key, "guidelines.pdf"), pdf_bytes, "application/pdf"
        )
        zip_files["guidelines.pdf"] = pdf_bytes
        kit_bytes = await asyncio.to_thread(
            build_zip, zip_files, fonts_manifest(brand_data["fonts"])
        )
        kit_url = await storage.upload_bytes(
            storage_path(base_key, "kit.zip"), kit_bytes, "application/zip"
        )
    except StorageError as exc:
        raise AssetRenderError(str(exc)) from exc

    log.info("brand_assets_rendered", brand_id=brand_id, version=version)
    return {
        "brand_id": brand_id,
        "logo_urls": logo_entries,
        "guidelines_pdf": guidelines_url,
        "kit_zip_url": kit_url,
    }
