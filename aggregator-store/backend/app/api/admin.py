"""
API роуты для административной панели.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, require_admin, require_manager
from app.models.user import User, UserRole
from app.models.product import Product
from app.models.order import Order, OrderStatus
from app.models.marketplace import Marketplace
from app.models.category import Category
from app.models.view_history import ViewHistory

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats(
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    """
    Статистика дашборда для админ-панели.
    """
    # Общая статистика
    stats = {}
    
    # Количество пользователей
    result = await db.execute(select(func.count(User.id)))
    stats["total_users"] = result.scalar()
    
    result = await db.execute(
        select(func.count(User.id)).where(
            User.created_at >= datetime.utcnow() - timedelta(days=30)
        )
    )
    stats["new_users_30d"] = result.scalar()
    
    # Количество товаров
    result = await db.execute(select(func.count(Product.id)))
    stats["total_products"] = result.scalar()
    
    result = await db.execute(
        select(func.count(Product.id)).where(Product.is_active == True)
    )
    stats["active_products"] = result.scalar()
    
    # Заказы
    result = await db.execute(select(func.count(Order.id)))
    stats["total_orders"] = result.scalar()
    
    result = await db.execute(
        select(func.sum(Order.total_amount)).where(Order.status != OrderStatus.CANCELLED)
    )
    stats["total_revenue"] = float(result.scalar() or 0)
    
    # Заказы по статусам
    status_counts = {}
    for status in OrderStatus:
        result = await db.execute(
            select(func.count(Order.id)).where(Order.status == status)
        )
        status_counts[status.value] = result.scalar()
    stats["orders_by_status"] = status_counts
    
    # Просмотры за последние 7 дней
    daily_views = []
    for i in range(7):
        date = datetime.utcnow().date() - timedelta(days=i)
        result = await db.execute(
            select(func.count(ViewHistory.id)).where(
                func.date(ViewHistory.viewed_at) == date
            )
        )
        daily_views.append({
            "date": date.isoformat(),
            "views": result.scalar()
        })
    stats["daily_views"] = list(reversed(daily_views))
    
    return stats


@router.get("/marketplaces")
async def get_marketplaces_status(
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    """
    Статус маркетплейсов и количество товаров от каждого.
    """
    result = await db.execute(
        select(
            Marketplace.id,
            Marketplace.name,
            Marketplace.code,
            Marketplace.is_active,
            Marketplace.parsing_enabled,
            func.count(ProductPrice.id).label("products_count")
        )
        .outerjoin(ProductPrice, ProductPrice.marketplace_id == Marketplace.id)
        .group_by(Marketplace.id)
    )
    
    marketplaces = []
    for row in result.all():
        marketplaces.append({
            "id": row[0],
            "name": row[1],
            "code": row[2],
            "is_active": row[3],
            "parsing_enabled": row[4],
            "products_count": row[5],
        })
    
    return {"marketplaces": marketplaces}


@router.post("/marketplaces/{marketplace_id}/sync")
async def sync_marketplace(
    marketplace_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Запуск синхронизации цен с маркетплейсом.
    
    В реальном приложении здесь запускался бы фоновый таск.
    """
    result = await db.execute(
        select(Marketplace).where(Marketplace.id == marketplace_id)
    )
    marketplace = result.scalar_one_or_none()
    
    if not marketplace:
        raise HTTPException(status_code=404, detail="Маркетплейс не найден")
    
    # Заглушка для симуляции синхронизации
    return {
        "message": f"Синхронизация с {marketplace.name} запущена",
        "marketplace_id": marketplace_id,
        "sync_started_at": datetime.utcnow().isoformat(),
    }


@router.get("/logs")
async def get_system_logs(
    log_type: str = "all",  # all, error, warning, info
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_admin),
):
    """
    Системные логи (заглушка).
    
    В реальном приложении здесь был бы запрос к системе логирования.
    """
    # Заглушка с примером логов
    logs = [
        {
            "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
            "level": "info",
            "message": "Scheduled price update completed",
            "source": "sync_service",
        },
        {
            "timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
            "level": "warning",
            "message": "High response time from AliExpress API",
            "source": "api_client",
        },
        {
            "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            "level": "error",
            "message": "Failed to parse product from Amazon",
            "source": "parser",
        },
    ]
    
    if log_type != "all":
        logs = [l for l in logs if l["level"] == log_type]
    
    return {"logs": logs[:limit]}


@router.get("/top-products")
async def get_top_products(
    by: str = Query("views", enum=["views", "orders", "revenue"]),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    """
    Топ товаров по разным метрикам.
    """
    if by == "views":
        result = await db.execute(
            select(Product)
            .where(Product.is_active == True)
            .options(selectinload(Product.prices))
            .order_by(desc(Product.views_count))
            .limit(limit)
        )
        products = result.scalars().all()
        
        return [
            {
                "id": p.id,
                "name": p.name,
                "slug": p.slug,
                "views": p.views_count,
                "min_price": p.min_price,
            }
            for p in products
        ]
    
    # Для orders и revenue нужны данные из OrderItem
    return {"products": []}


@router.get("/users-by-role")
async def get_users_by_role(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Распределение пользователей по ролям.
    """
    stats = {}
    for role in UserRole:
        result = await db.execute(
            select(func.count(User.id)).where(User.role == role)
        )
        stats[role.value] = result.scalar()
    
    return {"roles": stats}


@router.post("/clear-cache")
async def clear_cache(
    cache_type: str = "all",  # all, search, products
    current_user: User = Depends(require_admin),
):
    """
    Очистка кэша (заглушка).
    
    В реальном приложении здесь бы очищался Redis кэш.
    """
    return {
        "message": f"Cache {cache_type} cleared successfully",
        "cleared_at": datetime.utcnow().isoformat(),
    }
