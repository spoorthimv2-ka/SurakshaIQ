from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.config.settings import settings

# Construct the SQLAlchemy async URL
# If postgres_url is not set, fallback to a local asyncpg URI for development
if settings.postgres_url:
    # Ensure it uses the asyncpg driver
    if settings.postgres_url.startswith("postgresql://"):
        SQLALCHEMY_DATABASE_URL = settings.postgres_url.replace(
            "postgresql://", "postgresql+asyncpg://", 1
        )
    else:
        SQLALCHEMY_DATABASE_URL = settings.postgres_url
else:
    SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/suraksha"

# Create the async engine
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=settings.environment == "development",
    future=True,
    pool_size=5,
    max_overflow=10,
)

# Create the session maker
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.
    Yields an AsyncSession and ensures it is closed after the request.
    """
    async with async_session_maker() as session:
        yield session
