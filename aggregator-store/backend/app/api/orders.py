"""
API роуты для заказов пользователя.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List
import random
import string

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.product_price import ProductPrice
from app.models.marketplace import Marketplace
from app.models.cart_item import CartItem
from app.models.user import User
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderListResponse,
    OrderCancelRequest,
)

router = APIRouter()


def generate_order_number() -> str:
    """Генерирует уникальный номер заказа."""
    # Формат: ORD-YYYYMMDD-XXXXXX
    date_part = datetime.utcnow().strftime("%Y%m%d")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ORD-{date_part}-{random_part}"


def order_to_response(order: Order) -> dict:
    """Конвертирует Order в ответ."""
    items = []
    for item in order.items:
        items.append({
            "id": item.id,
            "product": {
                "id": item.product_id,
                "name": item.product_name,
                "image": item.product_image,
                "sku": item.product_sku,
            },
            "marketplace": {
                "id": item.marketplace_id,
                "name": item.marketplace_name,
                "code": item.marketplace.code if item.marketplace else "unknown",
            },
            "price": float(item.price),
            "quantity": item.quantity,
            "subtotal": float(item.subtotal),
            "currency": item.currency,
            "product_url": item.product_url,
        })
    
    return {
        "id": order.id,
        "order_number": order.order_number,
        "status": order.status.value,
        "payment_status": order.payment_status,
        "total_amount": float(order.total_amount),
        "currency": order.currency,
        "items_count": order.items_count,
        "shipping_name": order.shipping_name,
        "shipping_phone": order.shipping_phone,
        "shipping_address": order.shipping_address,
        "tracking_number": order.tracking_number,
        "estimated_delivery": order.estimated_delivery,
        "shipped_at": order.shipped_at,
        "delivered_at": order.delivered_at,
        "items": items,
        "notes": order.notes,
        "cancel_reason": order.cancel_reason,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
    }


@router.get("/", response_model=OrderListResponse)
async def list_orders(
    status: OrderStatus = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Список заказов текущего пользователя.
    """
    query = select(Order).where(Order.user_id == current_user.id)
    
    if status:
        query = query.where(Order.status == status)
    
    # Считаем общее количество
    from sqlalchemy import func
    count_query = select(func.count(Order.id)).where(Order.user_id == current_user.id)
    if status:
        count_query = count_query.where(Order.status == status)
    
    result = await db.execute(count_query)
    total = result.scalar()
    
    # Пагинация
    skip = (page - 1) * page_size
    query = (
        query
        .options(selectinload(Order.items).selectinload(OrderItem.marketplace))
        .order_by(desc(Order.created_at))
        .offset(skip)
        .limit(page_size)
    )
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    return {
        "items": [order_to_response(o) for o in orders],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size if total > 0 else 1,
    }


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Получение деталей заказа.
    """
    result = await db.execute(
        select(Order)
        .where(
            and_(
                Order.id == order_id,
                Order.user_id == current_user.id,
            )
        )
        .options(
            selectinload(Order.items).selectinload(OrderItem.marketplace)
        )
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден"
        )
    
    return order_to_response(order)


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Создание заказа из товаров корзины.
    
    - **items**: Список товаров с количеством
    - **shipping_address**: Адрес доставки
    - **shipping_name**: Имя получателя
    - **shipping_phone**: Телефон
    - **payment_method**: Способ оплаты
    - **notes**: Комментарий
    """
    if not order_data.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Заказ должен содержать минимум один товар"
        )
    
    # Проверяем и собираем товары
    order_items_data = []
    total_amount = Decimal("0")
    
    for item_data in order_data.items:
        # Получаем товар
        result = await db.execute(
            select(Product)
            .where(Product.id == item_data.product_id)
            .options(selectinload(Product.prices).selectinload(ProductPrice.marketplace))
        )
        product = result.scalar_one_or_none()
        
        if not product or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Товар ID {item_data.product_id} не найден"
            )
        
        # Находим цену для выбранного маркетплейса
        price_info = None
        for p in product.prices:
            if p.marketplace_id == item_data.marketplace_id and p.is_available:
                price_info = p
                break
        
        if not price_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Товар недоступен на выбранном маркетплейсе"
            )
        
        # Рассчитываем сумму
        item_price = Decimal(str(price_info.price))
        item_subtotal = item_price * item_data.quantity
        total_amount += item_subtotal
        
        order_items_data.append({
            "product_id": product.id,
            "marketplace_id": price_info.marketplace_id,
            "marketplace_name": price_info.marketplace.name,
            "product_name": product.name,
            "product_image": product.images[0] if product.images else None,
            "product_sku": product.sku,
            "price": item_price,
            "quantity": item_data.quantity,
            "subtotal": item_subtotal,
            "currency": price_info.currency,
            "product_url": price_info.product_url,
        })
    
    # Создаём заказ
    new_order = Order(
        user_id=current_user.id,
        order_number=generate_order_number(),
        status=OrderStatus.PENDING,
        payment_status="pending",
        total_amount=total_amount,
        currency="USD",  # Можно взять из первого товара
        shipping_address=order_data.shipping_address.dict(),
        shipping_name=order_data.shipping_name,
        shipping_phone=order_data.shipping_phone,
        payment_method=order_data.payment_method,
        notes=order_data.notes,
        estimated_delivery=datetime.utcnow() + timedelta(days=7),
    )
    
    db.add(new_order)
    await db.flush()  # Получаем ID заказа
    
    # Создаём элементы заказа
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=new_order.id,
            **item_data
        )
        db.add(order_item)
    
    # Очищаем корзину (опционально - можно оставить товары)
    # await db.execute(
    #     delete(CartItem).where(CartItem.user_id == current_user.id)
    # )
    
    await db.commit()
    await db.refresh(new_order)
    
    return order_to_response(new_order)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: int,
    cancel_data: OrderCancelRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Отмена заказа (если он ещё не отправлен).
    """
    result = await db.execute(
        select(Order)
        .where(
            and_(
                Order.id == order_id,
                Order.user_id == current_user.id,
            )
        )
        .options(selectinload(Order.items))
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден"
        )
    
    if not order.can_cancel():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Заказ нельзя отменить в текущем статусе"
        )
    
    order.status = OrderStatus.CANCELLED
    order.cancel_reason = cancel_data.reason
    order.cancelled_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(order)
    
    return order_to_response(order)
