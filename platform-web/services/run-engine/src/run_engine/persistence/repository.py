from __future__ import annotations

import copy
from datetime import datetime
from typing import Protocol
from uuid import UUID

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


class RunRepository(Protocol):
    async def create_run(self, run: Run) -> Run: ...
    async def get_run(self, run_id: UUID) -> Run | None: ...
    async def update_run(self, run: Run) -> Run: ...
    async def add_task(self, task: RunTask) -> RunTask: ...
    async def update_task(self, task: RunTask) -> RunTask: ...
    async def get_task(self, task_id: UUID) -> RunTask | None: ...
    async def get_pending_approval_tasks(self, run_id: UUID) -> list[RunTask]: ...
    async def add_event(self, event: RunEvent) -> RunEvent: ...
    async def get_events(self, run_id: UUID, since: datetime | None = None) -> list[RunEvent]: ...
    async def get_active_runs(self, business_id: UUID) -> list[Run]: ...
    async def get_all_active_runs(self) -> list[Run]: ...
    async def claim_run(self, run_id: UUID) -> bool: ...
    async def release_run(self, run_id: UUID) -> None: ...
    async def complete_task(self, run: Run, task: RunTask) -> None: ...


class InMemoryRunRepository:
    def __init__(self) -> None:
        self._runs: dict[UUID, Run] = {}
        self._tasks: dict[UUID, RunTask] = {}
        self._events: dict[UUID, list[RunEvent]] = {}
        self._claimed_runs: set[UUID] = set()

    async def create_run(self, run: Run) -> Run:
        self._runs[run.id] = copy.deepcopy(run)
        if run.id not in self._events:
            self._events[run.id] = []
        return copy.deepcopy(run)

    async def get_run(self, run_id: UUID) -> Run | None:
        run = self._runs.get(run_id)
        if run is None:
            return None
        # hydrate with latest tasks and events
        run_copy = copy.deepcopy(run)
        run_copy.tasks = [copy.deepcopy(t) for t in self._tasks.values() if t.run_id == run_id]
        run_copy.events = copy.deepcopy(self._events.get(run_id, []))
        return run_copy

    async def update_run(self, run: Run) -> Run:
        self._runs[run.id] = copy.deepcopy(run)
        return copy.deepcopy(run)

    async def add_task(self, task: RunTask) -> RunTask:
        self._tasks[task.id] = copy.deepcopy(task)
        if task.run_id in self._runs:
            existing = [t for t in self._runs[task.run_id].tasks if t.id == task.id]
            if not existing:
                self._runs[task.run_id].tasks.append(copy.deepcopy(task))
        return copy.deepcopy(task)

    async def update_task(self, task: RunTask) -> RunTask:
        self._tasks[task.id] = copy.deepcopy(task)
        if task.run_id in self._runs:
            for idx, existing in enumerate(self._runs[task.run_id].tasks):
                if existing.id == task.id:
                    self._runs[task.run_id].tasks[idx] = copy.deepcopy(task)
                    break
        return copy.deepcopy(task)

    async def get_task(self, task_id: UUID) -> RunTask | None:
        task = self._tasks.get(task_id)
        return copy.deepcopy(task) if task else None

    async def get_pending_approval_tasks(self, run_id: UUID) -> list[RunTask]:
        return [
            copy.deepcopy(t)
            for t in self._tasks.values()
            if t.run_id == run_id and t.status == TaskStatus.WAITING_APPROVAL
        ]

    async def add_event(self, event: RunEvent) -> RunEvent:
        if event.run_id not in self._events:
            self._events[event.run_id] = []
        self._events[event.run_id].append(copy.deepcopy(event))
        if event.run_id in self._runs:
            self._runs[event.run_id].events.append(copy.deepcopy(event))
        return copy.deepcopy(event)

    async def get_events(self, run_id: UUID, since: datetime | None = None) -> list[RunEvent]:
        events = self._events.get(run_id, [])
        if since is None:
            return [copy.deepcopy(e) for e in events]
        return [copy.deepcopy(e) for e in events if e.created_at > since]

    async def get_active_runs(self, business_id: UUID) -> list[Run]:
        active_statuses = {
            RunStatus.STARTING,
            RunStatus.PLANNING,
            RunStatus.EXECUTING,
            RunStatus.WAITING_APPROVAL,
        }
        active = []
        for run in self._runs.values():
            if run.business_id == business_id and run.status in active_statuses:
                active.append(await self.get_run(run.id))
        return [r for r in active if r is not None]

    async def get_all_active_runs(self) -> list[Run]:
        active = []
        for run in self._runs.values():
            if run.status in {
                RunStatus.STARTING,
                RunStatus.PLANNING,
                RunStatus.EXECUTING,
                RunStatus.WAITING_APPROVAL,
            }:
                current = await self.get_run(run.id)
                if current is not None:
                    active.append(current)
        return active

    async def claim_run(self, run_id: UUID) -> bool:
        if run_id in self._claimed_runs:
            return False
        self._claimed_runs.add(run_id)
        return True

    async def release_run(self, run_id: UUID) -> None:
        self._claimed_runs.discard(run_id)

    async def complete_task(self, run: Run, task: RunTask) -> None:
        await self.update_task(task)
        await self.update_run(run)


