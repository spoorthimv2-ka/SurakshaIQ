from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.config.settings import settings

if not settings.postgres_url:
    raise ValueError("POSTGRES_URL is required in production")

if settings.postgres_url.startswith("postgresql://"):
    SQLALCHEMY_DATABASE_URL = settings.postgres_url.replace(
        "postgresql://", "postgresql+asyncpg://", 1
    )
else:
    SQLALCHEMY_DATABASE_URL = settings.postgres_url

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=settings.environment == "development",
    future=True,
    pool_size=5,
    max_overflow=10,
)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
