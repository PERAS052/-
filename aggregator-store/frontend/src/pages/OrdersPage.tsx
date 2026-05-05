import { Package, CheckCircle, XCircle, Clock } from 'lucide-react'
import { Card, CardContent } from '@components/ui/card'
import { Button } from '@components/ui/button'
import { useState } from 'react'

interface Order {
  id: number
  order_number: string
  status: 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled'
  total_amount: number
  created_at: string
  items: { name: string; quantity: number; price: number }[]
}

const statusMap = {
  pending: { label: 'Ожидает оплаты', icon: Clock, color: 'text-yellow-500' },
  processing: { label: 'Обрабатывается', icon: Package, color: 'text-blue-500' },
  shipped: { label: 'В пути', icon: Package, color: 'text-purple-500' },
  delivered: { label: 'Доставлен', icon: CheckCircle, color: 'text-green-500' },
  cancelled: { label: 'Отменен', icon: XCircle, color: 'text-red-500' },
}

export function OrdersPage() {
  const [orders] = useState<Order[]>([
    {
      id: 1,
      order_number: 'ORD-001',
      status: 'delivered',
      total_amount: 999,
      created_at: '2024-01-15',
      items: [{ name: 'iPhone 15 Pro', quantity: 1, price: 999 }],
    },
  ])

  return (
    <div className="container py-8">
      <h1 className="text-3xl font-bold mb-8">Мои заказы</h1>
      
      <div className="space-y-4">
        {orders.map((order) => {
          const StatusIcon = statusMap[order.status].icon
          return (
            <Card key={order.id}>
              <CardContent className="p-6">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
                  <div>
                    <p className="text-sm text-muted-foreground">№ {order.order_number}</p>
                    <p className="text-sm text-muted-foreground">{order.created_at}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <StatusIcon className={`h-5 w-5 ${statusMap[order.status].color}`} />
                    <span>{statusMap[order.status].label}</span>
                  </div>
                </div>
                
                <div className="border-t pt-4">
                  {order.items.map((item, idx) => (
                    <div key={idx} className="flex justify-between py-2">
                      <span>{item.name} x{item.quantity}</span>
                      <span>${item.price}</span>
                    </div>
                  ))}
                  <div className="border-t pt-2 flex justify-between font-bold">
                    <span>Итого</span>
                    <span>${order.total_amount}</span>
                  </div>
                </div>

                <div className="flex gap-2 mt-4">
                  <Button variant="outline" size="sm">Детали</Button>
                  {order.status === 'pending' && (
                    <Button variant="destructive" size="sm">Отменить</Button>
                  )}
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
