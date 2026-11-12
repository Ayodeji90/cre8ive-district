"""WCAG contrast validation and brand output quality checks."""

from io import BytesIO

import httpx
from PIL import Image

from branding_agent.domain.ai_models import (
    BrandStrategy,
    ColorPalette,
    FontPair,
    PaletteResult,
    ValidationResult,
)


def _hex_to_linear(hex_color: str) -> tuple[float, float, float]:
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    channels = []
    for c in (r, g, b):
        s = c / 255.0
        channels.append(s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4)
    return channels[0], channels[1], channels[2]


def _relative_luminance(hex_color: str) -> float:
    r, g, b = _hex_to_linear(hex_color)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def check_contrast(fg_hex: str, bg_hex: str) -> float:
    l1 = _relative_luminance(fg_hex)
    l2 = _relative_luminance(bg_hex)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def validate_palette(palette: ColorPalette) -> PaletteResult:
    scores = {
        "primary_on_bg": check_contrast(palette.primary, palette.background),
        "neutral_on_bg": check_contrast(palette.neutral, palette.background),
        "accent_on_bg": check_contrast(palette.accent, palette.background),
        "bg_on_neutral": check_contrast(palette.background, palette.neutral),
    }
    passes = (
        scores["primary_on_bg"] >= 4.5
        and scores["neutral_on_bg"] >= 4.5
        and scores["accent_on_bg"] >= 3.0
    )
    return PaletteResult(
        palette=palette,
        contrast_scores={k: round(v, 2) for k, v in scores.items()},
        passes_wcag_aa=passes,
    )


GENERIC_POSITIONS = {
    "quality service",
    "best in class",
    "your trusted partner",
    "delivering excellence",
    "committed to quality",
    "your reliable partner",
    "providing premium services",
}


async def verify_google_font(family: str) -> bool:
    url = f"https://fonts.googleapis.com/css2?family={family.replace(' ', '+')}"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.head(url)
            return r.status_code == 200
    except httpx.HTTPError:
        return False


async def validate_brand_output(
    strategy: BrandStrategy,
    palette: PaletteResult,
    fonts: FontPair,
    logo_urls: list[str],
) -> ValidationResult:
    failures: list[str] = []

    if len(strategy.tagline.split()) > 10:
        failures.append(f"Tagline too long ({len(strategy.tagline.split())} words, max 10)")
    if strategy.positioning.lower().strip() in GENERIC_POSITIONS:
        failures.append("Positioning is generic — must be specific to this business")
    if len(strategy.voice_attributes) < 3:
        failures.append("Need at least 3 voice attributes")
    if not strategy.brand_story or len(strategy.brand_story) < 20:
        failures.append("Brand story is too short")

    if not palette.passes_wcag_aa:
        failures.append(f"Palette fails WCAG AA: {palette.contrast_scores}")

    if not await verify_google_font(fonts.heading.family):
        failures.append(f"Heading font '{fonts.heading.family}' not found on Google Fonts")
    if not await verify_google_font(fonts.body.family):
        failures.append(f"Body font '{fonts.body.family}' not found on Google Fonts")

    if len(logo_urls) < 3:
        failures.append(f"Expected 3 logo concepts, got {len(logo_urls)}")

    for i, url in enumerate(logo_urls):
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                img = Image.open(BytesIO(resp.content))
                if img.width < 512 or img.height < 512:
                    failures.append(f"Logo {i + 1} is {img.width}x{img.height}, minimum 512x512")
        except (httpx.HTTPError, OSError, ValueError):
            failures.append(f"Logo {i + 1} could not be downloaded or read from {url}")

    return ValidationResult(passed=len(failures) == 0, failures=failures)
