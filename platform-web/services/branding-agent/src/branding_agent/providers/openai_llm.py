"""OpenAI LLM provider (GPT-4o fallback)."""

import time
from collections.abc import AsyncIterator

import openai
from pydantic import BaseModel

from branding_agent.logging import get_logger

from ._llm import LLMResponse

log = get_logger(__name__)

DEFAULT_MODEL = "gpt-4o"

_COST_PER_MTOK: dict[str, tuple[float, float]] = {
    "gpt-4o": (2.5, 10.0),
    "gpt-4o-mini": (0.15, 0.60),
}

MAX_RETRIES = 3
BACKOFF_BASE = 1.0


def _cost(model: str, input_tokens: int, output_tokens: int) -> float:
    inp, out = _COST_PER_MTOK.get(model, (2.5, 10.0))
    return (input_tokens * inp + output_tokens * out) / 1_000_000


class OpenAILLM:
    def __init__(self, api_key: str) -> None:
        self._client = openai.AsyncOpenAI(api_key=api_key)

    async def complete(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: type[BaseModel] | None = None,
    ) -> LLMResponse:
        model = model or DEFAULT_MODEL

        api_messages = [{"role": m["role"], "content": m["content"]} for m in messages]

        kwargs: dict = {
            "model": model,
            "messages": api_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_format is not None:
            kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": response_format.__name__,
                    "schema": response_format.model_json_schema(),
                    "strict": True,
                },
            }

        last_exc: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                t0 = time.monotonic()
                response = await self._client.chat.completions.create(**kwargs)
                latency = time.monotonic() - t0
                break
            except (openai.RateLimitError, openai.APIConnectionError) as exc:
                last_exc = exc
                if attempt < MAX_RETRIES - 1:
                    wait = BACKOFF_BASE * (2**attempt)
                    log.warning("openai_retry", attempt=attempt + 1, wait=wait)
                    import asyncio

                    await asyncio.sleep(wait)
        else:
            raise RuntimeError(f"OpenAI API failed after {MAX_RETRIES} attempts") from last_exc

        choice = response.choices[0]
        content = choice.message.content or ""
        usage = response.usage

        result = LLMResponse(
            content=content,
            model=response.model,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            cost_usd=_cost(model, usage.prompt_tokens, usage.completion_tokens) if usage else 0.0,
        )
        log.info(
            "llm_call",
            provider="openai",
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
        api_messages = [{"role": m["role"], "content": m["content"]} for m in messages]

        response = await self._client.chat.completions.create(
            model=model,
            messages=api_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in response:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content
