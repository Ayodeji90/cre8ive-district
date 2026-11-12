"""Client-side contract for the remote Branding Agent."""

from collections.abc import AsyncIterator
from typing import Protocol

from app.schemas.ai import (
    BrandCopy,
    BrandStrategy,
    FontPair,
    PaletteResult,
    ValidationResult,
)


class AIServiceNotConfigured(RuntimeError):
    pass


class AIService(Protocol):
    def respond(
        self,
        conversation_context: dict,
        message_history: list[dict],
        new_message: str,
    ) -> AsyncIterator[str]: ...

    async def extract_context(self, message_history: list[dict]) -> dict: ...

    async def generate_strategy(
        self, description: str, industry: str, preferences: dict
    ) -> BrandStrategy: ...

    async def generate_logos(
        self, strategy: BrandStrategy, industry: str, style_keywords: list[str] | None = None
    ) -> list[str]: ...

    async def derive_palette(self, strategy: BrandStrategy, industry: str) -> PaletteResult: ...

    async def select_fonts(self, strategy: BrandStrategy) -> FontPair: ...

    async def generate_copy(self, strategy: BrandStrategy) -> BrandCopy: ...

    async def validate_output(
        self,
        strategy: BrandStrategy,
        palette: PaletteResult,
        fonts: FontPair,
        logo_urls: list[str],
    ) -> ValidationResult: ...
