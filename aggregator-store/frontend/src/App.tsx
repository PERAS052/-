import { Routes, Route } from 'react-router-dom'
import { Header } from '@components/layout/Header'
import { Footer } from '@components/layout/Footer'
import { HomePage } from '@pages/HomePage'
import { SearchPage } from '@pages/SearchPage'
import { ProductPage } from '@pages/ProductPage'
import { CategoryPage } from '@pages/CategoryPage'
import { CartPage } from '@pages/CartPage'
import { FavoritesPage } from '@pages/FavoritesPage'
import { ComparisonPage } from '@pages/ComparisonPage'
import { OrdersPage } from '@pages/OrdersPage'
import { ProfilePage } from '@pages/ProfilePage'
import { LoginPage } from '@pages/LoginPage'
import { RegisterPage } from '@pages/RegisterPage'
import { AdminDashboard } from '@pages/Admin/Dashboard'
import { CheckoutPage } from '@pages/CheckoutPage'

function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/product/:slug" element={<ProductPage />} />
          <Route path="/category/:slug" element={<CategoryPage />} />
          <Route path="/cart" element={<CartPage />} />
          <Route path="/checkout" element={<CheckoutPage />} />
          <Route path="/favorites" element={<FavoritesPage />} />
          <Route path="/compare" element={<ComparisonPage />} />
          <Route path="/orders" element={<OrdersPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/admin/*" element={<AdminDashboard />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}

export default App
