from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.schemas import DocumentCreate, SearchResponse, SearchHit
from app.services.docs import upsert_doc
from app.retriever import search_docs

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("")
async def upsert_document(payload: DocumentCreate, db: AsyncSession = Depends(get_db)):
    await upsert_doc(db, payload.id, payload.content, payload.meta)
    return {"ok": True}

@router.get("/search", response_model=SearchResponse)
async def search(q: str, k: int = 5, db: AsyncSession = Depends(get_db)):
    hits = await search_docs(db, q, k)
    return SearchResponse(query=q, hits=[SearchHit(**h) for h in hits])