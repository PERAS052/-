import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Search, Filter, SlidersHorizontal } from 'lucide-react'
import { Button } from '@components/ui/button'
import { Input } from '@components/ui/input'
import { Card, CardContent } from '@components/ui/card'
import { useQuery } from '@tanstack/react-query'
import api from '@services/api'

interface Product {
  id: number
  name: string
  slug: string
  brand: string
  images: string[]
  rating: number
  review_count: number
  min_price: number | null
  max_price: number | null
}

export function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [query, setQuery] = useState(searchParams.get('q') || '')
  const [isFilterOpen, setIsFilterOpen] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['search', searchParams.toString()],
    queryFn: async () => {
      const response = await api.get('/search', { params: Object.fromEntries(searchParams) })
      return response.data
    },
  })

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      setSearchParams({ q: query })
    }
  }

  return (
    <div className="container py-8">
      {/* Search Bar */}
      <form onSubmit={handleSearch} className="mb-8">
        <div className="relative max-w-2xl">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
          <Input
            className="pl-10 h-12 text-lg"
            placeholder="Поиск товаров..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <Button type="submit" className="absolute right-1 top-1/2 -translate-y-1/2">
            Найти
          </Button>
        </div>
      </form>

      <div className="flex gap-8">
        {/* Filters Sidebar */}
        <aside className={`w-64 flex-shrink-0 ${isFilterOpen ? 'block' : 'hidden md:block'}`}>
          <div className="sticky top-24 space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">Фильтры</h3>
              <Button variant="ghost" size="sm" className="md:hidden" onClick={() => setIsFilterOpen(false)}>
                ✕
              </Button>
            </div>

            {/* Price Range */}
            <div>
              <h4 className="font-medium mb-3">Цена</h4>
              <div className="flex gap-2">
                <Input type="number" placeholder="От" />
                <Input type="number" placeholder="До" />
              </div>
            </div>

            {/* Brands */}
            <div>
              <h4 className="font-medium mb-3">Бренды</h4>
              <div className="space-y-2">
                {['Apple', 'Samsung', 'Sony', 'Xiaomi'].map((brand) => (
                  <label key={brand} className="flex items-center gap-2 text-sm">
                    <input type="checkbox" className="rounded" />
                    {brand}
                  </label>
                ))}
              </div>
            </div>

            {/* Rating */}
            <div>
              <h4 className="font-medium mb-3">Рейтинг</h4>
              <div className="space-y-2">
                {['4.5 и выше', '4.0 и выше', '3.0 и выше'].map((rating) => (
                  <label key={rating} className="flex items-center gap-2 text-sm">
                    <input type="checkbox" className="rounded" />
                    {rating}
                  </label>
                ))}
              </div>
            </div>
          </div>
        </aside>

        {/* Results */}
        <div className="flex-1">
          {/* Toolbar */}
          <div className="flex items-center justify-between mb-6">
            <div className="text-sm text-muted-foreground">
              {isLoading ? 'Загрузка...' : `Найдено ${data?.total || 0} товаров`}
            </div>
            <div className="flex items-center gap-4">
              <Button variant="outline" size="sm" className="md:hidden" onClick={() => setIsFilterOpen(true)}>
                <SlidersHorizontal className="h-4 w-4 mr-2" />
                Фильтры
              </Button>
              <select className="text-sm border rounded-md px-3 py-2">
                <option>По популярности</option>
                <option>Сначала дешевле</option>
                <option>Сначала дороже</option>
                <option>По рейтингу</option>
              </select>
            </div>
          </div>

          {/* Products Grid */}
          {isLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <Card key={i} className="animate-pulse">
                  <div className="aspect-square bg-muted" />
                  <CardContent className="p-4 space-y-2">
                    <div className="h-4 bg-muted rounded w-1/4" />
                    <div className="h-4 bg-muted rounded" />
                    <div className="h-6 bg-muted rounded w-1/2" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : data?.items?.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {data.items.map((product: Product) => (
                <a key={product.id} href={`/product/${product.slug}`}>
                  <Card className="overflow-hidden group hover:shadow-lg transition-shadow h-full">
                    <div className="aspect-square overflow-hidden bg-muted">
                      <img
                        src={product.images[0] || 'https://via.placeholder.com/400'}
                        alt={product.name}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                      />
                    </div>
                    <CardContent className="p-4">
                      <p className="text-sm text-muted-foreground">{product.brand}</p>
                      <h3 className="font-semibold line-clamp-2 mb-2">{product.name}</h3>
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-sm">⭐ {product.rating}</span>
                        <span className="text-sm text-muted-foreground">({product.review_count})</span>
                      </div>
                      <div className="flex items-baseline gap-2">
                        {product.min_price ? (
                          <span className="text-lg font-bold">${product.min_price}</span>
                        ) : (
                          <span className="text-muted-foreground">Нет в наличии</span>
                        )}
                        {product.max_price && product.max_price > product.min_price! && (
                          <span className="text-sm text-muted-foreground line-through">
                            ${product.max_price}
                          </span>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </a>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-muted-foreground">Ничего не найдено</p>
              <p className="text-sm text-muted-foreground mt-2">
                Попробуйте изменить поисковый запрос или фильтры
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
