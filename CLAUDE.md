# MasterBot Platform - Claude AI Assistant Guide

## Project Overview

**MasterBot Platform** - это микросервисная платформа для мониторинга и уведомлений о торговых сигналах из Telegram каналов. Система состоит из трёх основных сервисов, работающих в Docker контейнерах.

### Core Services

1. **impulse_service** (порт 8001) - отслеживает импульсные движения криптовалют
2. **bablo_service** (порт 8002) - отслеживает торговые сигналы Bablo
3. **master_bot** - основной Telegram бот для взаимодействия с пользователями

### Infrastructure

- **PostgreSQL** (порт 5433) - хранение данных
- **Redis** (порт 6379) - pub/sub для межсервисной коммуникации

## Architecture

```
┌─────────────────┐         ┌─────────────────┐
│ Telegram Channel│         │ Telegram Channel│
│   (Impulses)    │         │    (Bablo)      │
└────────┬────────┘         └────────┬────────┘
         │                           │
         ▼                           ▼
┌─────────────────┐         ┌─────────────────┐
│ impulse_service │         │  bablo_service  │
│  - Telethon     │         │  - Telethon     │
│  - Parser       │         │  - Parser       │
│  - FastAPI      │         │  - FastAPI      │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │        ┌──────────┐       │
         └───────►│  Redis   │◄──────┘
                  │ (pub/sub)│
                  └────┬─────┘
                       │
                       ▼
                ┌─────────────┐
                │ master_bot  │
                │  - aiogram  │
                └──────┬──────┘
                       │
                       ▼
                 ┌──────────┐
                 │PostgreSQL│
                 └──────────┘
```

## Critical Technical Details

### 1. Telethon Events Handler

**ВАЖНО:** При регистрации обработчика событий в Telethon, параметр `chats` ДОЛЖЕН быть списком:

```python
# ✅ ПРАВИЛЬНО
@client.on(events.NewMessage(chats=[channel_id]))

# ❌ НЕПРАВИЛЬНО
@client.on(events.NewMessage(chats=channel_id))
```

Если передать число вместо списка, обработчик не будет срабатывать, и сообщения не будут получены.

### 2. Docker Environment Variables

При изменении переменных окружения в `.env`:
- `docker compose restart` - НЕ подхватывает новые переменные
- `docker compose up -d` - ПОДХВАТЫВАЕТ новые переменные (пересоздает контейнер)

### 3. Redis Pub/Sub Data Format

Данные в Redis публикуются в JSON формате:

```python
await redis.publish(channel, {
    "event": "event_type",
    "user_id": 123456,
    "data": {
        # event specific data
    }
})
```

Redis client автоматически сериализует dict в JSON строку.

### 4. Database Timezone

PostgreSQL хранит время в UTC. При фильтрации по времени учитывайте часовой пояс:
- Локальное время (МСК): UTC+3
- При удалении/фильтрации записей конвертируйте время в UTC

## Recent Fixes (January 2026)

### Impulse Service Fixes

1. **Critical Bug Fix** - Telegram handler не срабатывал
   - Файл: `impulse_service/telegram_listener/listener.py:76`
   - Изменение: `chats=settings.SOURCE_CHANNEL_ID` → `chats=[settings.SOURCE_CHANNEL_ID]`
   - Причина: Telethon требует список, а не число

2. **Parser Enhancement** - добавлена поддержка emoji формата
   - Файл: `impulse_service/core/parser.py`
   - Паттерн: `r"[🟢🔴]\s*([A-Z0-9]+(?:USDT|BUSD)?\.?P?)\s*([+-]?\d+\.?\d*)%"`

### Bablo Service Fixes

1. **Removed Strength Filtering**
   - Файл: `bablo_service/services/notification_service.py:95`
   - Убран фильтр: `BabloUserSettings.min_strength <= strength`
   - Причина: пользователи хотят получать все сигналы независимо от силы

2. **Fixed Quality Field Name**
   - Файл: `bablo_service/telegram_listener/listener.py:147`
   - Изменение: `"quality"` → `"quality_total"`
   - Причина: несоответствие с notification_listener

3. **Added Detailed Logging**
   - Handler triggers: `🔥 BABLO HANDLER TRIGGERED!`
   - Message processing: `📩 Processing Bablo message`
   - Parsed signals: `✅ Parsed Bablo signal`

## Project Structure

