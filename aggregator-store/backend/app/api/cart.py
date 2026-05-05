"""
API роуты для корзины пользователя.
"""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.product_price import ProductPrice
from app.models.marketplace import Marketplace
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartResponse, CartItemResponse, CartSummary

router = APIRouter()


def cart_item_to_response(cart_item: CartItem) -> dict:
    """Конвертирует CartItem в ответ."""
    product = cart_item.product
    marketplace = cart_item.marketplace
    
    # Находим актуальную цену
    price_info = None
    for p in product.prices:
        if p.marketplace_id == cart_item.marketplace_id:
            price_info = p
            break
    
    if not price_info:
        # Fallback если цена не найдена
        price_info = product.prices[0] if product.prices else None
    
    price_data = {
        "price": price_info.price if price_info else 0,
        "original_price": price_info.original_price if price_info else None,
        "discount_percent": price_info.discount_percent if price_info else None,
        "currency": price_info.currency if price_info else "USD",
        "is_available": price_info.is_available if price_info else False,
        "product_url": price_info.product_url if price_info else "",
    } if price_info else {
        "price": 0,
        "original_price": None,
        "discount_percent": None,
        "currency": "USD",
        "is_available": False,
        "product_url": "",
    }
    
    subtotal = price_data["price"] * cart_item.quantity
    
    return {
        "id": cart_item.id,
        "product": {
            "id": product.id,
            "name": product.name,
            "slug": product.slug,
            "brand": product.brand,
            "image": product.images[0] if product.images else None,
            "rating": product.rating,
        },
        "marketplace": {
            "id": marketplace.id,
            "name": marketplace.name,
            "code": marketplace.code,
            "logo_url": marketplace.logo_url,
            "currency": marketplace.currency,
        },
        "price_info": price_data,
        "quantity": cart_item.quantity,
        "subtotal": subtotal,
        "added_at": cart_item.added_at,
    }


@router.get("/", response_model=CartResponse)
async def get_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Получение корзины текущего пользователя.
    """
    result = await db.execute(
        select(CartItem)
        .where(CartItem.user_id == current_user.id)
        .options(
            selectinload(CartItem.product).selectinload(Product.prices),
            selectinload(CartItem.marketplace)
        )
    )
    cart_items = result.scalars().all()
    
    items = [cart_item_to_response(item) for item in cart_items]
    
    # Считаем итоги
    total_items = sum(item["quantity"] for item in items)
    unique_items = len(items)
    subtotal = sum(item["subtotal"] for item in items)
    
    return {
        "items": items,
        "summary": {
            "total_items": total_items,
            "unique_items": unique_items,
            "subtotal": subtotal,
            "currency": "USD",
        }
    }


@router.post("/", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    item_data: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Добавление товара в корзину.
    """
    # Проверяем существование товара
    result = await db.execute(
        select(Product)
        .where(Product.id == item_data.product_id)
        .options(selectinload(Product.prices))
    )
    product = result.scalar_one_or_none()
    
    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден"
        )
    
    # Проверяем маркетплейс
    result = await db.execute(
        select(Marketplace).where(Marketplace.id == item_data.marketplace_id)
    )
    marketplace = result.scalar_one_or_none()
    
    if not marketplace or not marketplace.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Маркетплейс не найден или неактивен"
        )
    
    # Проверяем доступность цены
    price_available = any(
        p.marketplace_id == item_data.marketplace_id and p.is_available
        for p in product.prices
    )
    
    if not price_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Товар недоступен на выбранном маркетплейсе"
        )
    
    # Проверяем, есть ли уже такой товар в корзине
    result = await db.execute(
        select(CartItem).where(
            and_(
                CartItem.user_id == current_user.id,
                CartItem.product_id == item_data.product_id,
                CartItem.marketplace_id == item_data.marketplace_id,
            )
        )
    )
    existing_item = result.scalar_one_or_none()
    
    if existing_item:
        # Обновляем количество
        existing_item.quantity += item_data.quantity
        await db.commit()
        await db.refresh(existing_item)
        
        # Подгружаем связанные данные для ответа
        result = await db.execute(
            select(CartItem)
            .where(CartItem.id == existing_item.id)
            .options(
                selectinload(CartItem.product).selectinload(Product.prices),
                selectinload(CartItem.marketplace)
            )
        )
        existing_item = result.scalar_one()
        
        return cart_item_to_response(existing_item)
    
    # Создаём новый элемент
    new_item = CartItem(
        user_id=current_user.id,
        product_id=item_data.product_id,
        marketplace_id=item_data.marketplace_id,
        quantity=item_data.quantity,
        added_at=datetime.utcnow(),
    )
    
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    
    # Подгружаем связанные данные
    result = await db.execute(
        select(CartItem)
        .where(CartItem.id == new_item.id)
        .options(
            selectinload(CartItem.product).selectinload(Product.prices),
            selectinload(CartItem.marketplace)
        )
    )
    new_item = result.scalar_one()
    
    return cart_item_to_response(new_item)


@router.patch("/{item_id}", response_model=CartItemResponse)
async def update_cart_item(
    item_id: int,
    quantity: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Обновление количества товара в корзине.
    """
    result = await db.execute(
        select(CartItem)
        .where(
            and_(
                CartItem.id == item_id,
                CartItem.user_id == current_user.id,
            )
        )
        .options(
            selectinload(CartItem.product).selectinload(Product.prices),
            selectinload(CartItem.marketplace)
        )
    )
    cart_item = result.scalar_one_or_none()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Элемент корзины не найден"
        )
    
    if quantity < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Количество должно быть минимум 1"
        )
    
    if quantity > 99:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Максимальное количество - 99"
        )
    
    cart_item.quantity = quantity
    await db.commit()
    await db.refresh(cart_item)
    
    return cart_item_to_response(cart_item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Удаление товара из корзины.
    """
    result = await db.execute(
        select(CartItem).where(
            and_(
                CartItem.id == item_id,
                CartItem.user_id == current_user.id,
            )
        )
    )
    cart_item = result.scalar_one_or_none()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Элемент корзины не найден"
        )
    
    await db.delete(cart_item)
    await db.commit()
    
    return None


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Очистка всей корзины.
    """
    await db.execute(
        delete(CartItem).where(CartItem.user_id == current_user.id)
    )
    await db.commit()
    
    return None
