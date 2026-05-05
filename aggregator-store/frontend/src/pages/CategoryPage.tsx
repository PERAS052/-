import { useParams, Link } from 'react-router-dom'
import { Card, CardContent } from '@components/ui/card'
import { Skeleton } from '@components/ui/skeleton'

const mockProducts = [
  { id: 1, name: 'iPhone 15 Pro', slug: 'iphone-15-pro', brand: 'Apple', price: 999, image: 'https://images.unsplash.com/photo-1696446701796-da61225697cc?w=400' },
  { id: 2, name: 'MacBook Air M3', slug: 'macbook-air-m3', brand: 'Apple', price: 1099, image: 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400' },
  { id: 3, name: 'AirPods Pro 2', slug: 'airpods-pro-2', brand: 'Apple', price: 249, image: 'https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=400' },
  { id: 4, name: 'Samsung Galaxy S24', slug: 'samsung-galaxy-s24', brand: 'Samsung', price: 799, image: 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400' },
]

export function CategoryPage() {
  const { slug } = useParams<{ slug: string }>()
  
  return (
    <div className="container py-8">
      <h1 className="text-3xl font-bold mb-6 capitalize">{slug}</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {mockProducts.map((product) => (
          <Link key={product.id} to={`/product/${product.slug}`}>
            <Card className="overflow-hidden group hover:shadow-lg transition-shadow h-full">
              <div className="aspect-square overflow-hidden bg-muted">
                <img
                  src={product.image}
                  alt={product.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                />
              </div>
              <CardContent className="p-4">
                <p className="text-sm text-muted-foreground">{product.brand}</p>
                <h3 className="font-semibold line-clamp-2 mb-2">{product.name}</h3>
                <p className="text-lg font-bold">${product.price}</p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
