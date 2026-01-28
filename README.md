# MasterBot Platform

Централизованная платформа для управления Telegram-ботами с микросервисной архитектурой.

## Архитектура

```
masterbot-platform/
├── master_bot/          # Основной Telegram бот (aiogram 3.x)
├── impulse_service/     # Сервис импульсов (FastAPI)
├── shared/              # Общие модули (схемы, база данных, константы)
├── scripts/             # Утилиты и скрипты
└── docker-compose.yml   # Оркестрация контейнеров
```

### Сервисы

- **Master Bot** — Telegram бот для взаимодействия с пользователями
- **Impulse Service** — Сбор и анализ торговых импульсов из Telegram-канала
- **PostgreSQL** — База данных
- **Redis** — Кэширование и pub/sub

## Требования

- Docker & Docker Compose
- Python 3.11+ (для локальной разработки)

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/SergiusArt/masterbot-platform.git
cd masterbot-platform
```

### 2. Настройка окружения

```bash
cp .env.example .env
```

Заполните `.env` своими значениями:

```env
# Telegram Bot
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_id_here

# Database
DB_USER=masterbot
DB_PASSWORD=your_secure_password
DB_NAME=masterbot_db

# Impulse Service - Telegram Listener
SOURCE_CHANNEL_ID=your_channel_id_here
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_SESSION_STRING=your_session_string_here
```

### 3. Запуск

```bash
docker compose up -d
```

### 4. Проверка статуса

```bash
docker compose ps
docker compose logs -f
```

## Разработка

### Локальное окружение (тестовый бот)

Используйте `.env` с токеном тестового бота для локальной разработки.

### Продакшн окружение

Создайте `.env.production` с продакшн-токенами и запустите:

```bash
docker compose --env-file .env.production up -d
```

## Функциональность

### Импульсы

- Автоматический сбор сигналов из Telegram-канала
- Аналитика по периодам (день, неделя, месяц)
- Настраиваемые пороги уведомлений
- Автоматические отчеты (утренний, вечерний, недельный, месячный)

### Администрирование

- Управление пользователями
- Контроль доступа по времени
- Статистика использования

## API Endpoints

Impulse Service доступен на порту `8001`:

- `GET /health` — Проверка здоровья сервиса
- `GET /api/impulses` — Список импульсов
- `GET /api/analytics/{period}` — Аналитика за период
- `GET /api/settings/{user_id}` — Настройки пользователя
- `PUT /api/settings/{user_id}` — Обновление настроек

## Технологии

- **Python 3.11**
- **aiogram 3.x** — Telegram Bot API
- **FastAPI** — REST API
- **SQLAlchemy 2.0** — Async ORM
- **PostgreSQL 15** — База данных
- **Redis 7** — Кэширование
- **Telethon** — Telegram MTProto API
- **Docker Compose** — Оркестрация

## Лицензия

Private / All rights reserved
