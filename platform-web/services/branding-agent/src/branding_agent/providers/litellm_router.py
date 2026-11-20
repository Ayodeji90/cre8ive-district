"""LiteLLM-backed provider routing with bounded transient-error failover."""

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any

from pydantic import BaseModel

from branding_agent.logging import get_logger
from branding_agent.providers._llm import LLMResponse
from branding_agent.providers.deployments import LLMDeployment

log = get_logger(__name__)


class LiteLLMProvider:
    def __init__(
        self,
        deployments: list[LLMDeployment],
        timeout_seconds: float,
        router: Any | None = None,
    ) -> None:
        if not deployments:
            raise ValueError("At least one LLM deployment is required")
        if timeout_seconds <= 0:
            raise ValueError("LLM provider timeout must be greater than zero")

        self._deployments = deployments
        self._timeout_seconds = timeout_seconds
        model_list = [
            {
                "model_name": deployment.route_name,
                "litellm_params": {
                    "model": deployment.litellm_model,
                    "api_key": deployment.api_key,
                    **({"api_base": deployment.api_base} if deployment.api_base else {}),
                },
            }
            for deployment in deployments
        ]
        if router is None:
            from litellm import Router

            router = Router(model_list=model_list, num_retries=0)
        self._router = router

    def _starting_index(self, requested_model: str | None) -> int:
        if requested_model is None:
            return 0
        for index, deployment in enumerate(self._deployments):
            if requested_model in {
                deployment.route_name,
                deployment.model,
                deployment.litellm_model,
            }:
                return index
        raise ValueError(f"LLM model is not configured for routing: {requested_model}")

    @staticmethod
    def _is_retryable(exc: Exception) -> bool:
        if isinstance(exc, TimeoutError):
            return True

        from litellm.exceptions import (
            APIConnectionError,
            InternalServerError,
            RateLimitError,
            ServiceUnavailableError,
            Timeout,
        )

        return isinstance(
            exc,
            (
                APIConnectionError,
                InternalServerError,
                RateLimitError,
                ServiceUnavailableError,
                Timeout,
            ),
        )

    async def _acompletion_with_failover(
        self, model: str | None, **kwargs: Any
    ) -> tuple[Any, LLMDeployment]:
        start = self._starting_index(model)
        last_error: Exception | None = None
        for deployment in self._deployments[start:]:
            try:
                async with asyncio.timeout(self._timeout_seconds):
                    response = await self._router.acompletion(model=deployment.route_name, **kwargs)
                    return response, deployment
            except Exception as exc:
                if not self._is_retryable(exc):
                    raise
                last_error = exc
                log.warning(
                    "llm_provider_transient_failure",
                    provider=deployment.provider,
                    error_type=type(exc).__name__,
                    fallback_available=deployment is not self._deployments[-1],
                )
        if last_error is None:
            raise RuntimeError("No LLM provider was attempted")
        raise RuntimeError(
            f"All configured LLM providers failed transiently "
            f"({len(self._deployments) - start} attempted)."
        ) from last_error

    async def complete(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: type[BaseModel] | None = None,
    ) -> LLMResponse:
        kwargs: dict[str, Any] = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format is not None:
            kwargs["response_format"] = response_format

        response, deployment = await self._acompletion_with_failover(model, **kwargs)
        choice = response.choices[0]
        content = choice.message.content
        if not isinstance(content, str):
            content = json.dumps(content, ensure_ascii=False)
        usage = getattr(response, "usage", None)
        hidden_params = getattr(response, "_hidden_params", None) or {}
        return LLMResponse(
            content=content or "",
            model=getattr(response, "model", None) or deployment.model,
            input_tokens=getattr(usage, "prompt_tokens", 0) if usage else 0,
            output_tokens=getattr(usage, "completion_tokens", 0) if usage else 0,
            cost_usd=hidden_params.get("response_cost", 0.0),
        )

    async def stream(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        start = self._starting_index(model)
        last_error: Exception | None = None
        for deployment in self._deployments[start:]:
            yielded_content = False
            try:
                async with asyncio.timeout(self._timeout_seconds):
                    response = await self._router.acompletion(
                        model=deployment.route_name,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=True,
                    )
                    async for chunk in response:
                        choices = getattr(chunk, "choices", [])
                        if choices and choices[0].delta.content:
                            yielded_content = True
                            yield choices[0].delta.content
                return
            except Exception as exc:
                if yielded_content or not self._is_retryable(exc):
                    raise
                last_error = exc
                log.warning(
                    "llm_stream_provider_transient_failure",
                    provider=deployment.provider,
                    error_type=type(exc).__name__,
                    fallback_available=deployment is not self._deployments[-1],
                )
        if last_error is None:
            raise RuntimeError("No LLM provider was attempted")
        raise RuntimeError(
            "All configured LLM providers failed before the stream began."
        ) from last_error
