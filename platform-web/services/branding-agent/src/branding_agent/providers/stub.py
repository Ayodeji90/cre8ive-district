"""Deterministic AI stand-in for local development and tests.

This is infrastructure glue, not product intelligence: it exists so the API can
be exercised end-to-end before the AI engineer's providers are wired in. Real
generation lives behind the same `AIService` interface.
"""

from collections.abc import AsyncIterator

from branding_agent.domain.ai_models import (
    BrandCopy,
    BrandStrategy,
    ColorPalette,
    FontPair,
    FontSpec,
    PaletteResult,
    ValidationResult,
)
from branding_agent.domain.brief import BriefExtraction
from branding_agent.logging import get_logger

log = get_logger(__name__)

GREETING = (
    "Hey! I'm Abija, your brand partner at Cre8ive District. "
    "What business or idea are you working on?"
)


class StubAIService:
    async def extract_brand_brief(
        self,
        raw_brief: str | None,
        structured_brief: dict | None,
        conversation_history: list[dict],
    ) -> BriefExtraction:
        return BriefExtraction.empty()

    async def respond(
        self, conversation_context: dict, message_history: list[dict], new_message: str
    ) -> AsyncIterator[str]:
        if not new_message:
            yield GREETING
            return
        stage = conversation_context.get("conversation_stage", "greeting")
        if stage == "summary_confirm":
            yield "Perfect. I'm on it — give me about a minute to put your brand together."
        else:
            yield (
                "I love where this is going. Tell me a bit more about who your ideal customer is."
            )

    async def extract_context(self, message_history: list[dict]) -> dict:
        turns = sum(1 for m in message_history if m.get("role") == "user")
        stage = "greeting"
        if turns >= 1:
            stage = "business_description"
        if turns >= 3:
            stage = "industry_refine"
        if turns >= 5:
            stage = "style_preferences"
        if turns >= 7:
            stage = "summary_confirm"
        return {
            "conversation_stage": stage,
            "ready_to_generate": turns >= 8,
        }

    async def generate_strategy(
        self, description: str, industry: str, preferences: dict
    ) -> BrandStrategy:
        name = preferences.get("business_name") or "Your Brand"
        context = preferences.get("target_audience") or "customers seeking a thoughtful experience"
        market = preferences.get("market_or_geography") or "urban Nigeria"
        return BrandStrategy(
            primary_name=name,
            name_alternatives=[f"{name} Co.", f"{name} Collective"],
            positioning=(
                f"A {industry or 'modern'} brand that turns {description[:60]} "
                "into a more personal customer experience."
            ),
            tagline="Made for what's next",
            voice_attributes=["warm", "confident", "distinctive"],
            brand_story=(
                f"{name} began with a simple observation: people deserve more than the usual "
                f"way of experiencing {description[:100]}. Built for {context}, it brings "
                f"care and character to every interaction."
            ),
            elevator_pitch=(
                f"{name} brings {description[:100]} to {context} across {market}. "
                "By pairing a distinctive point of view with a human, dependable experience, "
                "the brand gives customers a compelling reason to choose it and return."
            ),
            target_description=(
                f"{context} in {market}, looking for a more personal and dependable option."
            ),
            industry_keywords=[
                industry or "brand",
                "Nigeria",
                "African market",
                "customer experience",
                "local business",
                "brand strategy",
                "modern services",
                "community",
            ],
        )

    async def generate_logos(
        self, strategy: BrandStrategy, industry: str, style_keywords: list[str] | None = None
    ) -> list[str]:
        return [
            f"https://placeholder.cre8ivedistrict.com/logos/{strategy.primary_name}-{i}.png"
            for i in range(1, 4)
        ]

    async def derive_palette(self, strategy: BrandStrategy, industry: str) -> PaletteResult:
        palette = ColorPalette(
            primary="#F36B35",
            secondary="#2D2D2D",
            accent="#F4B942",
            neutral="#2D2D2D",
            background="#F5F5EE",
        )
        return PaletteResult(
            palette=palette,
            contrast_scores={"primary_on_bg": 3.1, "neutral_on_bg": 12.6},
            passes_wcag_aa=True,
        )

    async def select_fonts(self, strategy: BrandStrategy) -> FontPair:
        return FontPair(
            heading=FontSpec(family="Plus Jakarta Sans", weight=800),
            body=FontSpec(family="Plus Jakarta Sans", weight=400),
        )

    async def generate_copy(self, strategy: BrandStrategy) -> BrandCopy:
        return BrandCopy(
            tagline_variants=[strategy.tagline],
            instagram_bio=f"{strategy.primary_name} — {strategy.tagline}",
            linkedin_summary=strategy.positioning,
            whatsapp_status=strategy.tagline,
            elevator_pitch=strategy.elevator_pitch,
            one_liner=strategy.positioning,
            social_hashtags=["#brand", "#nigeria"],
        )

    async def validate_output(
        self,
        strategy: BrandStrategy,
        palette: PaletteResult,
        fonts: FontPair,
        logo_urls: list[str],
    ) -> ValidationResult:
        failures: list[str] = []
        if len(strategy.tagline.split()) > 10:
            failures.append("Tagline is longer than 10 words")
        if len(logo_urls) < 3:
            failures.append("Expected 3 logo concepts")
        return ValidationResult(passed=not failures, failures=failures)
