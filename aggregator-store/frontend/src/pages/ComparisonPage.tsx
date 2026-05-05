import { Link } from 'react-router-dom'
import { X, Scale } from 'lucide-react'
import { Button } from '@components/ui/button'
import { Card, CardContent } from '@components/ui/card'
import { useState } from 'react'

interface CompareProduct {
  id: number
  name: string
  slug: string
  brand: string
  image: string
  price: number
  rating: number
  specs: Record<string, string>
}

export function ComparisonPage() {
  const [products, setProducts] = useState<CompareProduct[]>([
    {
      id: 1,
      name: 'iPhone 15 Pro',
      slug: 'iphone-15-pro',
      brand: 'Apple',
      image: 'https://images.unsplash.com/photo-1696446701796-da61225697cc?w=400',
      price: 999,
      rating: 4.8,
      specs: { 'Экран': '6.1"', 'Память': '128GB', 'Батарея': '3274 мАч' },
    },
    {
      id: 2,
      name: 'Samsung Galaxy S24',
      slug: 'samsung-galaxy-s24',
      brand: 'Samsung',
      image: 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400',
      price: 799,
      rating: 4.6,
      specs: { 'Экран': '6.2"', 'Память': '256GB', 'Батарея': '4000 мАч' },
    },
  ])

  const removeProduct = (id: number) => {
    setProducts(products.filter(p => p.id !== id))
  }

  if (products.length === 0) {
    return (
      <div className="container py-12 text-center">
        <Scale className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
        <h1 className="text-2xl font-bold mb-2">Нет товаров для сравнения</h1>
        <p className="text-muted-foreground mb-6">Добавьте до 4 товаров для сравнения</p>
        <Link to="/search">
          <Button>Найти товары</Button>
        </Link>
      </div>
    )
  }

  const allSpecs = [...new Set(products.flatMap(p => Object.keys(p.specs)))]

  return (
    <div className="container py-8">
      <h1 className="text-3xl font-bold mb-8">Сравнение товаров ({products.length}/4)</h1>
      
      <div className="overflow-x-auto">
        <div className="grid" style={{ gridTemplateColumns: `200px repeat(${products.length}, minmax(250px, 1fr))` }}>
          {/* Headers */}
          <div className="p-4"></div>
          {products.map((product) => (
            <div key={product.id} className="p-4 text-center relative">
              <button
                onClick={() => removeProduct(product.id)}
                className="absolute top-2 right-2 p-1 hover:bg-muted rounded"
              >
                <X className="h-4 w-4" />
              </button>
              <Link to={`/product/${product.slug}`}>
                <img
                  src={product.image}
                  alt={product.name}
                  className="w-32 h-32 object-cover mx-auto mb-2 rounded-lg"
                />
                <h3 className="font-semibold hover:text-primary">{product.name}</h3>
              </Link>
              <p className="text-muted-foreground text-sm">{product.brand}</p>
              <p className="font-bold mt-2">${product.price}</p>
              <div className="flex justify-center gap-2 mt-2">
                <Button size="sm">В корзину</Button>
              </div>
            </div>
          ))}

          {/* Rows */}
          <div className="p-4 font-medium bg-muted">Рейтинг</div>
          {products.map((product) => (
            <div key={product.id} className="p-4 text-center border-l">
              <span className="text-yellow-500">★</span> {product.rating}
            </div>
          ))}

          {allSpecs.map((spec) => (
            <>
              <div key={spec} className="p-4 font-medium bg-muted">{spec}</div>
              {products.map((product) => (
                <div key={product.id} className="p-4 text-center border-l">
                  {product.specs[spec] || '-'}
                </div>
              ))}
            </>
          ))}
        </div>
      </div>
    </div>
  )
}
