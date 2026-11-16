import asyncio
from uuid import uuid4
import pytest

from run_engine.domain.run import (
    ApprovalMode,
    BusinessContext,
    ChannelPermissions,
    CreditBudget,
    Run,
    RunEventType,
    RunStatus,
    TaskStatus,
)
from run_engine.events.publisher import InMemoryEventPublisher
from run_engine.orchestrator.executor import TaskExecutor
from run_engine.orchestrator.loop import AgentLoop, SimpleContextGatherer
from run_engine.orchestrator.planner import TaskPlanner
from run_engine.persistence.repository import InMemoryRunRepository
from run_engine.providers.llm import StubPlanner


@pytest.mark.asyncio
async def test_agent_loop_autonomous_run_completes():
    repo = InMemoryRunRepository()
    events = InMemoryEventPublisher()
    planner = TaskPlanner(StubPlanner())
    executor = TaskExecutor()

    # Configure all channels to "on_its_own" so no human pause
    permissions = ChannelPermissions(
        website=ApprovalMode.ON_ITS_OWN,
        social_instagram=ApprovalMode.ON_ITS_OWN,
        outreach_email=ApprovalMode.ON_ITS_OWN,
    )

    loop = AgentLoop(
        planner=planner,
        executor=executor,
        repository=repo,
        event_publisher=events,
        context_gatherer=SimpleContextGatherer(),
        iteration_delay=0.01,
        approval_timeout=0.1,
    )

    run = Run(
        business_id=uuid4(),
        user_id=uuid4(),
        budget=CreditBudget(total=25),  # Enough for 1 round of 10+10+5 = 25 credits
        permissions=permissions,
        max_iterations=1,
    )
    saved = await repo.create_run(run)

    await loop.start(saved)

    finished = await repo.get_run(saved.id)
    assert finished is not None
    assert finished.status == RunStatus.COMPLETED
    assert finished.budget.used == 25
    assert finished.budget.remaining == 0
    assert len(finished.tasks) == 3
    assert all(t.status == TaskStatus.COMPLETED for t in finished.tasks)


@pytest.mark.asyncio
async def test_agent_loop_approval_flow():
    repo = InMemoryRunRepository()
    events = InMemoryEventPublisher()
    planner = TaskPlanner(StubPlanner())
    executor = TaskExecutor()

    # Website requires approval
    permissions = ChannelPermissions(
        website=ApprovalMode.ASK_FIRST,
        social_instagram=ApprovalMode.ON_ITS_OWN,
    )

    loop = AgentLoop(
        planner=planner,
        executor=executor,
        repository=repo,
        event_publisher=events,
        context_gatherer=SimpleContextGatherer(),
        iteration_delay=0.01,
        approval_timeout=2.0,
    )

    run = Run(
        business_id=uuid4(),
        user_id=uuid4(),
        budget=CreditBudget(total=50),
        permissions=permissions,
        max_iterations=1,
    )
    saved = await repo.create_run(run)

    # Spawn in background
    task_handle = loop.spawn(saved)

    # Give it a fraction of a second to plan and hit the website approval gate
    await asyncio.sleep(0.05)

    pending = await repo.get_pending_approval_tasks(saved.id)
    assert len(pending) >= 1
    target_task = pending[0]
    assert target_task.status == TaskStatus.WAITING_APPROVAL

    # Approve task externally
    unblocked = await loop.approve_task(target_task.id, approved=True)
    assert unblocked is True

    # Await completion of the 1 iteration
    await asyncio.wait_for(task_handle, timeout=2.0)

    finished = await repo.get_run(saved.id)
    assert finished is not None
    assert finished.status == RunStatus.COMPLETED
