from uuid import uuid4
import pytest
from run_engine.domain.run import (
    BusinessContext,
    CreditBudget,
    Run,
    RunTask,
    TaskStatus,
    TaskType,
)
from run_engine.orchestrator.planner import TaskPlanner
from run_engine.providers.llm import StubPlanner


@pytest.mark.asyncio
async def test_planner_generates_tasks():
    llm = StubPlanner()
    planner = TaskPlanner(llm)

    context = BusinessContext(
        business_id=uuid4(),
        business_name="Lagos Artisan Goods",
        business_description="Handcrafted leather items made in Nigeria.",
        industry="Retail & Fashion",
    )
    run = Run(
        business_id=context.business_id,
        user_id=uuid4(),
        budget=CreditBudget(total=50),
        goal="Launch initial store",
    )

    tasks = await planner.plan_next_tasks(context, run, [])
    assert len(tasks) == 3
    assert tasks[0].task_type == TaskType.BRAND_IMPROVEMENT
    assert tasks[0].estimated_credits == 10
    assert tasks[0].priority == 1


@pytest.mark.asyncio
async def test_planner_generates_executive_brief():
    llm = StubPlanner()
    planner = TaskPlanner(llm)

    context = BusinessContext(
        business_id=uuid4(),
        business_name="Lagos Artisan Goods",
        business_description="Handcrafted leather items made in Nigeria.",
    )
    run = Run(
        business_id=context.business_id,
        user_id=uuid4(),
        budget=CreditBudget(total=50, used=25),
        iteration=2,
    )

    brief = await planner.generate_brief(run, context)
    assert "Abija" in brief
    assert "executive brief" in brief.lower()
