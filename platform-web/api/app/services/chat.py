"""Conversation transport: persistence, Redis session context, AI hand-off."""

import json
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


async def load_context(
    redis: aioredis.Redis | None, conversation: Conversation
) -> dict[str, Any]:
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
) -> tuple[Conversation, Message]:
    conversation = Conversation(
        user_id=user_id,
        business_id=business_id,
        channel=channel,
        context={"conversation_stage": "greeting", "ready_to_generate": False},
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

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
        from app.services.jobs import enqueue_brand_generation

        await enqueue_brand_generation(conversation.business_id)
