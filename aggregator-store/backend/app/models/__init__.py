"""
SQLAlchemy модели для Aggregator Store.
Включает 12 таблиц для полноценной работы агрегатора маркетплейсов.
"""

from app.models.base import Base
from app.models.user import User, UserRole
from app.models.category import Category
from app.models.marketplace import Marketplace
from app.models.product import Product
from app.models.product_price import ProductPrice
from app.models.favorite import Favorite
from app.models.cart_item import CartItem
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.view_history import ViewHistory
from app.models.comparison_list import ComparisonList
from app.models.review import Review

__all__ = [
    "Base",
    "User",
    "UserRole",
    "Category",
    "Marketplace",
    "Product",
    "ProductPrice",
    "Favorite",
    "CartItem",
    "Order",
    "OrderStatus",
    "OrderItem",
    "ViewHistory",
    "ComparisonList",
    "Review",
]
