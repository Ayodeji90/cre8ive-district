"""Construct the configured in-process AI implementation for this service."""

from branding_agent.config import Settings
from branding_agent.logging import get_logger
from branding_agent.providers.deployments import LLMDeployment
from branding_agent.providers.litellm_router import LiteLLMProvider
from branding_agent.providers.stub import StubAIService
from branding_agent.storage import (
    LocalStorage,
    StorageNotConfigured,
    build_storage,
)
from branding_agent.workflows.ai_service import RealAIService
from branding_agent.workflows.protocol import BrandingAI

log = get_logger(__name__)


def build_llm_deployments(settings: Settings) -> list[LLMDeployment]:
    available = {
        "groq": (settings.GROQ_API_KEY, settings.GROQ_MODEL, None),
        "nvidia_nim": (
            settings.NVIDIA_NIM_API_KEY,
            settings.NVIDIA_NIM_MODEL,
            settings.NVIDIA_NIM_API_BASE,
        ),
        "openrouter": (
            settings.OPENROUTER_API_KEY,
            settings.OPENROUTER_MODEL,
            settings.OPENROUTER_API_BASE,
        ),
        "anthropic": (settings.ANTHROPIC_API_KEY, settings.ANTHROPIC_MODEL, None),
        "openai": (settings.OPENAI_API_KEY, settings.OPENAI_MODEL, None),
    }

    routing_order = [
        provider.strip().lower()
        for provider in settings.LLM_ROUTING_ORDER.split(",")
        if provider.strip()
    ]
    if settings.LLM_PROVIDER:
        legacy_provider = settings.LLM_PROVIDER.strip().lower()
        if legacy_provider not in available:
            raise ValueError(f"Unsupported LLM_PROVIDER: {settings.LLM_PROVIDER}")
        routing_order = [legacy_provider] + [
            provider for provider in routing_order if provider != legacy_provider
        ]

    if len(routing_order) != len(set(routing_order)):
        raise ValueError("LLM_ROUTING_ORDER must not contain duplicate providers")
    unknown_providers = set(routing_order) - available.keys()
    if unknown_providers:
        raise ValueError(
            "Unsupported provider(s) in LLM_ROUTING_ORDER: " + ", ".join(sorted(unknown_providers))
        )

    deployments: list[LLMDeployment] = []
    for provider in routing_order:
        api_key, model, api_base = available[provider]
        if not api_key.strip():
            continue
        if not model.strip():
            log.warning("llm_provider_skipped_missing_model", provider=provider)
            continue
        deployments.append(
            LLMDeployment(
                provider=provider,
                model=model.strip(),
                api_key=api_key,
                api_base=api_base.strip() or None if api_base else None,
            )
        )
    return deployments


def build_ai_service(settings: Settings) -> BrandingAI:
    if settings.AI_STUB:
        return StubAIService()

    deployments = build_llm_deployments(settings)
    if not deployments:
        raise RuntimeError(
            "No LLM provider is configured. Set a provider API key and model; "
            "see the Branding Agent README for examples."
        )
    llm = LiteLLMProvider(
        deployments=deployments,
        timeout_seconds=settings.LLM_PROVIDER_TIMEOUT_SECONDS,
    )

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
