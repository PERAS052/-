"""
Модель заказа пользователя.
Содержит информацию о заказе и его статус.
"""

import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Numeric, Text, Enum, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.order_item import OrderItem


class OrderStatus(str, enum.Enum):
    """Статусы заказа."""
    PENDING = "pending"           # Ожидает обработки
    CONFIRMED = "confirmed"       # Подтверждён
    PROCESSING = "processing"     # В обработке
    SHIPPED = "shipped"           # Отправлен
    DELIVERED = "delivered"       # Доставлен
    CANCELLED = "cancelled"       # Отменён
    REFUNDED = "refunded"         # Возврат


class Order(Base, TimestampMixin):
    """Заказ пользователя (симуляция).
    
    Поля:
        id: Уникальный номер заказа
        user_id: ID пользователя
        status: Статус заказа
        total_amount: Итоговая сумма
        currency: Валюта
        
        # Адрес доставки
        shipping_address: JSON с адресом
        shipping_name: Имя получателя
        shipping_phone: Телефон
        
        # Оплата (симуляция)
        payment_method: Способ оплаты
        payment_status: Статус оплаты
        
        # Доставка
        tracking_number: Трек-номер
        estimated_delivery: Ожидаемая дата доставки
        
        notes: Комментарий к заказу
    """
    
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # User
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="ID пользователя"
    )
    
    # Order info
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus),
        default=OrderStatus.PENDING,
        nullable=False,
        index=True,
        comment="Статус заказа"
    )
    order_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
        comment="Номер заказа для отображения (ORD-XXXXXX)"
    )
    
    # Pricing
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Итоговая сумма заказа"
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="USD",
        nullable=False,
        comment="Валюта заказа"
    )
    
    # Shipping address (JSON)
    shipping_address: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        comment="Адрес доставки в формате JSON"
    )
    shipping_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Имя получателя"
    )
    shipping_phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Телефон получателя"
    )
    
    # Payment (simulation)
    payment_method: Mapped[str] = mapped_column(
        String(50),
        default="card",
        nullable=False,
        comment="Способ оплаты: card, paypal, etc."
    )
    payment_status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
        comment="Статус оплаты: pending, paid, failed"
    )
    
    # Delivery
    tracking_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Трек-номер для отслеживания"
    )
    estimated_delivery: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Ожидаемая дата доставки"
    )
    shipped_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Дата отправки"
    )
    delivered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Дата доставки"
    )
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Комментарий к заказу"
    )
    
    # Cancellation
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Дата отмены"
    )
    cancel_reason: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Причина отмены"
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Order(id={self.id}, number={self.order_number}, status={self.status.value})>"
    
    @property
    def items_count(self) -> int:
        """Общее количество позиций в заказе."""
        return sum(item.quantity for item in self.items)
    
    def can_cancel(self) -> bool:
        """Можно ли отменить заказ."""
        return self.status in (OrderStatus.PENDING, OrderStatus.CONFIRMED)
    
    def can_return(self) -> bool:
        """Можно ли оформить возврат."""
        return self.status == OrderStatus.DELIVERED
