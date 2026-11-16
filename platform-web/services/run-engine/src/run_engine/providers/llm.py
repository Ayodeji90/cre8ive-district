from __future__ import annotations

import json
from typing import Protocol

from run_engine.config import Settings
from run_engine.domain.run import TaskType


class PlannerLLM(Protocol):
    async def complete(self, messages: list[dict]) -> str: ...


class StubPlanner:
    """Deterministic stub planner for tests or offline local environments."""

    def __init__(self) -> None:
        self.call_count = 0

    async def complete(self, messages: list[dict]) -> str:
        self.call_count += 1
        user_msg = messages[-1]["content"] if messages else ""

        # If brief request
        if "executive brief" in user_msg.lower():
            return (
                "Hello! Here is your latest executive brief from Abija.\n\n"
                "We made solid progress on your business foundations today. "
                "The core tasks scheduled were evaluated, and our key channels are moving forward smoothly.\n\n"
                "Next up, we will sharpen your outreach and website presentation to attract more buyers.\n\n"
                "— Abija, Cre8ive District"
            )

        # Task planning response
        tasks = [
            {
                "task_type": TaskType.BRAND_IMPROVEMENT.value,
                "title": "Sharpen Brand Positioning & Voice",
                "description": "Refine the brand tone of voice and core messaging for target customers.",
                "reasoning": "A sharp positioning makes every subsequent post, page, and email perform better.",
                "priority": 1,
                "channel": None,
                "input_data": {"focus": "value_proposition"},
            },
            {
                "task_type": TaskType.WEBSITE_IMPROVEMENT.value,
                "title": "Optimize Homepage Conversion Headline",
                "description": "Update hero headline and call-to-action copy for higher engagement.",
                "reasoning": "Clear, benefit-driven headlines directly boost conversion rates.",
                "priority": 2,
                "channel": "website",
                "input_data": {"section": "hero", "cta": "Get Started"},
            },
            {
                "task_type": TaskType.SOCIAL_POST.value,
                "title": "Create Instagram Announcement Post",
                "description": "Draft an engaging launch post with visual creative direction.",
                "reasoning": "Establishes immediate social proof and visibility for followers.",
                "priority": 3,
                "channel": "social_instagram",
                "input_data": {"platform": "instagram", "format": "carousel"},
            },
        ]
        return json.dumps(tasks)


class LiteLLMPlanner:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def complete(self, messages: list[dict]) -> str:
        import litellm

        model = self._settings.PLANNER_MODEL
        if not model.startswith("openrouter/") and "openrouter" in self._settings.OPENROUTER_API_BASE:
            model = f"openrouter/{model}"

        response = await litellm.acompletion(
            model=model,
            messages=messages,
            temperature=self._settings.PLANNER_TEMPERATURE,
            max_tokens=self._settings.PLANNER_MAX_TOKENS,
            api_key=self._settings.OPENROUTER_API_KEY,
            api_base=self._settings.OPENROUTER_API_BASE,
        )
        return response.choices[0].message.content or ""


def create_planner_llm(settings: Settings) -> PlannerLLM:
    if settings.AI_STUB or not settings.OPENROUTER_API_KEY:
        return StubPlanner()
    return LiteLLMPlanner(settings)
