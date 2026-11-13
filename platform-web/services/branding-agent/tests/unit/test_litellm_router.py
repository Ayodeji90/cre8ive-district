import asyncio
import inspect
from types import SimpleNamespace

import pytest
from litellm.exceptions import (
    APIConnectionError,
    InternalServerError,
    RateLimitError,
    ServiceUnavailableError,
    Timeout,
)
from pydantic import BaseModel

from branding_agent.providers.deployments import LLMDeployment
from branding_agent.providers.litellm_router import LiteLLMProvider


class BriefOutput(BaseModel):
    summary: str


class RetryableTestError(Exception):
    pass


class FakeRouter:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []

    async def acompletion(self, **kwargs):
        self.calls.append(kwargs)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        if callable(outcome):
            result = outcome()
            if inspect.isawaitable(result):
                return await result
            return result
        return outcome


def deployments():
    return [
        LLMDeployment("groq", "test-model", "groq-secret"),
        LLMDeployment("nvidia_nim", "test-model", "nim-secret"),
    ]


def response(content="generated", model="test-model"):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))],
        model=model,
        usage=SimpleNamespace(prompt_tokens=11, completion_tokens=7),
        _hidden_params={"response_cost": 0.001},
    )


@pytest.mark.parametrize(
    "error_type",
    [
        APIConnectionError,
        InternalServerError,
        RateLimitError,
        ServiceUnavailableError,
        Timeout,
    ],
)
def test_litellm_transient_errors_are_retryable(error_type) -> None:
    error = error_type("temporary provider failure", llm_provider="groq", model="test-model")

    assert LiteLLMProvider._is_retryable(error)


@pytest.mark.asyncio
async def test_complete_retries_with_same_context_and_schema_on_next_provider() -> None:
    messages = [{"role": "user", "content": "brief context"}]
    router = FakeRouter([RetryableTestError("limited"), response()])
    llm = LiteLLMProvider(deployments(), timeout_seconds=1, router=router)
    llm._is_retryable = lambda exc: isinstance(exc, RetryableTestError)

    result = await llm.complete(
        messages,
        temperature=0.2,
        response_format=BriefOutput,
    )

    assert result.content == "generated"
    assert result.input_tokens == 11
    assert result.output_tokens == 7
    assert result.cost_usd == 0.001
    assert [call["model"] for call in router.calls] == [
        "branding-groq",
        "branding-nvidia_nim",
    ]
    assert all(call["messages"] is messages for call in router.calls)
    assert all(call["response_format"] is BriefOutput for call in router.calls)


@pytest.mark.asyncio
async def test_complete_uses_requested_deployment_and_reports_its_model() -> None:
    router = FakeRouter([response(model=None)])
    llm = LiteLLMProvider(deployments(), timeout_seconds=1, router=router)

    result = await llm.complete(
        [{"role": "user", "content": "hello"}],
        model="nvidia_nim/test-model",
    )

    assert router.calls[0]["model"] == "branding-nvidia_nim"
    assert result.model == "test-model"


@pytest.mark.asyncio
async def test_complete_does_not_fallback_for_non_retryable_errors() -> None:
    router = FakeRouter([ValueError("invalid request"), response()])
    llm = LiteLLMProvider(deployments(), timeout_seconds=1, router=router)

    with pytest.raises(ValueError, match="invalid request"):
        await llm.complete([{"role": "user", "content": "hello"}])

    assert len(router.calls) == 1


@pytest.mark.asyncio
async def test_complete_falls_back_after_a_provider_timeout() -> None:
    async def slow_response():
        await asyncio.sleep(0.05)

    router = FakeRouter([slow_response, response()])
    llm = LiteLLMProvider(deployments(), timeout_seconds=0.005, router=router)

    result = await llm.complete([{"role": "user", "content": "hello"}])

    assert result.content == "generated"
    assert len(router.calls) == 2


@pytest.mark.asyncio
async def test_stream_falls_back_if_provider_fails_before_emitting_content() -> None:
    async def failed_stream():
        raise RetryableTestError("provider unavailable")
        yield "unreachable"

    async def good_stream():
        yield SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="answer"))])

    router = FakeRouter([failed_stream, good_stream])
    llm = LiteLLMProvider(deployments(), timeout_seconds=1, router=router)
    llm._is_retryable = lambda exc: isinstance(exc, RetryableTestError)

    chunks = [chunk async for chunk in llm.stream([{"role": "user", "content": "hello"}])]

    assert chunks == ["answer"]
    assert len(router.calls) == 2


@pytest.mark.asyncio
async def test_stream_does_not_restart_after_content_was_sent() -> None:
    async def partial_then_failed():
        yield SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="partial"))])
        raise RetryableTestError("connection lost")

    router = FakeRouter([partial_then_failed, response()])
    llm = LiteLLMProvider(deployments(), timeout_seconds=1, router=router)
    llm._is_retryable = lambda exc: isinstance(exc, RetryableTestError)
    chunks = []

    with pytest.raises(RetryableTestError, match="connection lost"):
        async for chunk in llm.stream([{"role": "user", "content": "hello"}]):
            chunks.append(chunk)

    assert chunks == ["partial"]
    assert len(router.calls) == 1
