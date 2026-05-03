# app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from llm_p.app.db.base import Base
from llm_p.app.db.session import engine
from llm_p.app.api.routes_auth import router as auth_router
from llm_p.app.api.routes_chat import router as chat_router
from llm_p.app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения.
    При старте создаём таблицы БД.
    """
    # Startup: создаём таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown: можно добавить очистку ресурсов, если нужно
    await engine.dispose()


def create_app() -> FastAPI:
    """
    Создаёт и настраивает приложение FastAPI.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        description="Protected API for LLM interaction via OpenRouter",
        lifespan=lifespan
    )

    # CORS middleware (опционально, но рекомендуется для фронтенда)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # В продакшене замените на конкретные домены
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Подключаем роутеры
    app.include_router(auth_router)
    app.include_router(chat_router)

    # Технический эндпоинт health check
    @app.get("/health", tags=["health"])
    async def health_check():
        return {
            "status": "ok",
            "environment": settings.ENV,
            "app_name": settings.APP_NAME
        }

    return app


# Создаём экземпляр приложения для uvicorn
app = create_app()