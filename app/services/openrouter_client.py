# app/services/openrouter_client.py
import httpx
from typing import List, Dict
from llm_p.app.core.errors import ExternalServiceError
from llm_p.app.core.config import settings  # Импортируем настройки

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
                # return response.json()["choices"][0]["message"]["content"]
                data = response.json()
                content = data["choices"][0]["message"]["content"]

                # если это строка → просто вернуть
                if isinstance(content, str):
                    return content

                # если это список блоков → собрать текст
                if isinstance(content, list):
                    texts = []
                    for item in content:
                        if item.get("type") == "text":
                            texts.append(item.get("text", ""))
                    return "\n".join(texts)

                # fallback
                return str(content)
        except httpx.RequestError as e:
            raise ExternalServiceError(f"Request to OpenRouter failed: {str(e)}")
        except KeyError as e:
            raise ExternalServiceError(f"Invalid response format from OpenRouter: {str(e)}")