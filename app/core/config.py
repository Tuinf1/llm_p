# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="llm_p/.env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # опционально: если переменные в .env могут быть в любом регистре
    )

    # Обязательные поля
    APP_NAME: str
    ENV: str

    # JWT настройки
    JWT_SECRET: str
    JWT_ALG: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # SQLite путь
    SQLITE_PATH: str

    # OpenRouter настройки
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str
    OPENROUTER_MODEL: str
    OPENROUTER_SITE_URL: str  # соответствует referer из требования (обычно используется как site_url или referer)
    OPENROUTER_APP_NAME: str  # соответствует title из требования

    OPENROUTER_TIMEOUT: int | None = None       # или str, если ожидаете строку
    OPENROUTER_MAX_RETRIES: int | None = None   # или str
    DEBUG: bool = False                         # Pydantic сам преобразует "true" в True
    LOG_LEVEL: str = "INFO"
    
# Единственный экземпляр настроек для импорта в других частях проекта
settings = Settings()