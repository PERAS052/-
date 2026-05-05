"""
Pydantic схемы для валидации данных API.
"""

from app.schemas.user import UserBase, UserCreate, UserResponse, UserLogin, Token
from app.schemas.category import CategoryBase, CategoryCreate, CategoryResponse, CategoryTree
from app.schemas.marketplace import MarketplaceBase, MarketplaceResponse
from app.schemas.product import (
    ProductBase, 
    ProductCreate, 
    ProductResponse, 
    ProductListResponse,
    ProductPriceInfo,
    ProductFilter
)
from app.schemas.cart import CartItemCreate, CartItemResponse, CartResponse
from app.schemas.order import OrderCreate, OrderResponse, OrderItemResponse
from app.schemas.search import SearchQuery, SearchResponse, AutocompleteResponse

__all__ = [
    # User
    "UserBase",
    "UserCreate", 
    "UserResponse",
    "UserLogin",
    "Token",
    # Category
    "CategoryBase",
    "CategoryCreate",
    "CategoryResponse",
    "CategoryTree",
    # Marketplace
    "MarketplaceBase",
    "MarketplaceResponse",
    # Product
    "ProductBase",
    "ProductCreate",
    "ProductResponse",
    "ProductListResponse",
    "ProductPriceInfo",
    "ProductFilter",
    # Cart
    "CartItemCreate",
    "CartItemResponse", 
    "CartResponse",
    # Order
    "OrderCreate",
    "OrderResponse",
    "OrderItemResponse",
    # Search
    "SearchQuery",
    "SearchResponse",
    "AutocompleteResponse",
]
