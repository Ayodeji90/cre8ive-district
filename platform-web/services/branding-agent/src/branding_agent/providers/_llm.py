"""Internal LLM protocol used by the AI layer.

This is NOT the same as the top-level AIService protocol the backend calls.
This is the lower-level abstraction over individual LLM providers (Anthropic,
OpenAI) that the AI service implementation uses internally.
"""

from collections.abc import AsyncIterator
from typing import Protocol

from pydantic import BaseModel


class LLMResponse(BaseModel):
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float


class LLMProvider(Protocol):
    async def complete(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: type[BaseModel] | None = None,
    ) -> LLMResponse: ...

    def stream(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]: ...
