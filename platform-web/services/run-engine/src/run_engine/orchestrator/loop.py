from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Protocol
from uuid import UUID

from run_engine.domain.permissions import needs_approval
from run_engine.domain.run import (
    BusinessContext,
    Run,
    RunEvent,
    RunEventType,
    RunStatus,
    RunTask,
    TaskStatus,
)
from run_engine.events.publisher import EventPublisher
from run_engine.orchestrator.executor import TaskExecutor
from run_engine.orchestrator.planner import TaskPlanner
from run_engine.persistence.repository import RunRepository

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ContextGatherer(Protocol):
    async def gather(self, business_id: UUID) -> BusinessContext: ...


class SimpleContextGatherer:
    """Default context gatherer pulling baseline data."""

    async def gather(self, business_id: UUID) -> BusinessContext:
        return BusinessContext(
            business_id=business_id,
            business_name="Cre8ive Studio Client",
            business_description="A modern African brand expanding into digital retail and creative services.",
            industry="Creative Services & E-commerce",
            target_audience="Digital entrepreneurs, founders, and forward-thinking consumers",
            has_brand=True,
            brand_summary="Complete brand guidelines, warm charcoal and orange identity, modern typography.",
            has_website=True,
            website_url="https://client.cre8ivedistrict.com",
            website_page_count=3,
            website_lighthouse_score=94.0,
            connected_socials=["instagram", "linkedin"],
            recent_posts_count=4,
            social_engagement_summary="Growing steadily. High engagement on brand story carousels.",
            outreach_emails_sent=12,
            outreach_reply_rate=0.25,
            total_revenue=250000.0,
            total_orders=5,
            known_competitors=["Local agency studios", "Global template platforms"],
        )


class PlatformContextGatherer:
    def __init__(self, api_url: str, api_key: str) -> None:
        self._api_url = api_url.rstrip("/")
        self._api_key = api_key

    async def gather(self, business_id: UUID) -> BusinessContext:
        import httpx
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{self._api_url}/api/internal/businesses/{business_id}/agent-context",
                headers={"X-Agent-Key": self._api_key},
            )
            response.raise_for_status()
            return BusinessContext.model_validate(response.json())