class PostgresRunRepository:
    def __init__(self, database_url: str) -> None:
        from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
        from sqlalchemy.pool import NullPool

        self._engine = create_async_engine(database_url, echo=False)
        # Advisory lock connections stay open for the run lifetime. Keep them
        # out of the query pool so active runs cannot exhaust it.
        self._lease_engine = create_async_engine(database_url, echo=False, poolclass=NullPool)
        self._session_factory = async_sessionmaker(self._engine, expire_on_commit=False)
        self._lease_connections = {}
        self._local_leases: set[UUID] = set()

    async def close(self) -> None:
        await self._engine.dispose()
        await self._lease_engine.dispose()

    async def initialize(self) -> None:
        from run_engine.persistence.models import Base

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def create_run(self, run: Run) -> Run:
        from run_engine.persistence.models import RunModel

        async with self._session_factory() as session:
            model = RunModel(
                id=run.id,
                business_id=run.business_id,
                user_id=run.user_id,
                status=run.status.value,
                goal=run.goal,
                budget_total=run.budget.total,
                budget_used=run.budget.used,
                permissions_json=run.permissions.model_dump(),
                iteration=run.iteration,
                max_iterations=run.max_iterations,
                created_at=run.created_at,
                started_at=run.started_at,
                paused_at=run.paused_at,
                completed_at=run.completed_at,
                completion_reason=run.completion_reason,
            )
            session.add(model)
            await session.commit()
            return await self.get_run(run.id)  # type: ignore

    async def get_run(self, run_id: UUID) -> Run | None:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        from run_engine.persistence.models import RunModel

        async with self._session_factory() as session:
            stmt = (
                select(RunModel)
                .where(RunModel.id == run_id)
                .options(selectinload(RunModel.tasks), selectinload(RunModel.events))
            )
            result = await session.execute(stmt)
            m = result.scalar_one_or_none()
            if m is None:
                return None
            return self._model_to_run(m)

    async def update_run(self, run: Run) -> Run:
        from run_engine.persistence.models import RunModel

        async with self._session_factory() as session:
            m = await session.get(RunModel, run.id)
            if m:
                m.status = run.status.value
                m.goal = run.goal
                m.budget_total = run.budget.total
                m.budget_used = run.budget.used
                m.permissions_json = run.permissions.model_dump()
                m.iteration = run.iteration
                m.max_iterations = run.max_iterations
                m.started_at = run.started_at
                m.paused_at = run.paused_at
                m.completed_at = run.completed_at
                m.completion_reason = run.completion_reason
                await session.commit()
            return await self.get_run(run.id) or run

    async def add_task(self, task: RunTask) -> RunTask:
        from run_engine.persistence.models import RunTaskModel

        async with self._session_factory() as session:
            model = RunTaskModel(
                id=task.id,
                run_id=task.run_id,
                task_type=task.task_type.value,
                status=task.status.value,
                title=task.title,
                description=task.description,
                reasoning=task.reasoning,
                priority=task.priority,
                estimated_credits=task.estimated_credits,
                actual_credits=task.actual_credits,
                channel=task.channel,
                input_data=task.input_data,
                output_data=task.output_data,
                error_message=task.error_message,
                created_at=task.created_at,
                started_at=task.started_at,
                completed_at=task.completed_at,
            )
            session.add(model)
            await session.commit()
            return task

    async def update_task(self, task: RunTask) -> RunTask:
        from run_engine.persistence.models import RunTaskModel

        async with self._session_factory() as session:
            m = await session.get(RunTaskModel, task.id)
            if m:
                m.status = task.status.value
                m.actual_credits = task.actual_credits
                m.output_data = task.output_data
                m.error_message = task.error_message
                m.started_at = task.started_at
                m.completed_at = task.completed_at
                await session.commit()
            return task

    async def get_task(self, task_id: UUID) -> RunTask | None:
        from run_engine.persistence.models import RunTaskModel

        async with self._session_factory() as session:
            m = await session.get(RunTaskModel, task_id)
            if m is None:
                return None
            return self._model_to_task(m)

    async def get_pending_approval_tasks(self, run_id: UUID) -> list[RunTask]:
        from sqlalchemy import select

        from run_engine.persistence.models import RunTaskModel

        async with self._session_factory() as session:
            stmt = select(RunTaskModel).where(
                RunTaskModel.run_id == run_id,
                RunTaskModel.status == TaskStatus.WAITING_APPROVAL.value,
            )
            result = await session.execute(stmt)
            return [self._model_to_task(m) for m in result.scalars().all()]

    async def add_event(self, event: RunEvent) -> RunEvent:
        from run_engine.persistence.models import RunEventModel

        async with self._session_factory() as session:
            model = RunEventModel(
                id=event.id,
                run_id=event.run_id,
                event_type=event.event_type.value,
                message=event.message,
                task_id=event.task_id,
                metadata_json=event.metadata,
                created_at=event.created_at,
            )
            session.add(model)
            await session.commit()
            return event

    async def get_events(self, run_id: UUID, since: datetime | None = None) -> list[RunEvent]:
        from sqlalchemy import select

        from run_engine.persistence.models import RunEventModel

        async with self._session_factory() as session:
            stmt = select(RunEventModel).where(RunEventModel.run_id == run_id)
            if since:
                stmt = stmt.where(RunEventModel.created_at > since)
            stmt = stmt.order_by(RunEventModel.created_at.asc())
            result = await session.execute(stmt)
            return [self._model_to_event(m) for m in result.scalars().all()]

    async def get_active_runs(self, business_id: UUID) -> list[Run]:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        from run_engine.persistence.models import RunModel

        active_statuses = [
            RunStatus.STARTING.value,
            RunStatus.PLANNING.value,
            RunStatus.EXECUTING.value,
            RunStatus.WAITING_APPROVAL.value,
        ]
        async with self._session_factory() as session:
            stmt = (
                select(RunModel)
                .where(RunModel.business_id == business_id, RunModel.status.in_(active_statuses))
                .options(selectinload(RunModel.tasks), selectinload(RunModel.events))
            )
            result = await session.execute(stmt)
            return [self._model_to_run(m) for m in result.scalars().all()]

    async def get_all_active_runs(self) -> list[Run]:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        from run_engine.persistence.models import RunModel

        statuses = [
            RunStatus.STARTING.value,
            RunStatus.PLANNING.value,
            RunStatus.EXECUTING.value,
            RunStatus.WAITING_APPROVAL.value,
        ]
        async with self._session_factory() as session:
            stmt = (
                select(RunModel)
                .where(RunModel.status.in_(statuses))
                .options(selectinload(RunModel.tasks), selectinload(RunModel.events))
            )
            result = await session.execute(stmt)
            return [self._model_to_run(model) for model in result.scalars().all()]

    async def claim_run(self, run_id: UUID) -> bool:
        if run_id in self._lease_connections or run_id in self._local_leases:
            return False
        if self._engine.dialect.name != "postgresql":
            self._local_leases.add(run_id)
            return True

        from sqlalchemy import text

        connection = await self._lease_engine.connect()
        try:
            result = await connection.execute(
                text("SELECT pg_try_advisory_lock(49273, hashtext(:run_id))"),
                {"run_id": str(run_id)},
            )
            acquired = bool(result.scalar_one())
            await connection.commit()
            if not acquired:
                await connection.close()
                return False
            self._lease_connections[run_id] = connection
            return True
        except Exception:
            await connection.close()
            raise

    async def release_run(self, run_id: UUID) -> None:
        connection = self._lease_connections.pop(run_id, None)
        if connection is None:
            self._local_leases.discard(run_id)
            return
        from sqlalchemy import text

        try:
            await connection.execute(
                text("SELECT pg_advisory_unlock(49273, hashtext(:run_id))"),
                {"run_id": str(run_id)},
            )
            await connection.commit()
        finally:
            await connection.close()

    async def complete_task(self, run: Run, task: RunTask) -> None:
        from run_engine.persistence.models import RunModel, RunTaskModel

        async with self._session_factory() as session:
            run_model = await session.get(RunModel, run.id)
            task_model = await session.get(RunTaskModel, task.id)
            if run_model is None or task_model is None:
                raise LookupError("Run or task disappeared before completion was committed")
            run_model.status = run.status.value
            run_model.budget_total = run.budget.total
            run_model.budget_used = run.budget.used
            run_model.iteration = run.iteration
            run_model.started_at = run.started_at
            run_model.paused_at = run.paused_at
            run_model.completed_at = run.completed_at
            run_model.completion_reason = run.completion_reason
            task_model.status = task.status.value
            task_model.actual_credits = task.actual_credits
            task_model.output_data = task.output_data
            task_model.error_message = task.error_message
            task_model.completed_at = task.completed_at
            await session.commit()

    def _model_to_task(self, m) -> RunTask:
        return RunTask(
            id=m.id,
            run_id=m.run_id,
            task_type=TaskType(m.task_type),
            status=TaskStatus(m.status),
            title=m.title,
            description=m.description,
            reasoning=m.reasoning,
            priority=m.priority,
            estimated_credits=m.estimated_credits,
            actual_credits=m.actual_credits,
            channel=m.channel,
            input_data=dict(m.input_data or {}),
            output_data=dict(m.output_data or {}),
            error_message=m.error_message,
            created_at=m.created_at,
            started_at=m.started_at,
            completed_at=m.completed_at,
        )

    def _model_to_event(self, m) -> RunEvent:
        return RunEvent(
            id=m.id,
            run_id=m.run_id,
            event_type=RunEventType(m.event_type),
            message=m.message,
            task_id=m.task_id,
            metadata=dict(m.metadata_json or {}),
            created_at=m.created_at,
        )

    def _model_to_run(self, m) -> Run:
        tasks = [self._model_to_task(t) for t in (m.tasks or [])]
        events = [self._model_to_event(e) for e in (m.events or [])]
        perms = ChannelPermissions(**(m.permissions_json or {}))
        budget = CreditBudget(total=m.budget_total, used=m.budget_used)
        return Run(
            id=m.id,
            business_id=m.business_id,
            user_id=m.user_id,
            status=RunStatus(m.status),
            budget=budget,
            permissions=perms,
            goal=m.goal,
            tasks=tasks,
            events=events,
            iteration=m.iteration,
            max_iterations=m.max_iterations,
            created_at=m.created_at,
            started_at=m.started_at,
            paused_at=m.paused_at,
            completed_at=m.completed_at,
            completion_reason=m.completion_reason,
        )
