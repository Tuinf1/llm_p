# app/api/deps.py
from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from llm_p.app.db.session import AsyncSessionLocal
from llm_p.app.repositories.users import UserRepository
from llm_p.app.repositories.chat_messages import ChatMessageRepository
from llm_p.app.usecases.auth import AuthUseCase
from llm_p.app.usecases.chat import ChatUseCase
from llm_p.app.services.openrouter_client import OpenRouterClient
from llm_p.app.core.security import decode_access_token
# from llm_p.app.core.config import settings


# --- Dependency для сессии БД ---
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Асинхронный генератор сессии БД."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# --- Dependencies для репозиториев ---
def get_user_repo(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    """Получить репозиторий пользователей."""
    return UserRepository(session=session)

def get_chat_message_repo(session: AsyncSession = Depends(get_db_session)) -> ChatMessageRepository:
    """Получить репозиторий сообщений чата."""
    return ChatMessageRepository(session=session)


# --- Dependencies для usecase'ов ---
def get_auth_usecase(user_repo: UserRepository = Depends(get_user_repo)) -> AuthUseCase:
    """Получить usecase авторизации."""
    return AuthUseCase(user_repository=user_repo)

def get_chat_usecase(
    message_repo: ChatMessageRepository = Depends(get_chat_message_repo),
    openrouter_client: OpenRouterClient = Depends(lambda: OpenRouterClient())
) -> ChatUseCase:
    """Получить usecase чата."""
    return ChatUseCase(message_repository=message_repo, openrouter_client=openrouter_client)


# --- Dependency для получения текущего пользователя ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")  # URL логина для Swagger

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """
    Получить ID текущего пользователя из JWT токена.
    
    Args:
        token: JWT access token
        
    Returns:
        user_id: int
        
    Raises:
        HTTPException: 401 если токен невалиден или истек
    """
    try:
        payload = decode_access_token(token)
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing 'sub' claim"
            )
        return int(user_id_str)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )