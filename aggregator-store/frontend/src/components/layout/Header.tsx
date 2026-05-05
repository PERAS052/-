import { Link } from 'react-router-dom'
import { Search, ShoppingCart, Heart, User, Menu, X } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@components/ui/button'
import { Input } from '@components/ui/input'
import { useAuthStore } from '@stores/authStore'

export function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const { isAuthenticated, user, logout } = useAuthStore()

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      window.location.href = `/search?q=${encodeURIComponent(searchQuery)}`
    }
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center">
        {/* Logo */}
        <Link to="/" className="mr-6 flex items-center space-x-2">
          <span className="text-xl font-bold text-primary">Aggregator Store</span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-6 text-sm font-medium flex-1">
          <Link to="/" className="transition-colors hover:text-primary">
            Главная
          </Link>
          <Link to="/search" className="transition-colors hover:text-primary">
            Каталог
          </Link>
          <Link to="/category/electronics" className="transition-colors hover:text-primary">
            Электроника
          </Link>
          <Link to="/category/fashion" className="transition-colors hover:text-primary">
            Мода
          </Link>
        </nav>

        {/* Search */}
        <form onSubmit={handleSearch} className="hidden md:flex items-center mr-4">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Поиск товаров..."
              className="w-[300px] pl-8"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </form>

        {/* Actions */}
        <div className="flex items-center space-x-4">
          <Link to="/favorites" className="hidden md:flex">
            <Button variant="ghost" size="icon">
              <Heart className="h-5 w-5" />
            </Button>
          </Link>
          
          <Link to="/cart">
            <Button variant="ghost" size="icon" className="relative">
              <ShoppingCart className="h-5 w-5" />
              <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-primary text-[10px] font-medium text-primary-foreground flex items-center justify-center">
                0
              </span>
            </Button>
          </Link>

          {isAuthenticated ? (
            <div className="hidden md:flex items-center space-x-2">
              <Link to="/profile">
                <Button variant="ghost" size="icon">
                  <User className="h-5 w-5" />
                </Button>
              </Link>
              <Button variant="ghost" size="sm" onClick={logout}>
                Выйти
              </Button>
            </div>
          ) : (
            <div className="hidden md:flex items-center space-x-2">
              <Link to="/login">
                <Button variant="ghost" size="sm">Вход</Button>
              </Link>
              <Link to="/register">
                <Button size="sm">Регистрация</Button>
              </Link>
            </div>
          )}

          {/* Mobile menu button */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="md:hidden border-t bg-background">
          <div className="container py-4 space-y-4">
            <form onSubmit={handleSearch} className="flex items-center">
              <div className="relative w-full">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  type="search"
                  placeholder="Поиск товаров..."
                  className="w-full pl-8"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </form>
            
            <nav className="flex flex-col space-y-2">
              <Link to="/" className="px-2 py-2 hover:bg-accent rounded-md" onClick={() => setIsMenuOpen(false)}>
                Главная
              </Link>
              <Link to="/search" className="px-2 py-2 hover:bg-accent rounded-md" onClick={() => setIsMenuOpen(false)}>
                Каталог
              </Link>
              <Link to="/favorites" className="px-2 py-2 hover:bg-accent rounded-md" onClick={() => setIsMenuOpen(false)}>
                Избранное
              </Link>
              <Link to="/cart" className="px-2 py-2 hover:bg-accent rounded-md" onClick={() => setIsMenuOpen(false)}>
                Корзина
              </Link>
              {isAuthenticated ? (
                <>
                  <Link to="/profile" className="px-2 py-2 hover:bg-accent rounded-md" onClick={() => setIsMenuOpen(false)}>
                    Профиль
                  </Link>
                  <button onClick={() => { logout(); setIsMenuOpen(false); }} className="px-2 py-2 hover:bg-accent rounded-md text-left">
                    Выйти
                  </button>
                </>
              ) : (
                <>
                  <Link to="/login" className="px-2 py-2 hover:bg-accent rounded-md" onClick={() => setIsMenuOpen(false)}>
                    Вход
                  </Link>
                  <Link to="/register" className="px-2 py-2 hover:bg-accent rounded-md" onClick={() => setIsMenuOpen(false)}>
                    Регистрация
                  </Link>
                </>
              )}
            </nav>
          </div>
        </div>
      )}
    </header>
  )
}
