from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase
from src.config import settings


engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,      # Test connection before using
    pool_size=5,             # Keep 5 connections ready
    max_overflow=10,         # Allow up to 10 extra under load
    pool_recycle=300,        # Recycle connections every 5 mins
                             # Prevents Neon idle disconnects
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    Drizzle owns migrations. SQLAlchemy only queries.
    """
    pass


async def get_db():
    """
    FastAPI dependency that provides a database session.
    Use with Depends(get_db) in route handlers.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()