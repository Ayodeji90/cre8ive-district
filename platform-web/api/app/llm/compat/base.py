"""The seam between the backend and the AI engineer's services.

Nothing in the backend imports provider SDKs directly. The AI engineer supplies
an object implementing `AIService`; `app.llm.factory` is the only place that
decides which implementation is active.
"""

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
    ) -> AsyncIterator[str]:
        """Yield Abija's response chunks for streaming."""
        ...

    async def extract_context(self, message_history: list[dict]) -> dict:
        """Extract the accumulated brand brief from the conversation."""
        ...

    async def generate_strategy(
        self, description: str, industry: str, preferences: dict
    ) -> BrandStrategy: ...

    async def generate_logos(
        self, strategy: BrandStrategy, industry: str, style_keywords: list[str] | None = None
    ) -> list[str]:
        """Return 3 logo URLs (uploaded to R2 by the AI layer)."""
        ...

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
