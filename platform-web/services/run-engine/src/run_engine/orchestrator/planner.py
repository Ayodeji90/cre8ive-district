from __future__ import annotations

import json
import logging
from typing import Protocol

from run_engine.domain.credits import CREDIT_COSTS, affordable_task_types
from run_engine.domain.run import (
    BusinessContext,
    Run,
    RunTask,
    TaskStatus,
    TaskType,
)
from run_engine.providers.llm import PlannerLLM

logger = logging.getLogger(__name__)


PLANNING_SYSTEM_PROMPT = """You are Abija, the autonomous AI business partner at Cre8ive District.
You are running an autonomous session for a business. Your job is to decide
what the next most useful actions are to grow this business.

You think like a sharp, strategic business consultant who understands the
African and global market. You prioritize actions that create real impact:
building credibility, reaching customers, and generating revenue.

RULES:
- Plan 1 to 3 tasks maximum per iteration
- Never plan tasks the business can't benefit from (e.g. don't improve a website that doesn't exist yet)
- Prioritize by expected business impact, not by what's easiest
- Don't repeat the same task type consecutively unless clearly needed
- Stay within the credit budget
- If the business is brand new, focus on: brand → website → first social presence → outreach
- If the business is established, focus on: content → outreach → analytics → improvements
"""


PLANNING_USER_TEMPLATE = """## Business Context

**Name:** {business_name}
**Description:** {business_description}
**Industry:** {industry}
**Target Audience:** {target_audience}

### Current State
- Brand: {brand_status} {brand_summary}
- Website: {website_status} ({website_page_count} pages, Lighthouse: {lighthouse})
- Social accounts: {socials}
- Posts created: {recent_posts_count}
- Outreach emails sent: {outreach_emails_sent} (reply rate: {reply_rate}%)
- Revenue: {currency}{total_revenue} from {total_orders} orders
- Known competitors: {competitors}

### Completed Tasks This Run
{action_history}

### Remaining Budget
{remaining_credits} credits available

### Available Actions
{available_actions}

### User's Goal
{goal}

---

Based on all of the above, plan the next 1–3 most impactful tasks.
For each task, explain WHY it's the best use of credits right now.

Respond ONLY with a JSON array:
```json
[
  {{
    "task_type": "<one of the available action types>",
    "title": "<short human-readable title>",
    "description": "<what specifically to do>",
    "reasoning": "<why this is the best next action>",
    "priority": 1,
    "channel": "<channel this affects, or null>",
    "input_data": {{}}
  }}
]
```"""


class TaskPlanner:
    def __init__(self, llm: PlannerLLM) -> None:
        self._llm = llm

    async def plan_next_tasks(
        self,
        context: BusinessContext,
        run: Run,
        completed_tasks: list[RunTask],
    ) -> list[RunTask]:
        affordable = affordable_task_types(run.budget)
        if not affordable:
            return []

        available_actions = "\n".join(
            f"- {t.value}: {CREDIT_COSTS.get(t, 5)} credits"
            for t in affordable
        )

        action_history = "\n".join(
            f"- [{t.task_type.value}] {t.title} → {t.status.value}"
            for t in completed_tasks[-20:]
        ) or "None yet — this is the first iteration."

        brand_status = "✅ Complete" if context.has_brand else "❌ Not created"
        website_status = (
            f"✅ Live at {context.website_url}" if context.has_website else "❌ Not deployed"
        )

        prompt = PLANNING_USER_TEMPLATE.format(
            business_name=context.business_name,
            business_description=context.business_description,
            industry=context.industry or "Not specified",
            target_audience=context.target_audience or "Not specified",
            brand_status=brand_status,
            brand_summary=context.brand_summary or "",
            website_status=website_status,
            website_page_count=context.website_page_count,
            lighthouse=context.website_lighthouse_score or "N/A",
            socials=", ".join(context.connected_socials) or "None",
            recent_posts_count=context.recent_posts_count,
            outreach_emails_sent=context.outreach_emails_sent,
            reply_rate=round(context.outreach_reply_rate * 100, 1),
            currency="₦",
            total_revenue=context.total_revenue,
            total_orders=context.total_orders,
            competitors=", ".join(context.known_competitors) or "None identified",
            action_history=action_history,
            remaining_credits=run.budget.remaining,
            available_actions=available_actions,
            goal=run.goal or "Grow this business — improve brand, reach customers, generate revenue.",
        )

        messages = [
            {"role": "system", "content": PLANNING_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        response = await self._llm.complete(messages)

        try:
            text = response.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            planned = json.loads(text)
            if not isinstance(planned, list):
                planned = [planned]
        except (json.JSONDecodeError, IndexError) as exc:
            logger.warning("Failed to parse planner response: %s (raw response: %s)", exc, response)
            return []

        tasks: list[RunTask] = []
        for item in planned[:3]:
            try:
                task_type_str = item.get("task_type", "")
                task_type = TaskType(task_type_str)
                estimated = CREDIT_COSTS.get(task_type, 5)
                tasks.append(
                    RunTask(
                        run_id=run.id,
                        task_type=task_type,
                        title=item.get("title", task_type.value),
                        description=item.get("description", ""),
                        reasoning=item.get("reasoning", ""),
                        priority=int(item.get("priority", 5)),
                        estimated_credits=estimated,
                        channel=item.get("channel"),
                        input_data=item.get("input_data", {}) or {},
                    )
                )
            except (KeyError, ValueError) as exc:
                logger.warning("Skipping invalid planned task: %s (item: %s)", exc, item)
                continue

        return sorted(tasks, key=lambda t: t.priority)

    async def generate_brief(self, run: Run, context: BusinessContext) -> str:
        completed = [t for t in run.tasks if t.status == TaskStatus.COMPLETED]
        failed = [t for t in run.tasks if t.status == TaskStatus.FAILED]
        rejected = [t for t in run.tasks if t.status == TaskStatus.REJECTED]

        completed_summary = "\n".join(
            f"- {t.title}: {t.description}" for t in completed[-10:]
        ) or "No completed tasks yet."

        prompt = f"""Generate a concise executive brief for the business owner.

Business: {context.business_name}
Run duration: {run.iteration} iterations
Credits used: {run.budget.used}/{run.budget.total}
Tasks completed: {len(completed)}
Tasks failed: {len(failed)}
Tasks declined by owner: {len(rejected)}

Completed work:
{completed_summary}

Write a warm, professional summary in 3-5 short paragraphs. Address the user
directly. Mention specific accomplishments. Suggest what to focus on next.
Sign off as Abija."""

        messages = [
            {
                "role": "system",
                "content": "You are Abija, the AI business partner. Write concise, warm executive briefs.",
            },
            {"role": "user", "content": prompt},
        ]
        return await self._llm.complete(messages)
