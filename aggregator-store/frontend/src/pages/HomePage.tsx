import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Button } from '@components/ui/button'
import { Card, CardContent } from '@components/ui/card'
import { Search, TrendingUp, Star, Clock } from 'lucide-react'

// Mock data для демонстрации
const categories = [
  { id: 1, name: 'Электроника', slug: 'electronics', image: 'https://images.unsplash.com/photo-1498049860654-af1a5c5668ba?w=400' },
  { id: 2, name: 'Мода', slug: 'fashion', image: 'https://images.unsplash.com/photo-1445205170230-053b83016050?w=400' },
  { id: 3, name: 'Дом и сад', slug: 'home', image: 'https://images.unsplash.com/photo-1484154218962-a197022b5858?w=400' },
  { id: 4, name: 'Спорт', slug: 'sports', image: 'https://images.unsplash.com/photo-1517649763962-0c623066013b?w=400' },
  { id: 5, name: 'Красота', slug: 'beauty', image: 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400' },
  { id: 6, name: 'Игрушки', slug: 'toys', image: 'https://images.unsplash.com/photo-1558060370-d644479cb6f7?w=400' },
]

const featuredProducts = [
  { id: 1, name: 'iPhone 15 Pro', slug: 'iphone-15-pro', brand: 'Apple', min_price: 999, max_price: 1199, rating: 4.8, image: 'https://images.unsplash.com/photo-1696446701796-da61225697cc?w=400' },
  { id: 2, name: 'Sony WH-1000XM5', slug: 'sony-wh1000xm5', brand: 'Sony', min_price: 299, max_price: 399, rating: 4.7, image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400' },
  { id: 3, name: 'MacBook Air M3', slug: 'macbook-air-m3', brand: 'Apple', min_price: 1099, max_price: 1299, rating: 4.9, image: 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400' },
  { id: 4, name: 'Samsung Galaxy S24', slug: 'samsung-galaxy-s24', brand: 'Samsung', min_price: 799, max_price: 999, rating: 4.6, image: 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400' },
]

export function HomePage() {
  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-r from-primary/10 to-primary/5 py-20">
        <div className="container">
          <div className="max-w-2xl">
            <h1 className="text-4xl md:text-5xl font-bold mb-6">
              Сравнивайте цены на товары из лучших маркетплейсов
            </h1>
            <p className="text-lg text-muted-foreground mb-8">
              AliExpress, Amazon, Wildberries, Ozon, Яндекс.Маркет — все цены в одном месте. 
              Экономьте до 30% на покупках!
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link to="/search">
                <Button size="lg" className="w-full sm:w-auto">
                  <Search className="mr-2 h-5 w-5" />
                  Найти товары
                </Button>
              </Link>
              <Link to="/category/electronics">
                <Button variant="outline" size="lg" className="w-full sm:w-auto">
                  Смотреть каталог
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Categories */}
      <section className="container">
        <h2 className="text-2xl font-bold mb-6">Популярные категории</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {categories.map((category) => (
            <Link key={category.id} to={`/category/${category.slug}`}>
              <Card className="overflow-hidden group hover:shadow-lg transition-shadow">
                <div className="aspect-square overflow-hidden">
                  <img
                    src={category.image}
                    alt={category.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                  />
                </div>
                <CardContent className="p-3">
                  <p className="font-medium text-center">{category.name}</p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </section>

      {/* Featured Products */}
      <section className="container">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">Рекомендуем для вас</h2>
          <Link to="/search" className="text-primary hover:underline">
            Смотреть все
          </Link>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {featuredProducts.map((product) => (
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
                  <div className="flex items-center gap-2 mb-2">
                    <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    <span className="text-sm">{product.rating}</span>
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-lg font-bold">${product.min_price}</span>
                    {product.max_price > product.min_price && (
                      <span className="text-sm text-muted-foreground line-through">
                        ${product.max_price}
                      </span>
                    )}
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="container py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-lg bg-primary/10">
              <TrendingUp className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold mb-2">Лучшие цены</h3>
              <p className="text-muted-foreground">
                Сравнивайте цены сразу из нескольких маркетплейсов и выбирайте выгодные предложения
              </p>
            </div>
          </div>
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-lg bg-primary/10">
              <Clock className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold mb-2">Экономия времени</h3>
              <p className="text-muted-foreground">
                Не тратьте время на поиск по разным сайтам — все товары в одном каталоге
              </p>
            </div>
          </div>
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-lg bg-primary/10">
              <Star className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold mb-2">Проверенные товары</h3>
              <p className="text-muted-foreground">
                Рейтинги, отзывы и реальные цены помогут сделать правильный выбор
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
