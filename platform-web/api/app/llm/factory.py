from collections.abc import AsyncIterator

from app.config import Settings
from app.llm.base import AIService, AIServiceNotConfigured
from app.llm.remote import build_ai_service
from app.schemas.ai import BrandCopy, BrandStrategy, FontPair, PaletteResult, ValidationResult


class FallbackAIService(AIService):
    """A no-op AI service used when the Branding Agent is not configured.

    It satisfies the AIService protocol so the chat paths that only need a
    greeting (e.g. local/development runs) do not fail with 503. All creative
    methods raise, since they have no sensible local fallback.
    """

    async def respond(
        self, conversation_context: dict, message_history: list[dict], new_message: str
    ) -> AsyncIterator[str]:
        if new_message.strip():
            yield (
                f"Got it — '{new_message.strip()[:60]}'⋯ I'll keep that in mind as we "
                f"build your brand.\n"
            )
        else:
            yield "Hi! What business are we building today?\n"

    async def extract_context(self, message_history: list[dict]) -> dict:
        return {}

    async def generate_strategy(
        self, description: str, industry: str, preferences: dict
    ) -> BrandStrategy:
        raise NotImplementedError("Branding Agent is not configured")

    async def generate_logos(self, strategy, industry, style_keywords=None) -> list[str]:
        raise NotImplementedError("Branding Agent is not configured")

    async def derive_palette(self, strategy, industry) -> PaletteResult:
        raise NotImplementedError("Branding Agent is not configured")

    async def select_fonts(self, strategy) -> FontPair:
        raise NotImplementedError("Branding Agent is not configured")

    async def generate_copy(self, strategy) -> BrandCopy:
        raise NotImplementedError("Branding Agent is not configured")

    async def validate_output(self, strategy, palette, fonts, logo_urls) -> ValidationResult:
        raise NotImplementedError("Branding Agent is not configured")


def get_ai_service(settings: Settings) -> AIService:
    if not settings.BRANDING_AGENT_URL or not settings.BRANDING_AGENT_API_KEY:
        return FallbackAIService()
    return build_ai_service(settings)


__all__ = ["AIService", "AIServiceNotConfigured", "get_ai_service", "FallbackAIService"]
