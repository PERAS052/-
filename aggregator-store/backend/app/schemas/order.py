"""
Pydantic схемы для заказов.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, ConfigDict, Field


# =============================================================================
# Enums
# =============================================================================

class OrderStatus(str, Enum):
    """Статусы заказа."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, Enum):
    """Статусы оплаты."""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


# =============================================================================
# Address Schema
# =============================================================================

class ShippingAddress(BaseModel):
    """Адрес доставки."""
    country: str = Field(..., max_length=100)
    city: str = Field(..., max_length=100)
    postal_code: str = Field(..., max_length=20)
    street: str = Field(..., max_length=255)
    house: str = Field(..., max_length=50)
    apartment: Optional[str] = Field(None, max_length=50)


# =============================================================================
# Request Schemas
# =============================================================================

class OrderItemCreate(BaseModel):
    """Элемент для создания заказа."""
    product_id: int
    marketplace_id: int
    quantity: int = Field(..., ge=1, le=99)


class OrderCreate(BaseModel):
    """Схема создания заказа."""
    items: List[OrderItemCreate] = Field(..., min_length=1)
    shipping_address: ShippingAddress
    shipping_name: str = Field(..., max_length=255)
    shipping_phone: str = Field(..., max_length=20)
    payment_method: str = "card"
    notes: Optional[str] = None


class OrderCancelRequest(BaseModel):
    """Схема отмены заказа."""
    reason: Optional[str] = Field(None, max_length=255)


# =============================================================================
# Response Schemas
# =============================================================================

class OrderItemMarketplaceInfo(BaseModel):
    """Информация о маркетплейсе в заказе."""
    id: int
    name: str
    code: str
    logo_url: str


class OrderItemProductInfo(BaseModel):
    """Информация о товаре в заказе (snapshot)."""
    id: int
    name: str
    image: Optional[str]
    sku: Optional[str]


class OrderItemResponse(BaseModel):
    """Элемент заказа в ответе."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    product: OrderItemProductInfo
    marketplace: OrderItemMarketplaceInfo
    price: float
    quantity: int
    subtotal: float
    currency: str
    product_url: str


class OrderResponse(BaseModel):
    """Полный ответ заказа."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    order_number: str
    status: OrderStatus
    payment_status: PaymentStatus
    
    # Pricing
    total_amount: float
    currency: str
    items_count: int
    
    # Shipping
    shipping_name: str
    shipping_phone: str
    shipping_address: ShippingAddress
    
    # Delivery
    tracking_number: Optional[str]
    estimated_delivery: Optional[datetime]
    shipped_at: Optional[datetime]
    delivered_at: Optional[datetime]
    
    # Items
    items: List[OrderItemResponse]
    
    # Notes
    notes: Optional[str]
    cancel_reason: Optional[str]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime


class OrderListResponse(BaseModel):
    """Список заказов с пагинацией."""
    items: List[OrderResponse]
    total: int
    page: int
    page_size: int
    pages: int


class OrderStatusHistory(BaseModel):
    """История изменения статуса заказа."""
    status: OrderStatus
    changed_at: datetime
    notes: Optional[str]
