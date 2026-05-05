"""
Pydantic схемы для маркетплейсов.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl


# =============================================================================
# Base Schemas
# =============================================================================

class MarketplaceBase(BaseModel):
    """Базовая схема маркетплейса."""
    name: str
    code: str
    logo_url: str
    website_url: str
    currency: str = "USD"
    country: str = "US"


# =============================================================================
# Request Schemas
# =============================================================================

class MarketplaceCreate(MarketplaceBase):
    """Схема создания маркетплейса."""
    api_endpoint: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    parsing_enabled: bool = True


class MarketplaceUpdate(BaseModel):
    """Схема обновления маркетплейса."""
    name: Optional[str] = None
    logo_url: Optional[str] = None
    api_endpoint: Optional[str] = None
    is_active: Optional[bool] = None
    parsing_enabled: Optional[bool] = None


# =============================================================================
# Response Schemas
# =============================================================================

class MarketplaceResponse(MarketplaceBase):
    """Схема ответа с маркетплейсом."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    api_endpoint: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    parsing_enabled: bool
    created_at: datetime


class MarketplaceSimple(BaseModel):
    """Упрощённая схема маркетплейса (для вложенных ответов)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    code: str
    logo_url: str
