"""Conversation transport: persistence, Redis session context, AI hand-off."""

import json
import re
import uuid
from collections.abc import AsyncIterator
from typing import Any

import redis.asyncio as aioredis
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.base import AIService
from app.logging import get_logger
from app.models import Conversation, Message

log = get_logger(__name__)

CONTEXT_TTL_SECONDS = 86_400
MAX_HISTORY = 50


class ConversationNotFound(LookupError):
    pass


def chat_key(conversation_id: uuid.UUID) -> str:
    return f"chat:{conversation_id}"


async def load_context(redis: aioredis.Redis | None, conversation: Conversation) -> dict[str, Any]:
    if redis is not None:
        try:
            raw = await redis.get(chat_key(conversation.id))
            if raw:
                return json.loads(raw)
        except Exception:  # pragma: no cover - redis outage fallback
            log.warning("chat_context_read_failed", conversation_id=str(conversation.id))
    return dict(conversation.context or {})


async def save_context(
    redis: aioredis.Redis | None, conversation: Conversation, context: dict[str, Any]
) -> None:
    conversation.context = context
    if redis is not None:
        try:
            await redis.set(chat_key(conversation.id), json.dumps(context), ex=CONTEXT_TTL_SECONDS)
        except Exception:  # pragma: no cover - redis outage fallback
            log.warning("chat_context_write_failed", conversation_id=str(conversation.id))


async def get_conversation(db: AsyncSession, conversation_id: uuid.UUID) -> Conversation:
    conversation = await db.get(Conversation, conversation_id)
    if conversation is None:
        raise ConversationNotFound(str(conversation_id))
    return conversation


async def list_messages(
    db: AsyncSession, conversation_id: uuid.UUID, page: int = 1, limit: int = 50
) -> tuple[list[Message], int]:
    total = (
        await db.execute(
            select(func.count())
            .select_from(Message)
            .where(Message.conversation_id == conversation_id)
        )
    ).scalar_one()
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    return list(result.scalars().all()), total


def to_history(messages: list[Message]) -> list[dict[str, str]]:
    return [
        {"role": "assistant" if message.role == "assistant" else "user", "content": message.content}
        for message in messages
    ]


