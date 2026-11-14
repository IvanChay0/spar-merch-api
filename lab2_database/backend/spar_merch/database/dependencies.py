from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from core.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
)

AsyncSessionMaker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    """Зависимость FastAPI для получения сессии БД."""
    async with AsyncSessionMaker() as session:
        yield session