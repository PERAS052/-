"""
Модель элементов корзины пользователя.
Каждый элемент привязан к конкретному товару и маркетплейсу.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.product import Product
    from app.models.marketplace import Marketplace


class CartItem(Base):
    """Элемент корзины пользователя.
    
    Поля:
        id: Уникальный идентификатор
        user_id: ID пользователя
        product_id: ID товара
        marketplace_id: ID выбранного маркетплейса
        quantity: Количество
        added_at: Дата добавления
        
    Уникальный индекс (user_id, product_id, marketplace_id) - 
    один товар от одного маркетплейса только один раз в корзине.
    """
    
    __tablename__ = "cart_items"
    
    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', 'marketplace_id', 
                        name='uix_user_product_marketplace_cart'),
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
    marketplace_id: Mapped[int] = mapped_column(
        ForeignKey("marketplaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID выбранного маркетплейса"
    )
    
    # Quantity
    quantity: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Количество товара"
    )
    
    # Timestamp
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        comment="Дата добавления в корзину"
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="cart_items")
    product: Mapped["Product"] = relationship("Product", back_populates="cart_items")
    marketplace: Mapped["Marketplace"] = relationship("Marketplace")
    
    def __repr__(self) -> str:
        return f"<CartItem(user={self.user_id}, product={self.product_id}, qty={self.quantity})>"
    
    def get_subtotal(self) -> float:
        """Подсчёт стоимости позиции."""
        # Ищем цену для данного маркетплейса
        for price in self.product.prices:
            if price.marketplace_id == self.marketplace_id and price.is_available:
                return price.price * self.quantity
        return 0.0
