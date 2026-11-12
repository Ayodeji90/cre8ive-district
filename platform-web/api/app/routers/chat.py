import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import async_session_factory, get_db
from app.deps import get_ai
from app.llm.base import AIService
from app.logging import get_logger
from app.models import Conversation, User
from app.schemas.conversation import (
    ChatHistoryResponse,
    ChatStartRequest,
    ChatStartResponse,
)
from app.schemas.conversation import (
    MessageResponse as ChatMessageResponse,
)
from app.services import chat as chat_service

log = get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/start", response_model=ChatStartResponse)
async def start_chat(
    payload: ChatStartRequest,
    db: AsyncSession = Depends(get_db),
    ai: AIService = Depends(get_ai),
    user: User = Depends(get_current_user),
) -> ChatStartResponse:
    conversation, greeting = await chat_service.start_conversation(
        db, ai, user_id=payload.user_id or user.id, business_id=payload.business_id
    )
    return ChatStartResponse(
        conversation_id=conversation.id,
        greeting_message=greeting.content,
        context=conversation.context,
    )


@router.get("/{conversation_id}/history", response_model=ChatHistoryResponse)
async def history(
    conversation_id: uuid.UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ChatHistoryResponse:
    try:
        conversation = await chat_service.get_conversation(db, conversation_id)
    except chat_service.ConversationNotFound as exc:
        raise HTTPException(status_code=404, detail="Conversation not found") from exc
    messages, total = await chat_service.list_messages(db, conversation_id, page, limit)
    return ChatHistoryResponse(
        conversation_id=conversation.id,
        messages=[ChatMessageResponse.model_validate(message) for message in messages],
        context=conversation.context,
        total=total,
        page=page,
        limit=limit,
    )


@router.websocket("/{conversation_id}")
async def chat_socket(
    websocket: WebSocket,
    conversation_id: uuid.UUID,
    token: str | None = Query(default=None),
) -> None:
    await websocket.accept()
    try:
        async with async_session_factory() as db:
            try:
                conversation = await chat_service.get_conversation(db, conversation_id)
            except chat_service.ConversationNotFound:
                await websocket.close(code=4404, reason="Conversation not found")
                return

            ai = getattr(websocket.app.state, "ai", None) or get_ai()
            redis = getattr(websocket.app.state, "redis", None)

            await websocket.send_json(
                {
                    "type": "ready",
                    "conversation_id": str(conversation.id),
                    "context": await chat_service.load_context(redis, conversation),
                }
            )

            while True:
                raw = await websocket.receive_json()
                if raw.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                    continue

                try:
                    inbound = _parse_inbound(raw)
                except ValidationError as exc:
                    await websocket.send_json(
                        {"type": "error", "detail": "Invalid message", "errors": exc.errors()}
                    )
                    continue

                full = ""
                try:
                    async for chunk in chat_service.process_message(
                        db,
                        redis,
                        ai,
                        conversation,
                        content=inbound["content"],
                        media_url=inbound.get("media_url"),
                        media_type=inbound.get("media_type"),
                    ):
                        full += chunk
                        await websocket.send_json({"type": "chunk", "content": chunk})
                except Exception:
                    log.error(
                        "chat_stream_failed",
                        conversation_id=str(conversation.id),
                        exc_info=True,
                    )
                    await websocket.send_json(
                        {"type": "error", "detail": "Abija could not reply. Please try again."}
                    )
                    continue

                await websocket.send_json(
                    {
                        "type": "done",
                        "content": full,
                        "context": conversation.context,
                    }
                )
    except WebSocketDisconnect:
        log.info("chat_disconnected", conversation_id=str(conversation_id))
        async with async_session_factory() as db:
            conversation = await db.get(Conversation, conversation_id)
            if conversation is not None:
                conversation.status = "idle"
                await db.commit()


def _parse_inbound(raw: dict) -> dict:
    from app.schemas.conversation import InboundMessage

    return InboundMessage.model_validate(raw).model_dump()
