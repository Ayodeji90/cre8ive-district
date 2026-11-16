from __future__ import annotations

from run_engine.domain.run import CreditBudget, TaskType

CREDIT_COSTS: dict[TaskType, int] = {
    TaskType.BRAND_IMPROVEMENT: 10,
    TaskType.WEBSITE_IMPROVEMENT: 10,
    TaskType.SOCIAL_POST: 5,
    TaskType.OUTREACH_EMAIL: 3,
    TaskType.COMPETITOR_RESEARCH: 10,
    TaskType.CONTENT_CREATION: 8,
    TaskType.SEO_OPTIMIZATION: 5,
    TaskType.ANALYTICS_REVIEW: 5,
}


def estimate_cost(task_type: TaskType) -> int:
    return CREDIT_COSTS.get(task_type, 5)


def affordable_task_types(budget: CreditBudget) -> list[TaskType]:
    return [
        task_type
        for task_type, cost in CREDIT_COSTS.items()
        if budget.can_afford(cost)
    ]
