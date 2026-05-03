# app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from llm_p.app.core.config import settings

# Формируем строку подключения к SQLite через aiosqlite
DATABASE_URL = f"sqlite+aiosqlite:///{settings.SQLITE_PATH}"

# Создаём асинхронный engine
engine = create_async_engine(DATABASE_URL, echo=False)  # echo=True для отладки SQL-запросов

# Создаём фабрику сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

