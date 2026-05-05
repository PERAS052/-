"""
Симулятор API маркетплейсов.
Генерирует тестовые данные для демонстрации агрегации.
"""

import random
from datetime import datetime
from typing import List, Dict, Any


class MarketplaceSimulator:
    """
    Симулятор данных маркетплейсов.
    
    Используется для демонстрации работы агрегатора без реальных API.
    """
    
    MARKETPLACES = [
        {
            "code": "aliexpress",
            "name": "AliExpress",
            "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Aliexpress_logo.svg/2560px-Aliexpress_logo.svg.png",
            "currency": "USD",
            "delivery_min": 15,
            "delivery_max": 45,
            "price_multiplier": 0.7,  # Дешевле
        },
        {
            "code": "amazon",
            "name": "Amazon",
            "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Amazon_logo.svg/2560px-Amazon_logo.svg.png",
            "currency": "USD",
            "delivery_min": 3,
            "delivery_max": 7,
            "price_multiplier": 1.0,  # Базовая цена
        },
        {
            "code": "wildberries",
            "name": "Wildberries",
            "logo_url": "/marketplaces/wildberries.svg",
            "currency": "RUB",
            "delivery_min": 1,
            "delivery_max": 3,
            "price_multiplier": 0.85,
        },
        {
            "code": "ozon",
            "name": "Ozon",
            "logo_url": "/marketplaces/ozon.svg",
            "currency": "RUB",
            "delivery_min": 1,
            "delivery_max": 5,
            "price_multiplier": 0.9,
        },
        {
            "code": "yandex_market",
            "name": "Яндекс.Маркет",
            "logo_url": "/marketplaces/yandex-market.svg",
            "currency": "RUB",
            "delivery_min": 1,
            "delivery_max": 4,
            "price_multiplier": 0.95,
        },
    ]
    
    SELLERS = [
        "Официальный магазин",
        "TechStore",
        "ElectroHub",
        "BestDeals",
        "TopSeller",
        "SuperShop",
    ]
    
    @classmethod
    def generate_price(
        cls,
        base_price: float,
        marketplace_code: str
    ) -> Dict[str, Any]:
        """
        Генерирует цену товара для конкретного маркетплейса.
        
        Args:
            base_price: Базовая цена товара
            marketplace_code: Код маркетплейса
            
        Returns:
            Словарь с ценой и метаданными
        """
        mp_config = next(
            (m for m in cls.MARKETPLACES if m["code"] == marketplace_code),
            cls.MARKETPLACES[0]
        )
        
        # Применяем множитель цены
        price = round(base_price * mp_config["price_multiplier"], 2)
        
        # Добавляем случайную вариацию ±10%
        variation = random.uniform(0.9, 1.1)
        price = round(price * variation, 2)
        
        # Иногда добавляем скидку
        has_discount = random.random() < 0.3
        original_price = None
        if has_discount:
            original_price = round(price * random.uniform(1.1, 1.5), 2)
        
        # Случайная доступность
        is_available = random.random() > 0.1  # 90% доступны
        
        return {
            "price": price,
            "original_price": original_price,
            "currency": mp_config["currency"],
            "is_available": is_available,
            "availability": "in_stock" if is_available else "out_of_stock",
            "delivery_days_min": mp_config["delivery_min"],
            "delivery_days_max": mp_config["delivery_max"],
            "seller_name": random.choice(cls.SELLERS),
            "seller_rating": round(random.uniform(3.5, 5.0), 1),
        }
    
    @classmethod
    def generate_product_prices(
        cls,
        base_price: float,
        include_marketplaces: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Генерирует цены для товара на всех (или выбранных) маркетплейсах.
        
        Args:
            base_price: Базовая цена товара
            include_marketplaces: Список кодов маркетплейсов (по умолчанию все)
            
        Returns:
            Список цен по маркетплейсам
        """
        if include_marketplaces is None:
            include_marketplaces = [m["code"] for m in cls.MARKETPLACES]
        
        prices = []
        for mp_code in include_marketplaces:
            mp_config = next(
                (m for m in cls.MARKETPLACES if m["code"] == mp_code),
                None
            )
            if not mp_config:
                continue
            
            price_data = cls.generate_price(base_price, mp_code)
            price_data["marketplace_code"] = mp_code
            price_data["product_url"] = f"https://example.com/{mp_code}/product"
            prices.append(price_data)
        
        return prices
    
    @classmethod
    def get_marketplace_info(cls, code: str) -> Dict[str, Any]:
        """Возвращает информацию о маркетплейсе."""
        return next(
            (m for m in cls.MARKETPLACES if m["code"] == code),
            cls.MARKETPLACES[0]
        )
    
    @classmethod
    def get_all_marketplaces(cls) -> List[Dict[str, Any]]:
        """Возвращает все маркетплейсы."""
        return cls.MARKETPLACES
