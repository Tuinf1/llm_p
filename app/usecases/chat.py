# app/usecases/chat.py
from typing import List

from llm_p.app.repositories.chat_messages import ChatMessageRepository
from llm_p.app.services.openrouter_client import OpenRouterClient
from llm_p.app.schemas.chat import ChatRequest, ChatResponse, MessagePublic # Используем MessageItem для истории
from llm_p.app.core.errors import ExternalServiceError
from llm_p.app.db.models import ChatMessage  
from llm_p.app.core.config import settings


class ChatUseCase:
    """Бизнес-логика общения с LLM через OpenRouter."""

    def __init__(self, message_repository: ChatMessageRepository, openrouter_client: OpenRouterClient):
        self.message_repository = message_repository
        self.openrouter_client = openrouter_client

    async def ask(self, user_id: int, request: ChatRequest) -> ChatResponse:
        """
        Обработка запроса к LLM.

        Шаги:
        1. Сохранить промпт пользователя в БД.
        2. Сформировать контекст (system + история + текущий промпт).
        3. Вызвать OpenRouter.
        4. Сохранить ответ ассистента в БД.
        5. Вернуть ответ.
        """
        # 1. Сохраняем промпт пользователя в БД
        # Создаем ORM-объект сообщения, так как репозиторий ждет объект
        user_msg = ChatMessage(
            user_id=user_id,
            role="user",
            content=request.prompt
        )
        await self.message_repository.add_message(user_msg)

        # 2. Формируем список сообщений для модели
        messages = []

        # Добавляем system-инструкцию, если она есть
        if request.system:
            messages.append({
                "role": "system",
                "content": request.system
            })

        # Получаем историю сообщений пользователя (ORM объекты)
        history_orm = await self.message_repository.get_user_history(
            user_id=user_id,
            limit=request.max_history
        )

        # Добавляем историю в формате, понятном модели
        for msg in history_orm:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # Добавляем текущий промпт (он уже сохранен в БД, но нужен для контекста)
        messages.append({
            "role": "user",
            "content": request.prompt
        })

        # 3. Вызываем OpenRouter
        try:
            # Используем модель из настроек .env
            assistant_response_text = await self.openrouter_client.chat_completion(
                messages=messages,
                model=settings.OPENROUTER_MODEL, 
                temperature=request.temperature
            )
        except Exception as e:
            raise ExternalServiceError(f"OpenRouter error: {str(e)}")

        # 4. Сохраняем ответ ассистента в БД
        # ИСПРАВЛЕНО: Создаем объект с ролью assistant и текстом ответа
        assistant_msg = ChatMessage(
            user_id=user_id,
            role="assistant",
            content=assistant_response_text
        )
        await self.message_repository.add_message(assistant_msg)

        # 5. Возвращаем ответ
        return ChatResponse(answer=assistant_response_text)

    async def get_history(self, user_id: int, limit: int = 50) -> List[MessagePublic]:
        """
        Получить историю сообщений пользователя.
        """
        messages_orm = await self.message_repository.get_user_history(
            user_id=user_id,
            limit=limit
        )

        # Преобразуем ORM-объекты в Pydantic-схемы
        # Убедитесь, что в schemas/chat.py есть класс MessageItem с model_config = ConfigDict(from_attributes=True)
        return [
            MessagePublic.model_validate(msg)
            for msg in messages_orm
        ]

    async def clear_history(self, user_id: int) -> None:
        """
        Очистить всю историю сообщений пользователя.
        """
        await self.message_repository.clear_user_history(user_id=user_id)