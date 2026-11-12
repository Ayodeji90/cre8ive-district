"""Anthropic LLM provider (Claude Sonnet 5.5 / Opus 5.5)."""

import json
import time
from collections.abc import AsyncIterator

import anthropic
from pydantic import BaseModel

from branding_agent.logging import get_logger

from ._llm import LLMResponse

log = get_logger(__name__)

DEFAULT_MODEL = "claude-sonnet-5-5"
QUALITY_MODEL = "claude-opus-5-5"

_COST_PER_MTOK: dict[str, tuple[float, float]] = {
    "claude-sonnet-5-5": (3.0, 15.0),
    "claude-opus-5-5": (15.0, 75.0),
}

MAX_RETRIES = 3
BACKOFF_BASE = 1.0


def _cost(model: str, input_tokens: int, output_tokens: int) -> float:
    inp, out = _COST_PER_MTOK.get(model, (3.0, 15.0))
    return (input_tokens * inp + output_tokens * out) / 1_000_000


class AnthropicLLM:
    def __init__(self, api_key: str) -> None:
        self._client = anthropic.AsyncAnthropic(api_key=api_key)

    async def complete(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: type[BaseModel] | None = None,
    ) -> LLMResponse:
        model = model or DEFAULT_MODEL

        system_parts: list[str] = []
        api_messages: list[dict] = []
        for msg in messages:
            if msg["role"] == "system":
                system_parts.append(msg["content"])
            else:
                api_messages.append({"role": msg["role"], "content": msg["content"]})

        kwargs: dict = {
            "model": model,
            "messages": api_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if system_parts:
            kwargs["system"] = "\n\n".join(system_parts)

        if response_format is not None:
            schema = response_format.model_json_schema()
            kwargs["tools"] = [
                {
                    "name": "structured_output",
                    "description": "Return structured data matching the schema.",
                    "input_schema": schema,
                }
            ]
            kwargs["tool_choice"] = {"type": "tool", "name": "structured_output"}

        last_exc: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                t0 = time.monotonic()
                response = await self._client.messages.create(**kwargs)
                latency = time.monotonic() - t0
                break
            except (anthropic.RateLimitError, anthropic.APIConnectionError) as exc:
                last_exc = exc
                if attempt < MAX_RETRIES - 1:
                    wait = BACKOFF_BASE * (2**attempt)
                    log.warning("anthropic_retry", attempt=attempt + 1, wait=wait)
                    import asyncio

                    await asyncio.sleep(wait)
        else:
            raise RuntimeError(f"Anthropic API failed after {MAX_RETRIES} attempts") from last_exc

        if response_format is not None:
            for block in response.content:
                if block.type == "tool_use":
                    content = json.dumps(block.input)
                    break
            else:
                content = response.content[0].text or ""
        else:
            content = response.content[0].text or ""

        result = LLMResponse(
            content=content,
            model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            cost_usd=_cost(model, response.usage.input_tokens, response.usage.output_tokens),
        )
        log.info(
            "llm_call",
            provider="anthropic",
            model=response.model,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            cost_usd=round(result.cost_usd, 6),
            latency_ms=round(latency * 1000),
        )
        return result

    async def stream(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        model = model or DEFAULT_MODEL

        system_parts: list[str] = []
        api_messages: list[dict] = []
        for msg in messages:
            if msg["role"] == "system":
                system_parts.append(msg["content"])
            else:
                api_messages.append({"role": msg["role"], "content": msg["content"]})

        kwargs: dict = {
            "model": model,
            "messages": api_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if system_parts:
            kwargs["system"] = "\n\n".join(system_parts)

        async with self._client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text
