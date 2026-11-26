from __future__ import annotations

from typing import Protocol

from run_engine.domain.run import BusinessContext, RunTask


class Capability(Protocol):
    """Protocol for a capability service that executes and delivers a specific task type."""

    async def execute(self, task: RunTask, context: BusinessContext) -> dict: ...
    async def deliver(self, task: RunTask, result: dict) -> None: ...
