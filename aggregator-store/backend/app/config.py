"""
Конфигурация приложения с использованием Pydantic Settings.
Все переменные окружения валидируются и типизируются.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # =============================================================================
    # Application
    # =============================================================================
    APP_NAME: str = "Aggregator Store"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # =============================================================================
    # Database
    # =============================================================================
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/aggregator_store"
    
    # =============================================================================
    # Redis
    # =============================================================================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # =============================================================================
    # JWT Authentication
    # =============================================================================
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # =============================================================================
    # CORS
    # =============================================================================
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Парсит строку CORS origins в список."""
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
    
    # =============================================================================
    # Pagination
    # =============================================================================
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # =============================================================================
    # ML Service
    # =============================================================================
    ML_SERVICE_URL: Optional[str] = None
    ENABLE_RECOMMENDATIONS: bool = True
    
    # =============================================================================
    # Email (опционально)
    # =============================================================================
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: str = "noreply@aggregator.store"


@lru_cache()
def get_settings() -> Settings:
    """Возвращает кэшированный экземпляр настроек."""
    return Settings()
