"""Branding intelligence implemented using configured LLM and image providers."""

import json
from collections.abc import AsyncIterator

from branding_agent.domain.ai_models import (
    BrandCopy,
    BrandStrategy,
    ColorPalette,
    FontPair,
    PaletteResult,
    ValidationResult,
)
from branding_agent.domain.brief import BriefExtraction
from branding_agent.domain.fonts import FONT_PAIRS, get_font_pair
from branding_agent.logging import get_logger
from branding_agent.prompts import render_prompt
from branding_agent.providers._llm import LLMProvider
from branding_agent.providers.image_gen.base import ImageProvider
from branding_agent.quality.validation import validate_brand_output, validate_palette

log = get_logger(__name__)

MAX_PALETTE_RETRIES = 2


class RealAIService:
    def __init__(
        self,
        llm: LLMProvider,
        image_provider: ImageProvider,
    ) -> None:
        self._llm = llm
        self._image = image_provider

    async def extract_brand_brief(
        self,
        raw_brief: str | None,
        structured_brief: dict | None,
        conversation_history: list[dict],
    ) -> BriefExtraction:
        prompt = render_prompt("brief_extract")
        input_data = json.dumps(
            {
                "raw_brief": raw_brief or "",
                "structured_brief": structured_brief or {},
                "conversation": conversation_history,
            },
            ensure_ascii=False,
        )
        response = await self._llm.complete(
            [
                {"role": "system", "content": prompt},
                {"role": "user", "content": input_data},
            ],
            response_format=BriefExtraction,
            temperature=0.1,
        )
        return BriefExtraction.model_validate_json(response.content)

    async def respond(
        self,
        conversation_context: dict,
        message_history: list[dict],
        new_message: str,
    ) -> AsyncIterator[str]:
        stage = conversation_context.get("conversation_stage", "greeting")
        extracted = conversation_context

        system = render_prompt("abija_system", stage=stage, extracted=extracted)
        messages: list[dict] = [{"role": "system", "content": system}]
        messages.extend(message_history)
        if new_message:
            messages.append({"role": "user", "content": new_message})

        async for chunk in self._llm.stream(messages, temperature=0.8):
            yield chunk

    async def extract_context(self, message_history: list[dict]) -> dict:
        from branding_agent.domain.ai_models import BrandBriefExtract

        prompt = render_prompt("context_extract", conversation=message_history)
        response = await self._llm.complete(
            [{"role": "user", "content": prompt}],
            response_format=BrandBriefExtract,
            temperature=0.2,
        )
        parsed = BrandBriefExtract.model_validate_json(response.content)
        return parsed.model_dump(exclude_none=True)

    async def generate_strategy(
        self, description: str, industry: str, preferences: dict
    ) -> BrandStrategy:
        prompt = render_prompt(
            "brand_strategy",
            description=description,
            industry=industry,
            preferences=preferences,
        )
        response = await self._llm.complete(
            [{"role": "user", "content": prompt}],
            response_format=BrandStrategy,
            temperature=0.7,
        )
        strategy = BrandStrategy.model_validate_json(response.content)
        log.info(
            "brand_strategy_generated",
            name=strategy.primary_name,
            tagline=strategy.tagline,
            cost_usd=response.cost_usd,
        )
        return strategy

    async def generate_logos(
        self,
        strategy: BrandStrategy,
        industry: str,
        style_keywords: list[str] | None = None,
    ) -> list[str]:
        concepts = ["icon_wordmark", "abstract_mark", "lettermark"]
        urls: list[str] = []

        for concept in concepts:
            prompt = render_prompt(
                "logo_brief",
                strategy=strategy,
                industry=industry,
                style=style_keywords,
                concept=concept,
            )
            try:
                results = await self._image.generate(prompt=prompt, size="1024x1024", n=1)
                if results:
                    urls.append(results[0].url)
            except Exception:
                log.warning("logo_generation_failed", concept=concept, exc_info=True)

        log.info("logos_generated", count=len(urls))
        return urls

    async def derive_palette(self, strategy: BrandStrategy, industry: str) -> PaletteResult:
        prompt = render_prompt("palette", strategy=strategy, industry=industry)
        response = await self._llm.complete(
            [{"role": "user", "content": prompt}],
            response_format=ColorPalette,
            temperature=0.7,
        )
        palette = ColorPalette.model_validate_json(response.content)
        result = validate_palette(palette)

        retries = 0
        while not result.passes_wcag_aa and retries < MAX_PALETTE_RETRIES:
            retries += 1
            failing_pairs = [f"{k}: {v:.1f}" for k, v in result.contrast_scores.items() if v < 4.5]
            fix_prompt = (
                f"The palette you generated has contrast issues: {', '.join(failing_pairs)}. "
                f"WCAG AA requires at least 4.5:1 for primary and neutral on background. "
                f"Adjust the colours to fix these ratios while keeping the same mood and hues. "
                f"Current palette: {json.dumps(palette.model_dump())}. "
                "Return ONLY the corrected JSON object with primary, secondary, accent, "
                "neutral, background."
            )
            response = await self._llm.complete(
                [{"role": "user", "content": fix_prompt}],
                response_format=ColorPalette,
                temperature=0.3,
            )
            palette = ColorPalette.model_validate_json(response.content)
            result = validate_palette(palette)

        log.info(
            "palette_derived",
            passes_wcag=result.passes_wcag_aa,
            retries=retries,
            scores=result.contrast_scores,
        )
        return result

    async def select_fonts(self, strategy: BrandStrategy) -> FontPair:
        prompt = render_prompt("font_pairing", strategy=strategy, font_pairs=FONT_PAIRS)
        response = await self._llm.complete(
            [{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        try:
            data = json.loads(response.content)
            index = int(data["index"])
        except (json.JSONDecodeError, KeyError, ValueError):
            index = 2  # fallback: Plus Jakarta Sans

        pair = get_font_pair(index)
        log.info(
            "fonts_selected",
            heading=pair.heading.family,
            body=pair.body.family,
            index=index,
        )
        return pair

    async def generate_copy(self, strategy: BrandStrategy) -> BrandCopy:
        prompt = render_prompt("copy_gen", strategy=strategy)
        response = await self._llm.complete(
            [{"role": "user", "content": prompt}],
            response_format=BrandCopy,
            temperature=0.7,
        )
        copy = BrandCopy.model_validate_json(response.content)
        log.info("copy_generated", tagline_count=len(copy.tagline_variants))
        return copy

    async def validate_output(
        self,
        strategy: BrandStrategy,
        palette: PaletteResult,
        fonts: FontPair,
        logo_urls: list[str],
    ) -> ValidationResult:
        return await validate_brand_output(strategy, palette, fonts, logo_urls)