class AgentLoop:
    """The core autonomous agent loop that executes Abija's continuous background work."""

    def __init__(
        self,
        planner: TaskPlanner,
        executor: TaskExecutor,
        repository: RunRepository,
        event_publisher: EventPublisher,
        context_gatherer: ContextGatherer | None = None,
        *,
        iteration_delay: float = 1.0,
        approval_timeout: float = 86400.0,
        brief_interval_hours: float = 6.0,
    ) -> None:
        self._planner = planner
        self._executor = executor
        self._repo = repository
        self._events = event_publisher
        self._context = context_gatherer or SimpleContextGatherer()
        self._iteration_delay = iteration_delay
        self._approval_timeout = approval_timeout
        self._brief_interval = timedelta(hours=brief_interval_hours)
        self._approval_futures: dict[UUID, asyncio.Future[bool]] = {}
        self._last_brief: datetime | None = None
        self._active_tasks: dict[UUID, asyncio.Task] = {}

    def is_running(self, run_id: UUID) -> bool:
        task = self._active_tasks.get(run_id)
        return task is not None and not task.done()

    def recover_active_runs(self, runs: list[Run]) -> int:
        """Schedule persisted non-terminal runs after repository initialization."""
        recovered = 0
        for run in runs:
            if run.status not in {RunStatus.STARTING, RunStatus.PLANNING, RunStatus.EXECUTING, RunStatus.WAITING_APPROVAL}:
                continue
            self.spawn(run)
            recovered += 1
        return recovered

    async def shutdown(self) -> None:
        """Stop local tasks while leaving their persisted states recoverable."""
        tasks = [task for task in self._active_tasks.values() if not task.done()]
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def start(self, run: Run) -> None:
        claimed = await self._repo.claim_run(run.id)
        if not claimed:
            logger.info("Run %s is already owned by another worker.", run.id)
            return
        try:
            run = await self._repo.get_run(run.id) or run
            if run.status in {RunStatus.PAUSED, RunStatus.CANCELLED, RunStatus.COMPLETED, RunStatus.FAILED}:
                return
            await self._recover_interrupted_tasks(run)
            run = await self._repo.get_run(run.id) or run
            if run.status in {RunStatus.PAUSED, RunStatus.CANCELLED, RunStatus.COMPLETED, RunStatus.FAILED}:
                return
            run.status = RunStatus.STARTING
            run.started_at = run.started_at or utc_now()
            await self._repo.update_run(run)
            await self._emit(run, RunEventType.RUN_STARTED, "Abija has started or resumed autonomous work.")
            await self._run_loop(run)
        except asyncio.CancelledError:
            logger.info("Run %s interrupted; persisted progress will be recovered.", run.id)
            current = await self._repo.get_run(run.id)
            if current and current.status not in {RunStatus.PAUSED, RunStatus.CANCELLED, RunStatus.COMPLETED, RunStatus.FAILED}:
                if current.status != RunStatus.WAITING_APPROVAL:
                    current.status = RunStatus.STARTING
                await self._repo.update_run(current)
        except Exception as exc:
            logger.exception("Run %s encountered an error: %s", run.id, exc)
            run.status = RunStatus.FAILED
            run.completed_at = utc_now()
            run.completion_reason = str(exc)
            await self._repo.update_run(run)
            await self._emit(run, RunEventType.RUN_FAILED, f"Run encountered error: {exc}")
        finally:
            await self._repo.release_run(run.id)

    def spawn(self, run: Run) -> asyncio.Task:
        """Spawn background asyncio task for this run."""
        current = self._active_tasks.get(run.id)
        if current is not None and not current.done():
            return current
        task = asyncio.create_task(self.start(run))
        self._active_tasks[run.id] = task
        return task

    async def _recover_interrupted_tasks(self, run: Run) -> None:
        """Finish persisted task output or approval work before planning again."""
        context: BusinessContext | None = None
        for task in run.tasks:
            if task.status == TaskStatus.EXECUTING:
                if not task.output_data:
                    task.status = TaskStatus.FAILED
                    task.error_message = "Run engine restarted before this task produced a saved result."
                    task.completed_at = utc_now()
                    await self._repo.update_task(task)
                    await self._emit(run, RunEventType.TASK_FAILED, f"Interrupted task failed: {task.title}", task_id=task.id)
                    continue
                if needs_approval(task, run.permissions):
                    task.status = TaskStatus.WAITING_APPROVAL
                    run.status = RunStatus.WAITING_APPROVAL
                    await self._repo.update_task(task)
                    await self._repo.update_run(run)
                    await self._emit(run, RunEventType.APPROVAL_REQUESTED, f"Approval is still needed: {task.title}", task_id=task.id)
                else:
                    task.status = TaskStatus.APPROVED
                    await self._repo.update_task(task)

            if task.status == TaskStatus.WAITING_APPROVAL:
                run.status = RunStatus.WAITING_APPROVAL
                await self._repo.update_run(run)
                approved = await self._wait_for_approval(task)
                if not approved:
                    task.status = TaskStatus.REJECTED
                    task.completed_at = utc_now()
                    await self._repo.update_task(task)
                    await self._emit(run, RunEventType.TASK_REJECTED, f"Declined: {task.title}", task_id=task.id)
                    continue
                task.status = TaskStatus.APPROVED
                await self._repo.update_task(task)
                await self._emit(run, RunEventType.TASK_APPROVED, f"Approved: {task.title}", task_id=task.id)

            if task.status == TaskStatus.APPROVED:
                if context is None:
                    context = await self._context.gather(run.business_id)
                run.status = RunStatus.EXECUTING
                await self._complete_task_delivery(run, task, context)

        if run.status == RunStatus.WAITING_APPROVAL:
            run.status = RunStatus.STARTING
            await self._repo.update_run(run)

    async def _complete_task_delivery(
        self, run: Run, task: RunTask, context: BusinessContext
    ) -> bool:
        try:
            await self._executor.deliver(task, task.output_data, context.business_id)
        except Exception as exc:
            logger.warning("Delivery error for task %s: %s", task.id, exc)
            task.status = TaskStatus.FAILED
            task.error_message = f"Delivery failed: {exc}"
            task.completed_at = utc_now()
            await self._repo.update_task(task)
            await self._emit(run, RunEventType.TASK_FAILED, f"Task failed: {task.title}", task_id=task.id)
            return False
        task.status = TaskStatus.COMPLETED
        task.completed_at = utc_now()
        run.budget.charge(task.actual_credits)
        await self._repo.complete_task(run, task)
        await self._emit(
            run, RunEventType.TASK_COMPLETED,
            f"Completed: {task.title} (used {task.actual_credits} credits)", task_id=task.id,
        )
        return True

    async def _run_loop(self, run: Run) -> None:
        while True:
            # Refresh state
            refreshed = await self._repo.get_run(run.id)
            if refreshed is None:
                return
            run = refreshed

            # Termination checks
            if run.status in (RunStatus.PAUSED, RunStatus.CANCELLED, RunStatus.COMPLETED, RunStatus.FAILED):
                logger.info("Run %s halted with status: %s", run.id, run.status)
                return

            if run.budget.exhausted:
                await self._complete(
                    run, "Credit budget exhausted — Abija has completed all work within your credit limit."
                )
                return

            if run.iteration >= run.max_iterations:
                await self._complete(run, f"Reached maximum iteration limit of {run.max_iterations}.")
                return

            # 1. OBSERVE: Gather context
            context = await self._context.gather(run.business_id)

            # 2. PLAN: Formulate next actions
            run.status = RunStatus.PLANNING
            await self._repo.update_run(run)

            completed_tasks = [t for t in run.tasks if t.status == TaskStatus.COMPLETED]
            planned_tasks = await self._planner.plan_next_tasks(
                context=context,
                run=run,
                completed_tasks=completed_tasks,
            )

            if not planned_tasks:
                await self._complete(
                    run, "No further immediate tasks planned — all current objectives addressed."
                )
                return

            # 3. EXECUTE: Walk planned tasks
            for task in planned_tasks:
                # Check if run paused while planning
                refreshed = await self._repo.get_run(run.id)
                if refreshed and refreshed.status in (RunStatus.PAUSED, RunStatus.CANCELLED):
                    return

                if run.budget.exhausted:
                    await self._emit(run, RunEventType.BUDGET_EXHAUSTED, "Credit budget fully exhausted.")
                    break

                if not run.budget.can_afford(task.estimated_credits):
                    task.status = TaskStatus.SKIPPED
                    await self._repo.update_task(task)
                    await self._emit(
                        run,
                        RunEventType.TASK_SKIPPED,
                        f"Skipped '{task.title}': requires {task.estimated_credits} credits ({run.budget.remaining} remaining).",
                        task_id=task.id,
                    )
                    continue

                task.run_id = run.id
                task = await self._repo.add_task(task)
                run.tasks.append(task)
                await self._emit(
                    run, RunEventType.TASK_PLANNED, f"Planned task: {task.title}", task_id=task.id
                )

                # Execute capability
                run.status = RunStatus.EXECUTING
                task.status = TaskStatus.EXECUTING
                task.started_at = utc_now()
                await self._repo.update_run(run)
                await self._repo.update_task(task)
                await self._emit(
                    run, RunEventType.TASK_EXECUTING, f"Executing: {task.title}", task_id=task.id
                )

                try:
                    result = await self._executor.execute(task, context)
                    task.output_data = result
                    task.actual_credits = task.estimated_credits
                    await self._repo.update_task(task)
                except Exception as exc:
                    logger.warning("Task %s failed execution: %s", task.id, exc)
                    task.status = TaskStatus.FAILED
                    task.error_message = str(exc)
                    task.completed_at = utc_now()
                    await self._repo.update_task(task)
                    await self._emit(
                        run,
                        RunEventType.TASK_FAILED,
                        f"Task failed: {task.title} ({exc})",
                        task_id=task.id,
                    )
                    continue

                # 4. APPROVAL CHECK
                if needs_approval(task, run.permissions):
                    task.status = TaskStatus.WAITING_APPROVAL
                    run.status = RunStatus.WAITING_APPROVAL
                    await self._repo.update_task(task)
                    await self._repo.update_run(run)
                    await self._emit(
                        run,
                        RunEventType.APPROVAL_REQUESTED,
                        f"Awaiting your approval: {task.title}",
                        task_id=task.id,
                    )

                    approved = await self._wait_for_approval(task)
                    if not approved:
                        task.status = TaskStatus.REJECTED
                        task.completed_at = utc_now()
                        await self._repo.update_task(task)
                        await self._emit(
                            run,
                            RunEventType.TASK_REJECTED,
                            f"Declined: {task.title}",
                            task_id=task.id,
                        )
                        continue

                    task.status = TaskStatus.APPROVED
                    await self._repo.update_task(task)
                    run.status = RunStatus.EXECUTING
                    await self._repo.update_run(run)
                    await self._emit(
                        run, RunEventType.TASK_APPROVED, f"Approved: {task.title}", task_id=task.id
                    )
                else:
                    task.status = TaskStatus.APPROVED
                    await self._repo.update_task(task)

                # 5. DELIVER
                if not await self._complete_task_delivery(run, task, context):
                    continue

                # 6. RECORD & CHARGE
                # Budget alerts
                if run.budget.used >= run.budget.total * 0.8 and not run.budget.exhausted:
                    pct = int((run.budget.used / run.budget.total) * 100)
                    await self._emit(
                        run,
                        RunEventType.BUDGET_WARNING,
                        f"Budget notice: {pct}% used ({run.budget.remaining} credits remaining).",
                    )

            # 7. PERIODIC BRIEF
            if self._should_brief():
                brief = await self._planner.generate_brief(run, context)
                await self._emit(run, RunEventType.BRIEF_SENT, brief)
                self._last_brief = utc_now()

            run.iteration += 1
            await self._repo.update_run(run)

            # Yield to event loop
            await asyncio.sleep(self._iteration_delay)

    async def approve_task(self, task_id: UUID, approved: bool) -> bool:
        future = self._approval_futures.get(task_id)
        if future and not future.done():
            future.set_result(approved)
            return True
        return False

    async def pause(self, run: Run) -> None:
        run.status = RunStatus.PAUSED
        run.paused_at = utc_now()
        await self._repo.update_run(run)
        await self._emit(run, RunEventType.RUN_PAUSED, "Abija paused the autonomous run.")

    async def resume(self, run: Run) -> None:
        run.status = RunStatus.STARTING
        run.paused_at = None
        await self._repo.update_run(run)
        await self._emit(run, RunEventType.RUN_RESUMED, "Abija resumed the autonomous run.")
        self.spawn(run)

    async def cancel(self, run: Run) -> None:
        run.status = RunStatus.CANCELLED
        run.completed_at = utc_now()
        run.completion_reason = "Cancelled by user."
        task = self._active_tasks.get(run.id)
        if task and not task.done():
            task.cancel()
        await self._repo.update_run(run)
        await self._emit(run, RunEventType.RUN_PAUSED, "Run cancelled.")

    async def _wait_for_approval(self, task: RunTask) -> bool:
        persisted = await self._repo.get_task(task.id)
        if persisted and persisted.status in {TaskStatus.APPROVED, TaskStatus.REJECTED}:
            return persisted.status == TaskStatus.APPROVED
        loop = asyncio.get_running_loop()
        future: asyncio.Future[bool] = loop.create_future()
        self._approval_futures[task.id] = future
        deadline = loop.time() + self._approval_timeout
        try:
            while True:
                remaining = deadline - loop.time()
                if remaining <= 0:
                    logger.info("Approval timed out for task %s", task.id)
                    return False
                try:
                    return await asyncio.wait_for(asyncio.shield(future), timeout=min(remaining, 1.0))
                except asyncio.TimeoutError:
                    persisted = await self._repo.get_task(task.id)
                    if persisted and persisted.status in {TaskStatus.APPROVED, TaskStatus.REJECTED}:
                        return persisted.status == TaskStatus.APPROVED
        finally:
            self._approval_futures.pop(task.id, None)

    async def _complete(self, run: Run, reason: str) -> None:
        run.status = RunStatus.COMPLETED
        run.completed_at = utc_now()
        run.completion_reason = reason
        await self._repo.update_run(run)
        await self._emit(run, RunEventType.RUN_COMPLETED, reason)

    def _should_brief(self) -> bool:
        if self._last_brief is None:
            return True
        return utc_now() - self._last_brief >= self._brief_interval

    async def _emit(
        self,
        run: Run,
        event_type: RunEventType,
        message: str,
        *,
        task_id: UUID | None = None,
    ) -> None:
        event = RunEvent(
            run_id=run.id,
            event_type=event_type,
            message=message,
            task_id=task_id,
        )
        await self._repo.add_event(event)
        run.events.append(event)
        await self._events.publish(event)
        logger.info("[Run %s] %s: %s", run.id, event_type.value, message)
