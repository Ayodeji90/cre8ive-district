from __future__ import annotations

import json
import logging

from run_engine.capabilities.base import Capability
from run_engine.capabilities.standard import (
    AnalyticsReviewCapability,
    BrandImprovementCapability,
    CompetitorResearchCapability,
    ContentCreationCapability,
    OutreachEmailCapability,
    SEOOptimizationCapability,
    SocialPostCapability,
    WebsiteImprovementCapability,
)
from run_engine.domain.run import BusinessContext, RunTask, TaskType

logger = logging.getLogger(__name__)


class TaskExecutor:
    """Dispatches planned tasks to registered capability implementations."""

    def __init__(self, llm=None) -> None:
        self._capabilities: dict[TaskType, Capability] = {}
        self._llm = llm
        if llm is None:
            self._register_defaults()
        else:
            for task_type in TaskType:
                self.register(task_type, LLMArtifactCapability(llm))

    def _register_defaults(self) -> None:
        self.register(TaskType.BRAND_IMPROVEMENT, BrandImprovementCapability())
        self.register(TaskType.WEBSITE_IMPROVEMENT, WebsiteImprovementCapability())
        self.register(TaskType.SOCIAL_POST, SocialPostCapability())
        self.register(TaskType.OUTREACH_EMAIL, OutreachEmailCapability())
        self.register(TaskType.COMPETITOR_RESEARCH, CompetitorResearchCapability())
        self.register(TaskType.CONTENT_CREATION, ContentCreationCapability())
        self.register(TaskType.SEO_OPTIMIZATION, SEOOptimizationCapability())
        self.register(TaskType.ANALYTICS_REVIEW, AnalyticsReviewCapability())

    def register(self, task_type: TaskType, capability: Capability) -> None:
        self._capabilities[task_type] = capability

    async def execute(self, task: RunTask, context: BusinessContext) -> dict:
        capability = self._capabilities.get(task.task_type)
        if capability is None:
            raise ValueError(f"No capability registered for task type: {task.task_type.value}")
        logger.info("Executing task [%s]: %s", task.task_type.value, task.title)
        return await capability.execute(task, context)

    async def deliver(self, task: RunTask, result: dict, business_id=None) -> None:
        capability = self._capabilities.get(task.task_type)
        if capability is None:
            return
        await capability.deliver(task, result)
        await self._deduct_credits(task, business_id)

    async def _deduct_credits(self, task: RunTask, business_id=None) -> None:
        from run_engine.config import get_settings

        settings = get_settings()
        if not settings.PLATFORM_API_URL or not settings.PLATFORM_API_KEY:
            return
        if business_id is None:
            raise ValueError("Business id is required to charge run task credits")
        try:
            import httpx

            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{settings.PLATFORM_API_URL}/api/billing/internal/{business_id}/credits/deduct",
                    headers={"X-Agent-Key": settings.PLATFORM_API_KEY},
                    json={
                        "amount": task.actual_credits or task.estimated_credits,
                        "description": f"Autonomous run task: {task.title}",
                        "reference_id": str(task.id),
                    },
                )
                resp.raise_for_status()
        except Exception as exc:
            logger.warning(
                "credit_deduction_failed", extra={"task_id": str(task.id)}, exc_info=True
            )
            raise RuntimeError("Could not deduct credits for the completed run task") from exc


class LLMArtifactCapability:
    """Generate a reviewable artifact based on actual business/task data."""

    def __init__(self, llm) -> None:
        self._llm = llm

    async def execute(self, task: RunTask, context: BusinessContext) -> dict:
        facts = context.model_dump(mode="json")
        prompt = (
            "Create a concise, useful draft artifact for the requested business task. "
            "Use only facts present in business_context; label assumptions and missing data. "
            "Do not claim any action was published, sent, researched live, or completed externally. "
            "Return valid JSON with keys artifact_type, title, content, evidence, open_questions.\n"
            f"Task type: {task.task_type.value}\nTitle: {task.title}\n"
            f"Description: {task.description}\nInput: {json.dumps(task.input_data, ensure_ascii=False)}\n"
            f"Business context: {json.dumps(facts, ensure_ascii=False)}"
        )
        raw = await self._llm.complete([{"role": "user", "content": prompt}])
        try:
            result = json.loads(raw)
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError("Run engine model returned invalid artifact JSON") from exc
        if not isinstance(result, dict) or not isinstance(result.get("content"), (str, list, dict)):
            raise ValueError("Run engine model returned an incomplete artifact")
        result["status"] = "draft_for_review"
        return result

    async def deliver(self, task: RunTask, result: dict, business_id=None) -> None:
        # External publication/sending requires a connected channel and explicit integration.
        result["delivery_status"] = "not_published"
