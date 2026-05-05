# Aggregator Store

Современный агрегатор товаров международных маркетплейсов (AliExpress, Amazon, Wildberries, Ozon, Яндекс.Маркет и др.)

## Технологический стек

- **Backend**: Python 3.12 + FastAPI + SQLAlchemy 2.0 + Alembic
- **Frontend**: React 18 + TypeScript + Vite + TailwindCSS + shadcn/ui
- **Database**: PostgreSQL 16 + Redis
- **ML**: scikit-learn (рекомендательная система)
- **Containerization**: Docker + docker-compose

## Функционал

- Агрегация товаров из разных маркетплейсов
- Продвинутый поиск с автодополнением и фильтрами
- ML-рекомендации ("Похожие товары", "Рекомендуем для вас")
- Сравнение до 4 товаров
- Личный кабинет, избранное, история просмотров
- Корзина и оформление заказа
- Админ-панель для управления

## Быстрый старт

### Предварительные требования

- Docker и docker-compose установлены
- Git

### Запуск проекта

1. **Клонировать репозиторий**:
   ```bash
   git clone <repository-url>
   cd aggregator-store
   ```

2. **Настроить окружение**:
   ```bash
   cp .env.example .env
   # Отредактируйте .env, установите SECRET_KEY и пароли
   ```

3. **Запустить сервисы**:
   ```bash
   docker-compose up -d
   ```

4. **Применить миграции**:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Создать тестовые данные** (опционально):
   ```bash
   docker-compose exec backend python -m app.scripts.seed
   ```

6. **Открыть приложение**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Разработка без Docker

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Структура проекта

```
aggregator-store/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # API роуты
│   │   ├── models/   # SQLAlchemy модели
│   │   ├── schemas/  # Pydantic схемы
│   │   ├── services/ # Бизнес-логика
│   │   └── core/     # Ядро (безопасность, конфиг)
│   └── migrations/   # Alembic миграции
├── frontend/         # React frontend
│   └── src/
│       ├── components/
│       ├── pages/
│       └── services/
└── docker-compose.yml
```

## API Endpoints

### Аутентификация
- `POST /api/v1/auth/register` - Регистрация
- `POST /api/v1/auth/login` - Вход
- `POST /api/v1/auth/refresh` - Обновление токена
- `GET /api/v1/auth/me` - Профиль пользователя

### Товары
- `GET /api/v1/products` - Список товаров
- `GET /api/v1/products/{slug}` - Детали товара
- `GET /api/v1/search` - Поиск с фильтрами
- `GET /api/v1/search/autocomplete` - Автодополнение

### Пользовательские
- `GET /api/v1/favorites` - Избранное
- `POST /api/v1/favorites/{product_id}` - Добавить в избранное
- `GET /api/v1/cart` - Корзина
- `POST /api/v1/cart` - Добавить в корзину
- `POST /api/v1/orders` - Оформить заказ
- `GET /api/v1/orders` - История заказов
- `GET /api/v1/recommendations` - ML-рекомендации
- `POST /api/v1/comparison` - Добавить к сравнению

### Админ
- `GET /api/v1/admin/dashboard` - Статистика
- `CRUD /api/v1/admin/products` - Управление товарами
- `CRUD /api/v1/admin/categories` - Управление категориями
- `CRUD /api/v1/admin/users` - Управление пользователями

## Роли пользователей

- **client** - обычный пользователь (покупатель)
- **manager** - менеджер (управление товарами)
- **admin** - полный доступ

## Лицензия

MIT License
