"""
Модель истории просмотров товаров пользователем.
Используется для рекомендательной системы и "недавно просмотренных".
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.product import Product


class ViewHistory(Base):
    """История просмотра товара пользователем.
    
    Поля:
        id: Уникальный идентификатор
        user_id: ID пользователя
        product_id: ID просмотренного товара
        viewed_at: Дата и время просмотра
        view_count: Сколько раз просмотрен
        source: Источник (search, recommendation, direct, category)
        
    Используется для:
    - Персональных рекомендаций
    - "Вы недавно смотрели"
    - Аналитики поведения
    """
    
    __tablename__ = "view_history"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign Keys
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID пользователя"
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID товара"
    )
    
    # View details
    viewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="Дата и время просмотра"
    )
    view_count: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Счётчик просмотров данного товара"
    )
    source: Mapped[str] = mapped_column(
        default="direct",
        nullable=False,
        comment="Источник: search, recommendation, direct, category"
    )
    
    # Session info (optional)
    session_id: Mapped[str] = mapped_column(
        nullable=True,
        comment="ID сессии (для неавторизованных)"
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="view_history")
    product: Mapped["Product"] = relationship("Product", back_populates="view_history")
    
    def __repr__(self) -> str:
        return f"<ViewHistory(user={self.user_id}, product={self.product_id}, at={self.viewed_at})>"
