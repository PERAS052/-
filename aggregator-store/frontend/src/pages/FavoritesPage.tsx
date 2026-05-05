import { Link } from 'react-router-dom'
import { Heart, ShoppingBag } from 'lucide-react'
import { Button } from '@components/ui/button'
import { Card, CardContent } from '@components/ui/card'
import { useState } from 'react'

interface FavoriteItem {
  id: number
  product_id: number
  product_name: string
  product_slug: string
  product_image: string
  price: number
}

export function FavoritesPage() {
  const [items, setItems] = useState<FavoriteItem[]>([
    {
      id: 1,
      product_id: 1,
      product_name: 'iPhone 15 Pro',
      product_slug: 'iphone-15-pro',
      product_image: 'https://images.unsplash.com/photo-1696446701796-da61225697cc?w=400',
      price: 999,
    },
  ])

  const removeFavorite = (id: number) => {
    setItems(items.filter(item => item.id !== id))
  }

  if (items.length === 0) {
    return (
      <div className="container py-12 text-center">
        <Heart className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
        <h1 className="text-2xl font-bold mb-2">Избранное пусто</h1>
        <p className="text-muted-foreground mb-6">Добавьте товары в избранное, чтобы сохранить их</p>
        <Link to="/search">
          <Button>Перейти к покупкам</Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="container py-8">
      <h1 className="text-3xl font-bold mb-8">Избранное ({items.length})</h1>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {items.map((item) => (
          <Card key={item.id} className="overflow-hidden group">
            <CardContent className="p-0">
              <Link to={`/product/${item.product_slug}`}>
                <div className="aspect-square overflow-hidden bg-muted">
                  <img
                    src={item.product_image}
                    alt={item.product_name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                  />
                </div>
              </Link>
              <div className="p-4">
                <Link to={`/product/${item.product_slug}`}>
                  <h3 className="font-semibold hover:text-primary">{item.product_name}</h3>
                </Link>
                <p className="font-bold mt-2">${item.price}</p>
                <div className="flex gap-2 mt-4">
                  <Button variant="outline" className="flex-1" size="sm">
                    <ShoppingBag className="h-4 w-4 mr-2" />
                    В корзину
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => removeFavorite(item.id)}
                  >
                    <Heart className="h-4 w-4 fill-destructive text-destructive" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
