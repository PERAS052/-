"""
API роуты v1.
Все эндпоинты сгруппированы по функционалу.
"""

from fastapi import APIRouter

from app.api import auth, users, products, categories, search, cart, orders, favorites, comparison, recommendations, admin

# Главный роутер API v1
router = APIRouter(prefix="/v1")

# Подключаем модули
router.include_router(auth.router, prefix="/auth", tags=["Аутентификация"])
router.include_router(users.router, prefix="/users", tags=["Пользователи"])
router.include_router(categories.router, prefix="/categories", tags=["Категории"])
router.include_router(products.router, prefix="/products", tags=["Товары"])
router.include_router(search.router, prefix="/search", tags=["Поиск"])
router.include_router(cart.router, prefix="/cart", tags=["Корзина"])
router.include_router(orders.router, prefix="/orders", tags=["Заказы"])
router.include_router(favorites.router, prefix="/favorites", tags=["Избранное"])
router.include_router(comparison.router, prefix="/comparison", tags=["Сравнение"])
router.include_router(recommendations.router, prefix="/recommendations", tags=["Рекомендации"])
router.include_router(admin.router, prefix="/admin", tags=["Админ-панель"])
