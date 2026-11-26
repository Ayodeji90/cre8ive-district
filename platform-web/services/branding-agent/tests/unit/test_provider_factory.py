import pytest

from branding_agent.config import Settings
from branding_agent.providers.factory import build_ai_service, build_llm_deployments


def test_build_llm_deployments_uses_configured_order_and_skips_missing_keys() -> None:
    settings = Settings(
        _env_file=None,
        LLM_ROUTING_ORDER="nvidia_nim,groq,openrouter",
        NVIDIA_NIM_API_KEY="nim-key",
        NVIDIA_NIM_MODEL="org/model-a",
        GROQ_API_KEY="groq-key",
        GROQ_MODEL="model-b",
        OPENROUTER_MODEL="org/model-c",
    )

    deployments = build_llm_deployments(settings)

    assert [deployment.provider for deployment in deployments] == ["nvidia_nim", "groq"]
    assert deployments[0].litellm_model == "nvidia_nim/org/model-a"
    assert deployments[1].litellm_model == "groq/model-b"


def test_legacy_provider_setting_moves_that_provider_to_the_front() -> None:
    settings = Settings(
        _env_file=None,
        LLM_PROVIDER="openai",
        LLM_ROUTING_ORDER="groq,nvidia_nim,openrouter",
        OPENAI_API_KEY="openai-key",
        GROQ_API_KEY="groq-key",
        GROQ_MODEL="model-b",
    )

    deployments = build_llm_deployments(settings)

    assert [deployment.provider for deployment in deployments] == ["openai", "groq"]


def test_default_routing_does_not_fall_back_to_paid_providers() -> None:
    settings = Settings(
        _env_file=None,
        OPENROUTER_API_KEY="openrouter-key",
        OPENROUTER_MODEL="baidu/ernie-5.5-flash-preview:free",
        ANTHROPIC_API_KEY="anthropic-key",
        OPENAI_API_KEY="openai-key",
    )

    deployments = build_llm_deployments(settings)

    assert [deployment.provider for deployment in deployments] == ["openrouter"]


def test_build_ai_service_requires_at_least_one_configured_llm() -> None:
    with pytest.raises(RuntimeError, match="No LLM provider is configured"):
        build_ai_service(Settings(_env_file=None, AI_STUB=False))


def test_build_ai_service_preserves_stub_mode_without_provider_keys() -> None:
    service = build_ai_service(Settings(_env_file=None, AI_STUB=True))

    assert service.__class__.__name__ == "StubAIService"
