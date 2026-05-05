import { Link } from 'react-router-dom'
import { LayoutDashboard, ShoppingBag, Users, Settings, BarChart3 } from 'lucide-react'
import { Button } from '@components/ui/button'
import { Card, CardContent } from '@components/ui/card'

export function AdminDashboard() {
  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="w-64 border-r bg-muted/10">
        <div className="p-6">
          <h2 className="font-bold text-lg">Admin Panel</h2>
        </div>
        <nav className="px-4 space-y-2">
          <Button variant="ghost" className="w-full justify-start">
            <LayoutDashboard className="h-4 w-4 mr-2" />
            Dashboard
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            <ShoppingBag className="h-4 w-4 mr-2" />
            Товары
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            <Users className="h-4 w-4 mr-2" />
            Пользователи
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            <BarChart3 className="h-4 w-4 mr-2" />
            Аналитика
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            <Settings className="h-4 w-4 mr-2" />
            Настройки
          </Button>
        </nav>
      </aside>

      {/* Content */}
      <main className="flex-1 p-8">
        <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <p className="text-muted-foreground text-sm">Всего товаров</p>
              <p className="text-3xl font-bold">1,234</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <p className="text-muted-foreground text-sm">Пользователей</p>
              <p className="text-3xl font-bold">567</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <p className="text-muted-foreground text-sm">Заказов</p>
              <p className="text-3xl font-bold">89</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <p className="text-muted-foreground text-sm">Выручка</p>
              <p className="text-3xl font-bold">$45,678</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardContent className="p-6">
              <h3 className="font-semibold mb-4">Последние заказы</h3>
              <p className="text-muted-foreground">Здесь будет список заказов</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <h3 className="font-semibold mb-4">Популярные товары</h3>
              <p className="text-muted-foreground">Здесь будет список товаров</p>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
