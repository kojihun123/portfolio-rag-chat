# app/models.py
from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector

from app.db import Base
from app.config import settings

EMBED_DIM = settings.embedding_dim  # .env: EMBEDDING_DIM

# 지식베이스(문서/청크)
class Document(Base):
    __tablename__ = "docs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # 속성명은 meta, 실제 DB 컬럼명은 "metadata"
    meta: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    embedding = mapped_column(Vector(EMBED_DIM), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

# 대화 세션(스레드)
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # uuid 문자열 추천
    title: Mapped[Optional[str]] = mapped_column(String(200))
    user_id: Mapped[Optional[str]] = mapped_column(String(100))
    # 예약어 충돌 방지: 속성 meta ↔ 컬럼 "metadata"
    meta: Mapped[dict | None] = mapped_column("metadata", JSONB)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), index=True
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
        passive_deletes=True,
    )

# 세션 내 메시지(사용자/어시스턴트)
class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        String, ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[str] = mapped_column(String(10))  # "user" | "assistant" | "system"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # 예약어 충돌 방지
    meta: Mapped[dict | None] = mapped_column("metadata", JSONB)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    session: Mapped["ChatSession"] = relationship(back_populates="messages")
