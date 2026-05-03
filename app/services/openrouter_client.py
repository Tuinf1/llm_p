# app/services/openrouter_client.py
import httpx
from typing import List, Dict
from llm_p.app.core.errors import ExternalServiceError
from llm_p.app.core.config import settings  # Импортируем настройки здесь


class OpenRouterClient:
    """Клиент для взаимодействия с API OpenRouter."""
    
    def __init__(self):
        """Конструктор пустой, настройки берутся из глобального объекта settings"""
        pass
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str,
        temperature: float = 0.7
    ) -> str:
        """
        Отправляет запрос к OpenRouter и возвращает текст ответа.
        """
        url = f"{settings.OPENROUTER_BASE_URL.rstrip('/')}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": settings.OPENROUTER_SITE_URL,
            "X-Title": settings.OPENROUTER_APP_NAME,
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        try:
            timeout = settings.OPENROUTER_TIMEOUT or 30.0
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code >= 400:
                    raise ExternalServiceError(
                        f"OpenRouter API error: {response.status_code} - {response.text}"
                    )
                
                # Возвращаем только текст ответа
                return response.json()["choices"][0]["message"]["content"]
                
        except httpx.RequestError as e:
            raise ExternalServiceError(f"Request to OpenRouter failed: {str(e)}")
        except KeyError as e:
            raise ExternalServiceError(f"Invalid response format from OpenRouter: {str(e)}")