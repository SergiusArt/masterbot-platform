# Mini App Gateway

WebSocket gateway для Telegram Mini App. Обеспечивает real-time обновления из Redis pub/sub.

## Запуск

### Локально (для разработки)

```bash
# Создать виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Установить переменные окружения
export BOT_TOKEN="your_bot_token"
export REDIS_URL="redis://localhost:6379/0"
export IMPULSE_SERVICE_URL="http://localhost:8001"
export BABLO_SERVICE_URL="http://localhost:8002"

# Запустить
python -m uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

### Docker

```bash
docker compose -f docker-compose.miniapp.yml up miniapp_gateway
```

## API

### Health Check
```
GET /health
```

### Dashboard Summary
```
GET /api/v1/dashboard/summary
```

### Impulses
```
GET /api/v1/dashboard/impulses?limit=20&offset=0
```

### Bablo Signals
```
GET /api/v1/dashboard/bablo?limit=20&direction=long&timeframe=5m
```

### Analytics
```
GET /api/v1/dashboard/analytics/{service}/{period}
# service: impulse | bablo
# period: today | yesterday | week | month
```

## WebSocket

### Подключение (Production)
```
ws://host:8003/ws?initData=<telegram_init_data>
```

### Подключение (Dev)
```
ws://host:8003/ws/dev
```

### Сообщения от сервера

```json
{"type": "connected", "data": {"user_id": 123, "message": "..."}, "timestamp": "..."}
{"type": "impulse:new", "data": {...}, "timestamp": "..."}
{"type": "bablo:new", "data": {...}, "timestamp": "..."}
{"type": "pong", "data": {}, "timestamp": "..."}
```

### Сообщения от клиента

```
ping                           # Heartbeat
{"type": "subscribe", "channel": "impulses"}
{"type": "unsubscribe", "channel": "impulses"}
```

## Аутентификация

Gateway валидирует Telegram initData используя HMAC-SHA256:
1. Парсит query string из initData
2. Извлекает hash
3. Сортирует оставшиеся параметры
4. Вычисляет HMAC с секретным ключом = HMAC-SHA256("WebAppData", bot_token)
5. Сравнивает хеши
6. Проверяет auth_date на свежесть (max 24 часа)
