"""
Модель избранных товаров пользователя.
Связующая таблица many-to-many между User и Product.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.product import Product


class Favorite(Base):
    """Избранный товар пользователя.
    
    Поля:
        id: Уникальный идентификатор
        user_id: ID пользователя
        product_id: ID товара
        created_at: Дата добавления в избранное
        
    Уникальный индекс (user_id, product_id) предотвращает дубли.
    """
    
    __tablename__ = "favorites"
    
    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', name='uix_user_product_favorite'),
    )
    
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
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        comment="Дата добавления в избранное"
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="favorites")
    product: Mapped["Product"] = relationship("Product", back_populates="favorites")
    
    def __repr__(self) -> str:
        return f"<Favorite(user={self.user_id}, product={self.product_id})>"
