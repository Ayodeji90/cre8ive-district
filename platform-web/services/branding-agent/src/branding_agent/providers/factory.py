"""Construct the configured in-process AI implementation for this service."""

from branding_agent.config import Settings
from branding_agent.providers.stub import StubAIService
from branding_agent.storage import (
    LocalStorage,
    StorageNotConfigured,
    build_storage,
)
from branding_agent.workflows.ai_service import RealAIService
from branding_agent.workflows.protocol import BrandingAI


def build_ai_service(settings: Settings) -> BrandingAI:
    if settings.AI_STUB:
        return StubAIService()

    if settings.LLM_PROVIDER == "openai":
        from branding_agent.providers.openai_llm import OpenAILLM

        llm = OpenAILLM(api_key=settings.OPENAI_API_KEY)
    else:
        from branding_agent.providers.anthropic import AnthropicLLM

        llm = AnthropicLLM(api_key=settings.ANTHROPIC_API_KEY)

    try:
        storage = build_storage(settings)
    except StorageNotConfigured:
        if settings.ENV != "development":
            raise
        storage = LocalStorage()

    if settings.IMAGE_PROVIDER == "dalle" or not settings.IDEOGRAM_API_KEY:
        from branding_agent.providers.image_gen.dalle import DalleProvider

        image_provider = DalleProvider(api_key=settings.OPENAI_API_KEY, storage=storage)
    else:
        from branding_agent.providers.image_gen.ideogram import IdeogramProvider

        image_provider = IdeogramProvider(api_key=settings.IDEOGRAM_API_KEY, storage=storage)

    return RealAIService(llm=llm, image_provider=image_provider)
