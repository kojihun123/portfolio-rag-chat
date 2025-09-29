from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import event
from app.config import settings

DATABASE_URL = settings.database_url

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

@event.listens_for(Base.metadata, "before_create")
def _ensure_pgvector(target, connection, **kw):
    connection.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS vector")

async def get_db():
    async with SessionLocal() as session:
        yield session
