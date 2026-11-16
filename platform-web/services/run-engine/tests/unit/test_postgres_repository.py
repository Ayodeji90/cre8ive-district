import pytest
from uuid import uuid4
from run_engine.domain.run import (
    ChannelPermissions,
    CreditBudget,
    Run,
    RunEvent,
    RunEventType,
    RunStatus,
    RunTask,
    TaskStatus,
    TaskType,
)
from run_engine.persistence.repository import PostgresRunRepository


@pytest.mark.asyncio
async def test_postgres_repo_lifecycle(tmp_path):
    repo = PostgresRunRepository(f"sqlite+aiosqlite:///{tmp_path / 'run-engine-test.db'}")
    try:
        await _exercise_repo_lifecycle(repo)
    finally:
        await repo.close()


async def _exercise_repo_lifecycle(repo):
    await repo.initialize()

    business_id = uuid4()
    user_id = uuid4()
    run = Run(
        business_id=business_id,
        user_id=user_id,
        budget=CreditBudget(total=100, used=0),
        permissions=ChannelPermissions(),
        goal="Test goal for growth",
    )

    created = await repo.create_run(run)
    assert created.id == run.id
    assert created.business_id == business_id
    assert created.goal == "Test goal for growth"

    # Fetch
    fetched = await repo.get_run(run.id)
    assert fetched is not None
    assert fetched.id == run.id
    assert fetched.status == RunStatus.STARTING

    # Update run status
    fetched.status = RunStatus.EXECUTING
    fetched.budget.used = 15
    updated = await repo.update_run(fetched)
    assert updated.status == RunStatus.EXECUTING
    assert updated.budget.used == 15

    # Add task
    task = RunTask(
        run_id=run.id,
        task_type=TaskType.BRAND_IMPROVEMENT,
        status=TaskStatus.WAITING_APPROVAL,
        title="Refine brand colors",
        description="Pick warmer accent colors",
    )
    added_task = await repo.add_task(task)
    assert added_task.id == task.id

    # Pending approval tasks
    pending = await repo.get_pending_approval_tasks(run.id)
    assert len(pending) == 1
    assert pending[0].id == task.id

    # Add event
    event = RunEvent(
        run_id=run.id,
        event_type=RunEventType.TASK_PLANNED,
        message="Planned brand color refinement",
        task_id=task.id,
    )
    await repo.add_event(event)

    events = await repo.get_events(run.id)
    assert len(events) == 1
    assert events[0].message == "Planned brand color refinement"

    # Active runs
    active = await repo.get_active_runs(business_id)
    assert len(active) == 1
    assert active[0].id == run.id
