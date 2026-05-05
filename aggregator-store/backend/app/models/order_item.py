"""
Модель элементов заказа.
Каждый элемент содержит информацию о товаре, маркетплейсе и цене на момент заказа.
"""

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import String, Numeric, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.product import Product
    from app.models.marketplace import Marketplace


class OrderItem(Base):
    """Элемент заказа (товар в заказе).
    
    Поля:
        id: Уникальный идентификатор
        order_id: ID заказа
        product_id: ID товара (snapshot на момент заказа)
        marketplace_id: ID маркетплейса
        
        # Snapshot данных (фиксируем на момент заказа)
        product_name: Название товара
        product_image: Изображение товара
        price: Цена за единицу
        quantity: Количество
        subtotal: Промежуточная сумма
        currency: Валюта
        
        # Маркетплейс информация
        marketplace_name: Название маркетплейса
        product_url: Ссылка на товар
    """
    
    __tablename__ = "order_items"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign Keys
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID заказа"
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="ID товара"
    )
    marketplace_id: Mapped[int] = mapped_column(
        ForeignKey("marketplaces.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="ID маркетплейса"
    )
    
    # Product snapshot (на момент заказа)
    product_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Название товара (snapshot)"
    )
    product_image: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
        comment="Изображение товара (snapshot)"
    )
    product_sku: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        comment="SKU товара (snapshot)"
    )
    
    # Pricing (fixed at order time)
    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Цена за единицу на момент заказа"
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Количество"
    )
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Итого за позицию (price * quantity)"
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        comment="Валюта"
    )
    
    # Marketplace info (snapshot)
    marketplace_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Название маркетплейса (snapshot)"
    )
    product_url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        comment="Ссылка на товар"
    )
    
    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")
    marketplace: Mapped["Marketplace"] = relationship("Marketplace")
    
    def __repr__(self) -> str:
        return f"<OrderItem(order={self.order_id}, product={self.product_name[:30]}..., qty={self.quantity})>"
