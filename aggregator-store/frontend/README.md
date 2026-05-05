# Aggregator Store Frontend

React + TypeScript + Vite + TailwindCSS приложение для агрегатора товаров.

## Технологии

- **React 18** - UI библиотека
- **TypeScript** - типизация
- **Vite** - сборщик
- **TailwindCSS** - стилизация
- **shadcn/ui** - компоненты интерфейса
- **React Router DOM** - роутинг
- **Zustand** - state management
- **TanStack Query** - работа с API
- **Axios** - HTTP клиент
- **Lucide React** - иконки

## Структура проекта

```
src/
├── components/
│   ├── ui/           # UI компоненты (Button, Input, Card, Skeleton)
│   └── layout/       # Layout компоненты (Header, Footer)
├── pages/            # Страницы приложения
│   ├── Admin/        # Админ панель
│   ├── CartPage.tsx
│   ├── CategoryPage.tsx
│   ├── CheckoutPage.tsx
│   ├── ComparisonPage.tsx
│   ├── FavoritesPage.tsx
│   ├── HomePage.tsx
│   ├── LoginPage.tsx
│   ├── OrdersPage.tsx
│   ├── ProductPage.tsx
│   ├── ProfilePage.tsx
│   ├── RegisterPage.tsx
│   └── SearchPage.tsx
├── services/         # API сервисы
├── stores/           # Zustand сторы
├── lib/              # Утилиты
├── App.tsx           # Главный компонент
├── main.tsx          # Точка входа
└── index.css         # Глобальные стили
```

## Доступные страницы

- `/` - Главная страница
- `/search` - Поиск товаров
- `/product/:slug` - Страница товара
- `/category/:slug` - Страница категории
- `/cart` - Корзина
- `/checkout` - Оформление заказа
- `/favorites` - Избранное
- `/compare` - Сравнение товаров
- `/orders` - История заказов
- `/profile` - Профиль пользователя
- `/login` - Вход
- `/register` - Регистрация
- `/admin/*` - Админ панель

## Запуск

### Локальная разработка

```bash
npm install
npm run dev
```

### Docker

```bash
docker build -t aggregator-frontend .
docker run -p 80:80 aggregator-frontend
```

### Через docker-compose (рекомендуется)

```bash
cd ..
docker-compose up frontend
```

## Переменные окружения

Создайте `.env` файл:

```
VITE_API_URL=http://localhost:8000/api/v1
```

## Скрипты

- `npm run dev` - запуск dev сервера
- `npm run build` - сборка production
- `npm run preview` - preview сборки
- `npm run lint` - проверка линтером
