# app/api/routes_chat.py
from fastapi import APIRouter, Depends, HTTPException, status

# from llm_p.app.schemas.chat import ChatRequest, ChatResponse, MessageItem

from llm_p.app.schemas.chat import ChatRequest, ChatResponse, MessagePublic

from llm_p.app.usecases.chat import ChatUseCase
from llm_p.app.api.deps import get_chat_usecase, get_current_user_id
from llm_p.app.core.errors import ExternalServiceError


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "",
    response_model=ChatResponse,
    responses={
        503: {"description": "External service error (OpenRouter)"},
    }
)
async def chat(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    chat_usecase: ChatUseCase = Depends(get_chat_usecase)
):
    """
    Отправить запрос к LLM и получить ответ.
    
    Args:
        request: Данные запроса (prompt, system, max_history, temperature)
        user_id: ID текущего пользователя (из JWT токена)
        chat_usecase: Use case для чата
        
    Returns:
        ChatResponse: Ответ от модели
        
    Raises:
        HTTPException: 503 если OpenRouter вернул ошибку
    """
    try:
        return await chat_usecase.ask(user_id=user_id, request=request)
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"LLM service unavailable: {str(e)}"
        )


@router.get(
    "/history",
    response_model=list[MessagePublic],
    responses={
        401: {"description": "Not authenticated"},
    }
)
async def get_history(
    user_id: int = Depends(get_current_user_id),
    chat_usecase: ChatUseCase = Depends(get_chat_usecase),
    limit: int = 50  # можно сделать параметром запроса
):
    """
    Получить историю сообщений текущего пользователя.
    
    Args:
        user_id: ID текущего пользователя
        chat_usecase: Use case для чата
        limit: Максимальное количество сообщений (по умолчанию 50)
        
    Returns:
        list[MessageItem]: Список сообщений
    """
    return await chat_usecase.get_history(user_id=user_id, limit=limit)


@router.delete(
    "/history",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"description": "Not authenticated"},
    }
)
async def clear_history(
    user_id: int = Depends(get_current_user_id),
    chat_usecase: ChatUseCase = Depends(get_chat_usecase)
):
    """
    Очистить всю историю сообщений текущего пользователя.
    
    Args:
        user_id: ID текущего пользователя
        chat_usecase: Use case для чата
        
    Returns:
        None (статус 204 No Content)
    """
    await chat_usecase.clear_history(user_id=user_id)
    # Возвращаем 204 автоматически благодаря status_code