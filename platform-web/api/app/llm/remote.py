"""HTTP client adapter for the independently deployed Branding Agent."""

from collections.abc import AsyncIterator

import httpx

from app.config import Settings
from app.llm.base import AIService, AIServiceNotConfigured
from app.logging import get_logger
from app.schemas.ai import (
    BrandCopy,
    BrandStrategy,
    FontPair,
    PaletteResult,
    ValidationResult,
)

log = get_logger(__name__)


class BrandingAgentError(RuntimeError):
    pass


class BrandingAgentClient(AIService):
    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = 300.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout
        self._transport = transport

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self._base_url,
            headers={"X-Agent-Key": self._api_key},
            timeout=httpx.Timeout(self._timeout, connect=10.0),
            transport=self._transport,
        )

    async def _post(self, path: str, payload: dict) -> dict:
        try:
            async with self._client() as client:
                response = await client.post(path, json=payload)
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            log.error("branding_agent_request_failed", path=path, exc_info=True)
            raise BrandingAgentError(f"Branding Agent request failed at {path}") from exc

    async def respond(
        self, conversation_context: dict, message_history: list[dict], new_message: str
    ) -> AsyncIterator[str]:
        try:
            async with self._client() as client:
                async with client.stream(
                    "POST",
                    "/v1/chat/respond",
                    json={
                        "conversation_context": conversation_context,
                        "message_history": message_history,
                        "new_message": new_message,
                    },
                ) as response:
                    response.raise_for_status()
                    async for chunk in response.aiter_text():
                        if chunk:
                            yield chunk
        except httpx.HTTPError as exc:
            log.error("branding_agent_stream_failed", path="/v1/chat/respond", exc_info=True)
            raise BrandingAgentError("Branding Agent chat request failed") from exc

    async def extract_context(self, message_history: list[dict]) -> dict:
        return await self._post("/v1/chat/extract", {"message_history": message_history})

    async def generate_strategy(
        self, description: str, industry: str, preferences: dict
    ) -> BrandStrategy:
        result = await self._post(
            "/v1/brand/strategy",
            {"description": description, "industry": industry, "preferences": preferences},
        )
        return BrandStrategy.model_validate(result)

    async def generate_logos(
        self, strategy: BrandStrategy, industry: str, style_keywords: list[str] | None = None
    ) -> list[str]:
        result = await self._post(
            "/v1/brand/logos",
            {
                "strategy": strategy.model_dump(),
                "industry": industry,
                "style_keywords": style_keywords,
            },
        )
        return result["logo_urls"]

    async def derive_palette(self, strategy: BrandStrategy, industry: str) -> PaletteResult:
        result = await self._post(
            "/v1/brand/palette",
            {"strategy": strategy.model_dump(), "industry": industry},
        )
        return PaletteResult.model_validate(result)

    async def select_fonts(self, strategy: BrandStrategy) -> FontPair:
        result = await self._post("/v1/brand/fonts", {"strategy": strategy.model_dump()})
        return FontPair.model_validate(result)

    async def generate_copy(self, strategy: BrandStrategy) -> BrandCopy:
        result = await self._post("/v1/brand/copy", {"strategy": strategy.model_dump()})
        return BrandCopy.model_validate(result)

    async def validate_output(
        self,
        strategy: BrandStrategy,
        palette: PaletteResult,
        fonts: FontPair,
        logo_urls: list[str],
    ) -> ValidationResult:
        result = await self._post(
            "/v1/brand/validate",
            {
                "strategy": strategy.model_dump(),
                "palette": palette.model_dump(),
                "fonts": fonts.model_dump(),
                "logo_urls": logo_urls,
            },
        )
        return ValidationResult.model_validate(result)


def build_ai_service(settings: Settings) -> BrandingAgentClient:
    if not settings.BRANDING_AGENT_URL:
        raise AIServiceNotConfigured("BRANDING_AGENT_URL is not configured")
    if not settings.BRANDING_AGENT_API_KEY:
        raise AIServiceNotConfigured("BRANDING_AGENT_API_KEY is not configured")
    return BrandingAgentClient(
        base_url=settings.BRANDING_AGENT_URL,
        api_key=settings.BRANDING_AGENT_API_KEY,
    )
