"""
Модель отзывов на товары.
Отзывы привязаны к товару и маркетплейсу (где куплен/просмотрен).
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.product import Product
    from app.models.marketplace import Marketplace


class Review(Base, TimestampMixin):
    """Отзыв на товар.
    
    Поля:
        id: Уникальный идентификатор
        user_id: ID автора отзыва
        product_id: ID товара
        marketplace_id: ID маркетплейса (где куплен)
        
        rating: Оценка (1-5)
        title: Заголовок отзыва
        content: Текст отзыва
        pros: Достоинства
        cons: Недостатки
        
        is_verified: Проверенная покупка
        is_helpful: Полезный отзыв (лайки)
        helpful_count: Количество лайков
        
        images: URL изображений к отзыву (JSON)
    """
    
    __tablename__ = "reviews"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign Keys
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID автора"
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID товара"
    )
    marketplace_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("marketplaces.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID маркетплейса (где куплен)"
    )
    
    # Review content
    rating: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Оценка 1-5"
    )
    title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Заголовок отзыва"
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Текст отзыва"
    )
    pros: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Достоинства"
    )
    cons: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Недостатки"
    )
    
    # Status
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Проверенная покупка"
    )
    is_approved: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Одобрен модератором"
    )
    
    # Engagement
    helpful_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="Количество "полезно""
    )
    
    # Media
    images: Mapped[Optional[list]] = mapped_column(
        default=list,
        nullable=True,
        comment="Изображения к отзыву (JSON array)"
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="reviews")
    product: Mapped["Product"] = relationship("Product", back_populates="reviews")
    marketplace: Mapped[Optional["Marketplace"]] = relationship("Marketplace")
    
    def __repr__(self) -> str:
        return f"<Review(id={self.id}, product={self.product_id}, rating={self.rating})>"
    
    @property
    def is_positive(self) -> bool:
        """Положительный ли отзыв (4+ звёзд)."""
        return self.rating >= 4.0
    
    @property
    def is_negative(self) -> bool:
        """Отрицательный ли отзыв (2- звёзд)."""
        return self.rating <= 2.0
