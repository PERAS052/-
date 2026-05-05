"""
Главный файл приложения FastAPI.
Точка входа для запуска сервера.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.db.session import init_db, close_db
from app.api import router as api_router
from app.core.exceptions import AggregatorException

# Получаем настройки
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения.
    
    - startup: Инициализация БД и кэша
    - shutdown: Закрытие соединений
    """
    # Startup
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Инициализация БД (только для разработки, в проде используем Alembic)
    # await init_db()
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")
    await close_db()


# Создаём приложение FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API агрегатора товаров международных маркетплейсов",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# =============================================================================
# Middleware
# =============================================================================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip сжатие ответов
app.add_middleware(GZipMiddleware, minimum_size=1000)


# =============================================================================
# Exception Handlers
# =============================================================================

@app.exception_handler(AggregatorException)
async def aggregator_exception_handler(request, exc: AggregatorException):
    """Обработчик кастомных исключений приложения."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "status_code": exc.status_code,
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Общий обработчик исключений."""
    # Логирование ошибки
    print(f"Unhandled exception: {exc}")
    
    if settings.DEBUG:
        raise exc  # В режиме разработки показываем полную ошибку
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Внутренняя ошибка сервера",
            "status_code": 500,
        }
    )


# =============================================================================
# Routes
# =============================================================================

@app.get("/")
async def root():
    """Корневой endpoint с информацией о приложении."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.DEBUG else None,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint для мониторинга."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
    }


# Подключаем API роуты
app.include_router(api_router, prefix="/api/v1")


# =============================================================================
# Run (для разработки)
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
