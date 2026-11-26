from __future__ import annotations

from datetime import UTC, datetime

from run_engine.domain.run import Run, TaskStatus


def format_brief_summary(run: Run) -> dict:
    completed = [t for t in run.tasks if t.status == TaskStatus.COMPLETED]
    by_type: dict[str, int] = {}
    for t in completed:
        by_type[t.task_type.value] = by_type.get(t.task_type.value, 0) + 1

    return {
        "business_id": str(run.business_id),
        "run_id": str(run.id),
        "iteration": run.iteration,
        "credits_used": run.budget.used,
        "credits_remaining": run.budget.remaining,
        "tasks_completed": len(completed),
        "tasks_by_type": by_type,
        "latest_tasks": [
            {
                "id": str(t.id),
                "title": t.title,
                "type": t.task_type.value,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            }
            for t in completed[-5:]
        ],
        "generated_at": datetime.now(UTC).isoformat(),
    }
