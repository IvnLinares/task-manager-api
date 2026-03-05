from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# Create async engine for SQLite
# Note: connect_args={"check_same_thread": False} is specific to SQLite
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=False,
    connect_args={"check_same_thread": False}
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

async def get_db():
    """
    Dependency to yield an async database session.
    """
    async with AsyncSessionLocal() as session:
        yield session
