import { Link } from 'react-router-dom'
import { Trash2, Plus, Minus, ShoppingBag } from 'lucide-react'
import { Button } from '@components/ui/button'
import { Card, CardContent } from '@components/ui/card'
import { useState } from 'react'

interface CartItem {
  id: number
  product_id: number
  product_name: string
  product_slug: string
  product_image: string
  price: number
  quantity: number
}

export function CartPage() {
  const [items, setItems] = useState<CartItem[]>([
    {
      id: 1,
      product_id: 1,
      product_name: 'iPhone 15 Pro',
      product_slug: 'iphone-15-pro',
      product_image: 'https://images.unsplash.com/photo-1696446701796-da61225697cc?w=400',
      price: 999,
      quantity: 1,
    },
  ])

  const total = items.reduce((sum, item) => sum + item.price * item.quantity, 0)

  const updateQuantity = (id: number, quantity: number) => {
    if (quantity < 1) return
    setItems(items.map(item => item.id === id ? { ...item, quantity } : item))
  }

  const removeItem = (id: number) => {
    setItems(items.filter(item => item.id !== id))
  }

  if (items.length === 0) {
    return (
      <div className="container py-12 text-center">
        <ShoppingBag className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
        <h1 className="text-2xl font-bold mb-2">Корзина пуста</h1>
        <p className="text-muted-foreground mb-6">Добавьте товары в корзину, чтобы оформить заказ</p>
        <Link to="/search">
          <Button>Перейти к покупкам</Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="container py-8">
      <h1 className="text-3xl font-bold mb-8">Корзина ({items.length})</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-4">
          {items.map((item) => (
            <Card key={item.id}>
              <CardContent className="p-4 flex gap-4">
                <Link to={`/product/${item.product_slug}`}>
                  <img
                    src={item.product_image}
                    alt={item.product_name}
                    className="w-24 h-24 object-cover rounded-md"
                  />
                </Link>
                <div className="flex-1">
                  <Link to={`/product/${item.product_slug}`}>
                    <h3 className="font-semibold hover:text-primary">{item.product_name}</h3>
                  </Link>
                  <p className="text-muted-foreground">${item.price}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <Button
                      variant="outline"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => updateQuantity(item.id, item.quantity - 1)}
                    >
                      <Minus className="h-4 w-4" />
                    </Button>
                    <span className="w-8 text-center">{item.quantity}</span>
                    <Button
                      variant="outline"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => updateQuantity(item.id, item.quantity + 1)}
                    >
                      <Plus className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 ml-auto text-destructive"
                      onClick={() => removeItem(item.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="lg:col-span-1">
          <Card className="sticky top-24">
            <CardContent className="p-6">
              <h2 className="font-semibold text-lg mb-4">Итого</h2>
              <div className="space-y-2 mb-4">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Товары ({items.length})</span>
                  <span>${total}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Доставка</span>
                  <span className="text-green-600">Бесплатно</span>
                </div>
                <div className="border-t pt-2 flex justify-between font-bold text-lg">
                  <span>Итого</span>
                  <span>${total}</span>
                </div>
              </div>
              <Link to="/checkout">
                <Button className="w-full" size="lg">Оформить заказ</Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
