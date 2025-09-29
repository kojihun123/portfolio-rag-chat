from sqlalchemy import text, bindparam
from sqlalchemy.ext.asyncio import AsyncSession
from pgvector.sqlalchemy import Vector
from app.embedding import embed_query
from app.config import settings

async def search_docs(db: AsyncSession, query: str, k: int | None = None):
    k = k or settings.top_k
    q_vec = embed_query(query)

    sql = text("""
        SELECT id, content, 1 - (embedding <=> :q) AS score
        FROM docs
        ORDER BY embedding <=> :q
        LIMIT :k
    """).bindparams(
        bindparam("q", type_=Vector(settings.embedding_dim))
    )

    res = await db.execute(sql, {"q": q_vec, "k": k})
    rows = res.fetchall()
    return [{"id": r[0], "content": r[1], "score": float(r[2])} for r in rows]
