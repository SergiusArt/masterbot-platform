# Check Service Status

Проверка статуса всех сервисов на продакшн сервере.

## Что проверяется

1. **Docker контейнеры** — запущены ли все сервисы
2. **Health endpoints** — отвечают ли API сервисов
3. **Redis** — работает ли pub/sub
4. **Database** — подключение к PostgreSQL

## Команды

### Статус контейнеров

```bash
ssh impulse "cd /root/masterbot-platform && docker compose ps"
```

### Health checks

```bash
# Impulse Service
ssh impulse "curl -s http://localhost:8001/health | jq"

# Bablo Service
ssh impulse "curl -s http://localhost:8002/health | jq"
```

### Redis ping

```bash
ssh impulse "docker compose exec redis redis-cli PING"
```

### Database check

```bash
ssh impulse "docker compose exec postgres psql -U masterbot -d masterbot_db -c 'SELECT COUNT(*) FROM impulses;'"
ssh impulse "docker compose exec postgres psql -U masterbot -d masterbot_db -c 'SELECT COUNT(*) FROM bablo_signals;'"
```

### Последние записи в БД

```bash
# Последние 5 импульсов
ssh impulse "docker compose exec postgres psql -U masterbot -d masterbot_db -c 'SELECT symbol, percent, type, received_at FROM impulses ORDER BY received_at DESC LIMIT 5;'"

# Последние 5 сигналов Bablo
ssh impulse "docker compose exec postgres psql -U masterbot -d masterbot_db -c 'SELECT symbol, direction, quality_total, received_at FROM bablo_signals ORDER BY received_at DESC LIMIT 5;'"
```

## Ожидаемый вывод

Все контейнеры должны быть в статусе `Up`:
- `postgres` (5432)
- `redis` (6379)
- `impulse_service` (8001)
- `bablo_service` (8002)
- `master_bot`

Health endpoints должны возвращать `{"status": "ok"}` или `{"status": "healthy"}`.