```
masterbot-platform/
├── impulse_service/
│   ├── telegram_listener/
│   │   └── listener.py          # Telethon listener для импульсов
│   ├── core/
│   │   └── parser.py            # Парсер импульсных сообщений
│   ├── services/
│   │   ├── impulse_service.py   # Бизнес-логика импульсов
│   │   └── notification_service.py
│   └── models/
│       └── impulse.py           # SQLAlchemy модели
│
├── bablo_service/
│   ├── telegram_listener/
│   │   └── listener.py          # Telethon listener для Bablo
│   ├── core/
│   │   └── parser.py            # Парсер Bablo сигналов
│   ├── services/
│   │   ├── signal_service.py    # Бизнес-логика сигналов
│   │   └── notification_service.py
│   └── models/
│       └── bablo.py             # SQLAlchemy модели
│
├── master_bot/
│   ├── services/
│   │   └── notification_listener.py  # Redis listener для уведомлений
│   ├── handlers/                # Telegram bot handlers
│   └── models/                  # User models
│
├── shared/
│   ├── utils/
│   │   ├── redis_client.py     # Redis wrapper
│   │   └── logger.py           # Logging utils
│   ├── database/
│   │   └── connection.py       # Database connection
│   └── constants.py            # Shared constants
│
├── scripts/
│   ├── backfill_impulses.py    # Восстановление пропущенных импульсов
│   └── test_bablo_notification.py
│
├── .env                        # Environment variables (local)
├── .env.production            # Environment variables (production)
└── docker-compose.yml
```

## Environment Configuration

### Local Development

- Impulse Channel: `-1002313787119` (SrgArt Impulse)
- Bablo Channel: `-1001628431640`
- Test Channel: `-1001801996686`

### Production Server

- IP: `178.212.12.186`
- User: `root`
- Project Path: `/root/masterbot-platform`

## Database Models

### Impulse Service

```python
class Impulse:
    id: int
    symbol: str
    percent: float
    type: str  # 'growth' or 'decline'
    received_at: datetime (UTC)
    telegram_message_id: bigint
```

### Bablo Service

```python
class BabloSignal:
    id: int
    symbol: str
    direction: str  # 'long' or 'short'
    strength: int  # 1-5
    timeframe: str  # '1m', '15m', '1h', '4h'
    quality_total: int  # 0-10
    quality_profit: int
    quality_drawdown: int
    quality_accuracy: int
    probabilities: jsonb
    max_drawdown: Decimal
    received_at: datetime (UTC)
```

### User Settings

```python
class BabloUserSettings:
    user_id: int
    notifications_enabled: bool
    min_quality: int  # Minimum quality (0-10)
    # NOTE: min_strength field exists but NOT used for filtering
    timeframe_1m: bool
    timeframe_15m: bool
    timeframe_1h: bool
    timeframe_4h: bool
    long_signals: bool
    short_signals: bool
```

## Deployment Process

### Local Testing

```bash
# 1. Start services
docker compose up -d

# 2. Check logs
docker compose logs -f [service_name]

# 3. Test with test channel
# Edit .env: SOURCE_CHANNEL_ID=-1001801996686
docker compose up -d impulse_service
```

### Production Deployment

```bash
# On local machine:
git add .
git commit -m "Description"
git push origin main

# On production server (178.212.12.186):
ssh root@178.212.12.186
cd masterbot-platform
git pull origin main
docker compose up -d --build [service_name]

# Verify deployment
docker compose logs [service_name] --tail=20
docker compose ps
```

## Common Issues & Solutions

### Issue 1: Telegram Handler Not Triggering

**Symptoms:** Listener starts, but no messages are received

**Solution:** Check that `chats` parameter is a list:
```python
@client.on(events.NewMessage(chats=[channel_id]))  # ✅
```

### Issue 2: Environment Variables Not Updated

**Symptoms:** Changed `.env` but service still uses old values

**Solution:** Use `docker compose up -d` instead of `restart`:
```bash
docker compose up -d service_name  # Recreates container
```

### Issue 3: Notifications Not Arriving

**Checklist:**
1. Check user settings (notifications_enabled, filters)
2. Verify Redis pub/sub (check logs)
3. Check master_bot Redis subscription
4. Verify field names match (quality vs quality_total)

### Issue 4: Database Time Mismatch

**Solution:** Always use UTC for database queries:
```python
# Local time: 10:25 MSK → UTC: 07:25
WHERE received_at > '2026-01-30 07:25:00'  # ✅ UTC
```

## Testing Checklist

### Impulse Service Test
- [ ] Handler triggers on test message
- [ ] Parser recognizes format
- [ ] Impulse saved to DB
- [ ] Notification sent to Redis
- [ ] User receives Telegram message

### Bablo Service Test
- [ ] Handler triggers on test message
- [ ] Parser recognizes format
- [ ] Signal saved to DB with correct quality
- [ ] Strength filter NOT applied
- [ ] quality_total field correct
- [ ] Notification sent to Redis
- [ ] User receives Telegram message

## Key Contacts & Resources

- Repository: `https://github.com/SergiusArt/masterbot-platform.git`
- Production Server: `178.212.12.186`
- Telegram Bot: `@srgart_summary_bot`

## Notes for Future Development

1. **Parser Patterns:** Keep regex patterns updated when message format changes
2. **Logging:** Use emoji markers for easy log filtering (🔥, 📩, ✅, ⚠️)
3. **Error Handling:** Always log exceptions with `exc_info=True` for stack traces
4. **Testing:** Test on test channel before deploying to production
5. **Backfill:** Use `/app/scripts/backfill_impulses.py` to restore missing data

---

Last Updated: January 30, 2026
