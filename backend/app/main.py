from fastapi import FastAPI
from app.db import Base, engine
from app.models import Document, ChatSession, Message
from app.config import settings
from app.routers import documents

app = FastAPI(title=settings.app_name)

app.include_router(documents.router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.exec_driver_sql(
            "CREATE INDEX IF NOT EXISTS docs_embedding_hnsw "
            "ON docs USING hnsw (embedding vector_cosine_ops)"
        )

@app.get("/healthz")        
async def healthz():
    return {"ok": True}