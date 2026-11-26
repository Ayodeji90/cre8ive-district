from __future__ import annotations

from run_engine.domain.run import (
    ApprovalMode,
    ChannelPermissions,
    RunTask,
    TaskType,
)


def task_channel(task_type: TaskType, input_data: dict | None = None) -> str | None:
    data = input_data or {}
    match task_type:
        case TaskType.WEBSITE_IMPROVEMENT | TaskType.SEO_OPTIMIZATION:
            return "website"
        case TaskType.SOCIAL_POST:
            platform = str(data.get("platform", "instagram")).lower()
            return f"social_{platform}"
        case TaskType.OUTREACH_EMAIL:
            return "outreach_email"
        case TaskType.CONTENT_CREATION:
            return "content"
        case _:
            return None


def needs_approval(task: RunTask, permissions: ChannelPermissions) -> bool:
    channel = task.channel or task_channel(task.task_type, task.input_data)
    if channel is None:
        return False
    mode = permissions.mode_for(channel)
    return mode == ApprovalMode.ASK_FIRST
