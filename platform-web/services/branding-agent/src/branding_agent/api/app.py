import hmac
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from branding_agent.application.intake import analyze_brand_brief
from branding_agent.application.strategy import generate_strategy_package
from branding_agent.config import get_settings
from branding_agent.domain.brief import IntakeAnalysisResponse, IntakeRequest
from branding_agent.domain.strategy_package import (
    StrategyPackageRequest,
    StrategyPackageResponse,
)
from branding_agent.logging import configure_logging
from branding_agent.providers.factory import build_ai_service
from branding_agent.rendering.assets import AssetRenderError, render_brand_assets
from branding_agent.storage import LocalStorage, StorageNotConfigured, build_storage
from branding_agent.workflows.protocol import BrandingAI


class ChatRespondRequest(BaseModel):
    conversation_context: dict[str, Any] = Field(default_factory=dict)
    message_history: list[dict[str, Any]] = Field(default_factory=list)
    new_message: str = ""


class ChatExtractRequest(BaseModel):
    message_history: list[dict[str, Any]]


class StrategyRequest(BaseModel):
    description: str
    industry: str
    preferences: dict[str, Any] = Field(default_factory=dict)


class LogoRequest(BaseModel):
    strategy: dict[str, Any]
    industry: str
    style_keywords: list[str] | None = None


class StrategyOnlyRequest(BaseModel):
    strategy: dict[str, Any]


class PaletteRequest(StrategyOnlyRequest):
    industry: str


class ValidateRequest(BaseModel):
    strategy: dict[str, Any]
    palette: dict[str, Any]
    fonts: dict[str, Any]
    logo_urls: list[str]


class RenderAssetsRequest(BaseModel):
    brand_id: str
    business_id: str
    business_name: str
    version: int
    strategy: dict[str, Any] = Field(default_factory=dict)
    logo_urls: list[dict[str, Any] | str]
    colors: dict[str, Any] = Field(default_factory=dict)
    fonts: dict[str, Any] = Field(default_factory=dict)
    copy_data: dict[str, Any] = Field(default_factory=dict, alias="copy")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.ENV)
    app.state.ai = build_ai_service(settings)
    try:
        app.state.storage = build_storage(settings)
    except StorageNotConfigured:
        if settings.ENV != "development":
            raise
        app.state.storage = LocalStorage()
    yield


app = FastAPI(
    title="Cre8ive District Branding Agent",
    version="0.1.0",
    lifespan=lifespan,
)


def get_ai() -> BrandingAI:
    return app.state.ai


def require_service_key(x_agent_key: str | None = Header(default=None)) -> None:
    expected = get_settings().SERVICE_API_KEY
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Branding Agent service authentication is not configured",
        )
    if x_agent_key is None or not hmac.compare_digest(x_agent_key, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid service credentials",
        )


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "branding-agent"}


@app.post("/v1/chat/respond", dependencies=[Depends(require_service_key)])
async def respond(
    payload: ChatRespondRequest, ai: BrandingAI = Depends(get_ai)
) -> StreamingResponse:
    async def stream() -> AsyncIterator[str]:
        async for chunk in ai.respond(
            payload.conversation_context,
            payload.message_history,
            payload.new_message,
        ):
            yield chunk

    return StreamingResponse(stream(), media_type="text/plain; charset=utf-8")


@app.post("/v1/chat/extract", dependencies=[Depends(require_service_key)])
async def extract_context(
    payload: ChatExtractRequest, ai: BrandingAI = Depends(get_ai)
) -> dict[str, Any]:
    return await ai.extract_context(payload.message_history)


@app.post(
    "/v1/intake/analyze",
    response_model=IntakeAnalysisResponse,
    dependencies=[Depends(require_service_key)],
)
async def analyze_intake(
    payload: IntakeRequest, ai: BrandingAI = Depends(get_ai)
) -> IntakeAnalysisResponse:
    return await analyze_brand_brief(payload, ai)


@app.post("/v1/brand/strategy", dependencies=[Depends(require_service_key)])
async def generate_strategy(
    payload: StrategyRequest, ai: BrandingAI = Depends(get_ai)
) -> dict[str, Any]:
    result = await ai.generate_strategy(payload.description, payload.industry, payload.preferences)
    return result.model_dump()


@app.post(
    "/v1/brand/strategy-package",
    response_model=StrategyPackageResponse,
    dependencies=[Depends(require_service_key)],
)
async def create_strategy_package(
    payload: StrategyPackageRequest, ai: BrandingAI = Depends(get_ai)
) -> StrategyPackageResponse:
    return await generate_strategy_package(ai, payload.brief)


@app.post("/v1/brand/logos", dependencies=[Depends(require_service_key)])
async def generate_logos(
    payload: LogoRequest, ai: BrandingAI = Depends(get_ai)
) -> dict[str, list[str]]:
    from branding_agent.domain.ai_models import BrandStrategy

    strategy = BrandStrategy.model_validate(payload.strategy)
    return {
        "logo_urls": await ai.generate_logos(strategy, payload.industry, payload.style_keywords)
    }


@app.post("/v1/brand/palette", dependencies=[Depends(require_service_key)])
async def derive_palette(
    payload: PaletteRequest, ai: BrandingAI = Depends(get_ai)
) -> dict[str, Any]:
    from branding_agent.domain.ai_models import BrandStrategy

    strategy = BrandStrategy.model_validate(payload.strategy)
    result = await ai.derive_palette(strategy, payload.industry)
    return result.model_dump()


@app.post("/v1/brand/fonts", dependencies=[Depends(require_service_key)])
async def select_fonts(
    payload: StrategyOnlyRequest, ai: BrandingAI = Depends(get_ai)
) -> dict[str, Any]:
    from branding_agent.domain.ai_models import BrandStrategy

    result = await ai.select_fonts(BrandStrategy.model_validate(payload.strategy))
    return result.model_dump()


@app.post("/v1/brand/copy", dependencies=[Depends(require_service_key)])
async def generate_copy(
    payload: StrategyOnlyRequest, ai: BrandingAI = Depends(get_ai)
) -> dict[str, Any]:
    from branding_agent.domain.ai_models import BrandStrategy

    result = await ai.generate_copy(BrandStrategy.model_validate(payload.strategy))
    return result.model_dump()


@app.post("/v1/brand/validate", dependencies=[Depends(require_service_key)])
async def validate_output(
    payload: ValidateRequest, ai: BrandingAI = Depends(get_ai)
) -> dict[str, Any]:
    from branding_agent.domain.ai_models import (
        BrandStrategy,
        FontPair,
        PaletteResult,
    )

    result = await ai.validate_output(
        BrandStrategy.model_validate(payload.strategy),
        PaletteResult.model_validate(payload.palette),
        FontPair.model_validate(payload.fonts),
        payload.logo_urls,
    )
    return result.model_dump()


@app.post("/v1/brand/render-assets", dependencies=[Depends(require_service_key)])
async def render_assets(
    payload: RenderAssetsRequest,
) -> dict[str, Any]:
    try:
        return await render_brand_assets(payload.model_dump(by_alias=True), app.state.storage)
    except AssetRenderError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
