"""
Базовый класс для всех моделей SQLAlchemy.
Содержит общие поля и настройки.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для всех моделей.
    
    Обеспечивает:
    - Автоматическое создание таблиц
    - Общие колонки для всех моделей (created_at, updated_at)
    """
    
    # Автоматическое именование таблиц в snake_case
    pass


class TimestampMixin:
    """Миксин для добавления timestamp полей к моделям."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Дата создания записи"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Дата последнего обновления"
    )
