from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, Sequence
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.llm.openai_client import OpenAIClient
from app.models import ChatSession, Message
from app.retriever import search_docs
from app.schemas import ChatRequest, ChatResponse, Role

SYSTEM_PROMPT = (
    "You are a helpful assistant for a portfolio website. "
    "Answer in Korean unless the user requests another language. "
    "If the latest user message contains numbered context like [1], [2], cite them in your reply."
)

_HISTORY_LIMIT = 20

_llm_client: OpenAIClient | None = None


def _get_llm_client() -> OpenAIClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = OpenAIClient()
    return _llm_client


async def ask_llm(db: AsyncSession, payload: ChatRequest) -> ChatResponse:
    """Main chat entry point used by the router."""
    message = payload.message.strip()
    if not message:
        raise ValueError("message must not be empty")

    session = await _get_or_create_session(db, payload.session_id)

    top_k = payload.top_k if payload.top_k and payload.top_k > 0 else settings.top_k
    context_text, sources = await _build_context(db, message, top_k)

    try:
        user_msg = await _save_message(db, session.id, Role.user.value, message)
        history = await _load_history(db, session.id, _HISTORY_LIMIT)
        llm_messages = _to_llm_messages(history, user_msg.id, context_text)
        reply = await _get_llm_client().acomplete(messages=llm_messages, system=SYSTEM_PROMPT)
        await _save_message(db, session.id, Role.assistant.value, reply, meta={"sources": sources} if sources else None)
        session.last_activity_at = datetime.now(timezone.utc)
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return ChatResponse(reply=reply, sources=sources, session_id=session.id)


async def _get_or_create_session(db: AsyncSession, session_id: str | None) -> ChatSession:
    if session_id:
        session = await db.get(ChatSession, session_id)
        if session:
            return session
        new_session = ChatSession(id=session_id)
    else:
        new_session = ChatSession(id=str(uuid4()))

    db.add(new_session)
    await db.flush()
    return new_session


async def _load_history(db: AsyncSession, session_id: str, limit: int) -> Sequence[Message]:
    stmt = (
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    messages = list(result.scalars())
    messages.reverse()
    return messages


async def _save_message(
    db: AsyncSession,
    session_id: str,
    role: str,
    content: str,
    *,
    meta: dict | None = None,
) -> Message:
    msg = Message(session_id=session_id, role=role, content=content, meta=meta)
    db.add(msg)
    await db.flush()
    return msg


async def _build_context(db: AsyncSession, query: str, top_k: int) -> tuple[str, list[str]]:
    if top_k <= 0:
        return "", []

    hits = await search_docs(db, query, top_k)
    if not hits:
        return "", []

    formatted = []
    sources: list[str] = []
    for idx, hit in enumerate(hits, start=1):
        sources.append(hit["id"])
        snippet = hit["content"].strip()
        formatted.append(f"[{idx}] {snippet}")

    return "\n\n".join(formatted), sources


def _to_llm_messages(history: Iterable[Message], latest_user_id: int, context: str) -> list[dict[str, str]]:
    messages = []
    for msg in history:
        content = msg.content
        if msg.id == latest_user_id and context:
            content = (
                f"{msg.content}\n\n"
                "Relevant context:\n"
                f"{context}\n\n"
                "If the answer uses the context, cite using [number]."
            )
        messages.append({"role": msg.role, "content": content})
    return messages