import { User, Mail, Phone, MapPin, Package, Heart } from 'lucide-react'
import { Button } from '@components/ui/button'
import { Card, CardContent } from '@components/ui/card'
import { Input } from '@components/ui/input'
import { useAuthStore } from '@stores/authStore'
import { Link } from 'react-router-dom'

export function ProfilePage() {
  const { user } = useAuthStore()

  return (
    <div className="container py-8">
      <h1 className="text-3xl font-bold mb-8">Личный кабинет</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Sidebar */}
        <div className="space-y-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
                  <User className="h-8 w-8 text-primary" />
                </div>
                <div>
                  <h2 className="font-semibold">{user?.full_name || 'Пользователь'}</h2>
                  <p className="text-sm text-muted-foreground">{user?.email}</p>
                </div>
              </div>
              
              <nav className="space-y-2">
                <Link to="/orders">
                  <Button variant="ghost" className="w-full justify-start">
                    <Package className="h-4 w-4 mr-2" />
                    Мои заказы
                  </Button>
                </Link>
                <Link to="/favorites">
                  <Button variant="ghost" className="w-full justify-start">
                    <Heart className="h-4 w-4 mr-2" />
                    Избранное
                  </Button>
                </Link>
              </nav>
            </CardContent>
          </Card>
        </div>

        {/* Profile Form */}
        <div className="md:col-span-2">
          <Card>
            <CardContent className="p-6">
              <h2 className="text-xl font-semibold mb-6">Персональные данные</h2>
              
              <form className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Имя</label>
                  <Input defaultValue={user?.full_name || ''} />
                </div>
                <div>
                  <label className="text-sm font-medium">Email</label>
                  <Input defaultValue={user?.email || ''} disabled />
                </div>
                <div>
                  <label className="text-sm font-medium">Телефон</label>
                  <Input placeholder="+7 (999) 123-45-67" />
                </div>
                <div>
                  <label className="text-sm font-medium">Адрес доставки</label>
                  <Input placeholder="Москва, ул. Примерная, 1" />
                </div>
                
                <Button>Сохранить изменения</Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
