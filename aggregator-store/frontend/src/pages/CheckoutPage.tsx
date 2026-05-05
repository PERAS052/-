import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { CreditCard, Truck } from 'lucide-react'
import { Button } from '@components/ui/button'
import { Card, CardContent } from '@components/ui/card'
import { Input } from '@components/ui/input'

export function CheckoutPage() {
  const navigate = useNavigate()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    // Simulate order creation
    await new Promise(resolve => setTimeout(resolve, 1500))
    navigate('/orders')
  }

  return (
    <div className="container py-8">
      <h1 className="text-3xl font-bold mb-8">Оформление заказа</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <form onSubmit={handleSubmit} className="space-y-6">
            <Card>
              <CardContent className="p-6">
                <h2 className="text-xl font-semibold mb-4">Контактная информация</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <Input placeholder="Имя" required />
                  <Input placeholder="Фамилия" required />
                  <Input placeholder="Email" type="email" required />
                  <Input placeholder="Телефон" required />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <Truck className="h-5 w-5" />
                  Адрес доставки
                </h2>
                <div className="space-y-4">
                  <Input placeholder="Город" required />
                  <Input placeholder="Улица, дом, квартира" required />
                  <Input placeholder="Почтовый индекс" required />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <CreditCard className="h-5 w-5" />
                  Оплата (симуляция)
                </h2>
                <p className="text-muted-foreground text-sm mb-4">
                  Для демонстрации оплата не требуется. Заказ будет создан сразу.
                </p>
              </CardContent>
            </Card>

            <Button type="submit" className="w-full" size="lg" disabled={isSubmitting}>
              {isSubmitting ? 'Создание заказа...' : 'Подтвердить заказ'}
            </Button>
          </form>
        </div>

        <div className="lg:col-span-1">
          <Card className="sticky top-24">
            <CardContent className="p-6">
              <h2 className="font-semibold text-lg mb-4">Ваш заказ</h2>
              <div className="space-y-2 mb-4">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Товары</span>
                  <span>$999</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Доставка</span>
                  <span className="text-green-600">Бесплатно</span>
                </div>
                <div className="border-t pt-2 flex justify-between font-bold text-lg">
                  <span>Итого</span>
                  <span>$999</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
