from __future__ import annotations

from typing import Optional, List
from enum import Enum
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, AliasChoices

# ---------------------------
# 공통 타입
# ---------------------------
class Role(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"

# ---------------------------
# Document (지식 베이스)
# ---------------------------
class DocumentCreate(BaseModel):
    """문서/청크 적재용 요청 바디"""
    id: str
    content: str
    # 입력 받을 때는 meta/metadata 둘 다 OK, 코드에선 payload.meta 로 사용
    meta: Optional[dict] = Field(default=None, validation_alias=AliasChoices("meta", "metadata"))

class SearchHit(BaseModel):
    """벡터 검색 결과 한 건"""
    id: str
    content: str
    score: float  # 0~1 (코사인 유사도면 보통 1 - distance)

class SearchResponse(BaseModel):
    """검색 응답 포맷"""
    query: str
    hits: List[SearchHit]

# ---------------------------
# ChatSession / Message (대화 히스토리)
# ---------------------------
class ChatSessionCreate(BaseModel):
    """새 세션 생성 요청 바디 (선택값 위주)"""
    title: Optional[str] = None
    user_id: Optional[str] = None
    meta: Optional[dict] = Field(default=None, validation_alias=AliasChoices("meta", "metadata"))

class ChatSessionOut(BaseModel):
    """세션 정보 응답"""
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: Optional[str] = None
    user_id: Optional[str] = None
    meta: Optional[dict] = None
    created_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None

class MessageCreate(BaseModel):
    """메시지 생성 요청 바디"""
    session_id: str
    role: Role
    content: str
    meta: Optional[dict] = Field(default=None, validation_alias=AliasChoices("meta", "metadata"))

class MessageOut(BaseModel):
    """메시지 응답"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    session_id: str
    role: Role
    content: str
    meta: Optional[dict] = None
    created_at: datetime

# ---------------------------
# Chat API (RAG 엔드포인트)
# ---------------------------
class ChatRequest(BaseModel):
    """/chat 요청 바디: 세션 없으면 백엔드에서 새로 만들 수 있게 session_id는 옵션"""
    session_id: Optional[str] = None
    message: str
    top_k: Optional[int] = None  # 미지정 시 settings.top_k 사용

class ChatResponse(BaseModel):
    """/chat 응답 포맷"""
    reply: str
    sources: List[str] = []   # 사용한 Document.id 목록
    session_id: str           # 이어서 대화할 때 필요