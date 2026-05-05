import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { Heart, ShoppingCart, Share2, Star, Truck, Shield, RotateCcw } from 'lucide-react'
import { Button } from '@components/ui/button'
import { Card, CardContent } from '@components/ui/card'
import { useQuery } from '@tanstack/react-query'
import api from '@services/api'

interface PriceInfo {
  marketplace: {
    id: number
    name: string
    code: string
    logo_url: string
  }
  price: number
  original_price: number | null
  discount_percent: number | null
  currency: string
  product_url: string
  is_available: boolean
  delivery_range: string
  seller_name: string
}

interface Product {
  id: number
  name: string
  slug: string
  description: string
  brand: string
  images: string[]
  specifications: Record<string, string>
  rating: number
  review_count: number
  min_price: number | null
  max_price: number | null
  prices: PriceInfo[]
}

export function ProductPage() {
  const { slug } = useParams<{ slug: string }>()
  const [selectedImage, setSelectedImage] = useState(0)
  const [selectedMarketplace, setSelectedMarketplace] = useState<number | null>(null)

  const { data: product, isLoading } = useQuery({
    queryKey: ['product', slug],
    queryFn: async () => {
      const response = await api.get(`/products/${slug}`)
      return response.data as Product
    },
  })

  if (isLoading) {
    return (
      <div className="container py-8">
        <div className="animate-pulse grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="aspect-square bg-muted rounded-lg" />
          <div className="space-y-4">
            <div className="h-8 bg-muted rounded w-3/4" />
            <div className="h-4 bg-muted rounded w-1/4" />
            <div className="h-6 bg-muted rounded w-1/3" />
          </div>
        </div>
      </div>
    )
  }

  if (!product) {
    return (
      <div className="container py-8 text-center">
        <h1 className="text-2xl font-bold mb-4">Товар не найден</h1>
        <p className="text-muted-foreground">Возможно, товар был удалён или ссылка неверная</p>
      </div>
    )
  }

  const bestPrice = product.prices?.find(p => p.is_available) || product.prices?.[0]

  return (
    <div className="container py-8">
      {/* Breadcrumb */}
      <div className="text-sm text-muted-foreground mb-6">
        <span>Главная</span>
        <span className="mx-2">/</span>
        <span>{product.brand}</span>
        <span className="mx-2">/</span>
        <span>{product.name}</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
        {/* Images */}
        <div className="space-y-4">
          <div className="aspect-square rounded-lg overflow-hidden bg-muted">
            <img
              src={product.images[selectedImage] || 'https://via.placeholder.com/600'}
              alt={product.name}
              className="w-full h-full object-cover"
            />
          </div>
          {product.images.length > 1 && (
            <div className="flex gap-2 overflow-x-auto">
              {product.images.map((img, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedImage(idx)}
                  className={`flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 ${
                    selectedImage === idx ? 'border-primary' : 'border-transparent'
                  }`}
                >
                  <img src={img} alt="" className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Info */}
        <div className="space-y-6">
          <div>
            <p className="text-sm text-muted-foreground mb-1">{product.brand}</p>
            <h1 className="text-3xl font-bold">{product.name}</h1>
            <div className="flex items-center gap-4 mt-2">
              <div className="flex items-center gap-1">
                <Star className="h-5 w-5 fill-yellow-400 text-yellow-400" />
                <span className="font-semibold">{product.rating}</span>
                <span className="text-muted-foreground">({product.review_count} отзывов)</span>
              </div>
            </div>
          </div>

          {/* Prices Comparison */}
          <Card>
            <CardContent className="p-4">
              <h3 className="font-semibold mb-4">Цены в магазинах</h3>
              <div className="space-y-3">
                {product.prices?.map((price) => (
                  <div
                    key={price.marketplace.id}
                    onClick={() => setSelectedMarketplace(price.marketplace.id)}
                    className={`flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors ${
                      selectedMarketplace === price.marketplace.id
                        ? 'bg-primary/10 border border-primary'
                        : 'hover:bg-muted'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <img
                        src={price.marketplace.logo_url}
                        alt={price.marketplace.name}
                        className="h-8 w-8 object-contain"
                      />
                      <div>
                        <p className="font-medium">{price.marketplace.name}</p>
                        <p className="text-sm text-muted-foreground">
                          Доставка: {price.delivery_range}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-lg">${price.price}</p>
                      {price.discount_percent && (
                        <p className="text-sm text-green-600">-{price.discount_percent}%</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Actions */}
          <div className="flex gap-3">
            <Button size="lg" className="flex-1">
              <ShoppingCart className="mr-2 h-5 w-5" />
              В корзину
            </Button>
            <Button variant="outline" size="icon">
              <Heart className="h-5 w-5" />
            </Button>
            <Button variant="outline" size="icon">
              <Share2 className="h-5 w-5" />
            </Button>
          </div>

          {/* Features */}
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="p-3 bg-muted rounded-lg">
              <Truck className="h-6 w-6 mx-auto mb-2 text-primary" />
              <p className="text-sm">Доставка</p>
            </div>
            <div className="p-3 bg-muted rounded-lg">
              <Shield className="h-6 w-6 mx-auto mb-2 text-primary" />
              <p className="text-sm">Гарантия</p>
            </div>
            <div className="p-3 bg-muted rounded-lg">
              <RotateCcw className="h-6 w-6 mx-auto mb-2 text-primary" />
              <p className="text-sm">Возврат</p>
            </div>
          </div>
        </div>
      </div>

      {/* Description & Specs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          <section>
            <h2 className="text-2xl font-bold mb-4">Описание</h2>
            <p className="text-muted-foreground leading-relaxed">
              {product.description || 'Описание товара отсутствует.'}
            </p>
          </section>

          {Object.keys(product.specifications).length > 0 && (
            <section>
              <h2 className="text-2xl font-bold mb-4">Характеристики</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {Object.entries(product.specifications).map(([key, value]) => (
                  <div key={key} className="flex justify-between py-2 border-b">
                    <span className="text-muted-foreground">{key}</span>
                    <span className="font-medium">{value}</span>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>

        {/* Similar Products */}
        <aside>
          <h3 className="font-bold mb-4">Похожие товары</h3>
          <div className="space-y-4">
            <p className="text-muted-foreground">Загрузка рекомендаций...</p>
          </div>
        </aside>
      </div>
    </div>
  )
}