async def add_message(
    db: AsyncSession,
    conversation: Conversation,
    *,
    role: str,
    direction: str,
    content: str,
    media_url: str | None = None,
    media_type: str | None = None,
) -> Message:
    message = Message(
        conversation_id=conversation.id,
        role=role,
        direction=direction,
        content=content,
        media_url=media_url,
        media_type=media_type,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def start_conversation(
    db: AsyncSession,
    ai: AIService,
    *,
    user_id: uuid.UUID | None = None,
    business_id: uuid.UUID | None = None,
    channel: str = "webchat",
    initial_idea: str | None = None,
) -> tuple[Conversation, Message]:
    if business_id is None and user_id is not None:
        from app.models.business import Business

        business_id = await db.scalar(
            select(Business.id)
            .where(Business.owner_id == user_id)
            .order_by(Business.created_at.desc())
            .limit(1)
        )
        if business_id is None:
            new_biz = Business(
                name="My Business",
                slug=f"biz-{uuid.uuid4().hex[:8]}",
                description=initial_idea.strip() if initial_idea else None,
                status="onboarding",
                plan="free",
                credit_balance=50,
                owner_id=user_id,
            )
            db.add(new_biz)
            await db.flush()
            business_id = new_biz.id

    conversation = Conversation(
        user_id=user_id,
        business_id=business_id,
        channel=channel,
        context={
            "conversation_stage": "greeting",
            "ready_to_generate": False,
            "business_id": str(business_id) if business_id else None,
        },
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    if initial_idea and initial_idea.strip():
        await add_message(
            db,
            conversation,
            role="customer",
            direction="inbound",
            content=initial_idea.strip(),
        )
        greeting = ""
        async for chunk in ai.respond(
            conversation.context,
            [{"role": "user", "content": initial_idea.strip()}],
            initial_idea.strip(),
        ):
            greeting += chunk
        greeting = (
            greeting.strip()
            or f"I love that concept! Let's build your brand around {initial_idea.strip()[:50]}."
        )

        try:
            initial_extract = await ai.extract_context(
                [{"role": "user", "content": initial_idea.strip()}]
            )
            if initial_extract:
                conversation.context.update(
                    {k: v for k, v in initial_extract.items() if v is not None}
                )
                if conversation.business_id:
                    from app.models.business import Business

                    biz = await db.get(Business, conversation.business_id)
                    if biz is not None:
                        if initial_extract.get("business_name"):
                            biz.name = str(initial_extract["business_name"]).strip()
                        if initial_extract.get("industry"):
                            biz.industry = str(initial_extract["industry"]).strip()
                        if initial_extract.get("description"):
                            biz.description = str(initial_extract["description"]).strip()
                        db.add(biz)
        except Exception:
            log.warning(
                "initial_context_extraction_failed",
                conversation_id=str(conversation.id),
                exc_info=True,
            )
    else:
        greeting = ""
        async for chunk in ai.respond(conversation.context, [], ""):
            greeting += chunk
        greeting = greeting.strip() or "Hi! What business are we building today?"

    message = await add_message(
        db,
        conversation,
        role="assistant",
        direction="outbound",
        content=greeting,
    )
    conversation.status = "active"
    await db.commit()
    await db.refresh(conversation)
    await db.refresh(message)
    return conversation, message


async def process_message(
    db: AsyncSession,
    redis: aioredis.Redis | None,
    ai: AIService,
    conversation: Conversation,
    *,
    content: str,
    media_url: str | None = None,
    media_type: str | None = None,
) -> AsyncIterator[str]:
    """Persist inbound, stream Abija's reply, then persist and update context."""
    await add_message(
        db,
        conversation,
        role="customer",
        direction="inbound",
        content=content,
        media_url=media_url,
        media_type=media_type,
    )

    history_rows, _ = await list_messages(db, conversation.id, page=1, limit=MAX_HISTORY)
    history = to_history(history_rows)
    context = await load_context(redis, conversation)

    reply_parts: list[str] = []
    async for chunk in ai.respond(context, history[:-1], content):
        reply_parts.append(chunk)
        yield chunk
    reply = "".join(reply_parts).strip()

    if not reply:
        reply = "Sorry, I lost that thought. Could you say that again?"

    await add_message(
        db,
        conversation,
        role="assistant",
        direction="outbound",
        content=reply,
    )

    try:
        extracted = await ai.extract_context(history)
        context.update({k: v for k, v in extracted.items() if v is not None})
        if conversation.business_id:
            from app.models.business import Business

            business = await db.get(Business, conversation.business_id)
            if business is not None:
                updated = False
                if extracted.get("business_name") and str(extracted["business_name"]).strip():
                    business.name = str(extracted["business_name"]).strip()
                    if business.slug.startswith("biz-"):
                        base_slug = (
                            re.sub(r"[^a-z0-9]+", "-", business.name.lower()).strip("-")[:80]
                            or "business"
                        )
                        slug = base_slug
                        collision = await db.scalar(
                            select(Business.id).where(
                                Business.slug == slug, Business.id != business.id
                            )
                        )
                        if collision:
                            slug = f"{base_slug}-{str(business.id)[:6]}"
                        business.slug = slug
                    updated = True
                if extracted.get("industry") and str(extracted["industry"]).strip():
                    business.industry = str(extracted["industry"]).strip()
                    updated = True
                if extracted.get("description") and str(extracted["description"]).strip():
                    business.description = str(extracted["description"]).strip()
                    updated = True
                if extracted.get("location") and str(extracted["location"]).strip():
                    business.location = str(extracted["location"]).strip()[:120]
                    updated = True
                if extracted.get("contact_phone") and str(extracted["contact_phone"]).strip():
                    business.contact_phone = str(extracted["contact_phone"]).strip()[:20]
                    updated = True
                if extracted.get("contact_email") and str(extracted["contact_email"]).strip():
                    business.contact_email = str(extracted["contact_email"]).strip()[:200]
                    updated = True
                preferences = dict(business.preferences or {})
                for key in (
                    "target_audience",
                    "services",
                    "brand_preferences",
                    "mood",
                    "style_keywords",
                ):
                    value = extracted.get(key)
                    if (
                        isinstance(value, str)
                        and value.strip()
                        and key not in ("services", "style_keywords")
                    ):
                        preferences[key] = value.strip()[:1000]
                    elif key in ("services", "style_keywords") and isinstance(value, list):
                        preferences[key] = [
                            str(item)[:120] for item in value[:12] if str(item).strip()
                        ]
                if preferences != (business.preferences or {}):
                    business.preferences = preferences
                    updated = True
                if context.get("ready_to_generate") and business.status == "onboarding":
                    business.status = "ready"
                    updated = True
                if updated:
                    db.add(business)
                # Auto-create the canonical Project when Business becomes ready
                if business.status == "ready":
                    from app.services.project_bridge import get_or_create_project_for_business

                    try:
                        await get_or_create_project_for_business(db, business)
                    except Exception:
                        log.warning(
                            "project_bridge_failed",
                            business_id=str(business.id),
                            exc_info=True,
                        )
    except Exception:  # extraction failure should never break the chat
        log.warning(
            "context_extraction_failed",
            conversation_id=str(conversation.id),
            exc_info=True,
        )

    await save_context(redis, conversation, context)
    conversation.status = "active"
    await db.commit()

    if context.get("ready_to_generate") and conversation.business_id:
        from app.services.website_gen import WebsiteGenerationError, queue_website_generation

        try:
            result = await queue_website_generation(db, conversation.business_id)
            context["website_job_status"] = result["status"]
        except WebsiteGenerationError:
            context["website_job_status"] = "failed"
            log.warning(
                "website_generation_queue_failed",
                business_id=str(conversation.business_id),
                exc_info=True,
            )
        await save_context(redis, conversation, context)
        await db.commit()
