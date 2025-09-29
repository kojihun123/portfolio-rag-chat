# app/services/docs.py
from sqlalchemy import text, bindparam
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector

from app.config import settings
from app.embedding import embed_texts

async def upsert_doc(db: AsyncSession, doc_id: str, content: str, meta: dict | None):
    emb = embed_texts([content])[0]  # <- 리스트[float] 그대로

    sql = text("""
      INSERT INTO docs (id, content, metadata, embedding)
      VALUES (:id, :content, :meta, :emb)
      ON CONFLICT (id) DO UPDATE
        SET content=EXCLUDED.content,
            metadata=EXCLUDED.metadata,
            embedding=EXCLUDED.embedding
    """).bindparams(
        bindparam("meta", type_=JSONB),                              
        bindparam("emb",  type_=Vector(settings.embedding_dim)),
    )

    await db.execute(sql, {"id": doc_id, "content": content, "meta": meta, "emb": emb})
    await db.commit()
