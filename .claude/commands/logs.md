# Check Server Logs

Проверка логов сервисов на продакшн сервере.

## Аргументы

- `impulse` или `impulse_service`: логи impulse_service
- `bablo` или `bablo_service`: логи bablo_service
- `bot` или `master_bot`: логи master_bot
- `all`: логи всех сервисов
- `ps`: статус контейнеров (docker compose ps)

## Server Info

- SSH: `ssh impulse` (алиас для `ssh root@178.212.12.186`)
- Path: `/root/masterbot-platform`

## Команды

```bash
# Подключиться и посмотреть логи
ssh impulse "cd /root/masterbot-platform && docker compose logs <service> --tail=50"

# Статус контейнеров
ssh impulse "cd /root/masterbot-platform && docker compose ps"

# Логи в реальном времени (follow)
ssh impulse "cd /root/masterbot-platform && docker compose logs -f <service> --tail=20"
```

## Полезные паттерны для grep

```bash
# Ошибки
docker compose logs master_bot 2>&1 | grep -i error

# Telegram handler events
docker compose logs impulse_service 2>&1 | grep "🔥\|📩\|✅"

# Activity alerts
docker compose logs bablo_service 2>&1 | grep "activity"
```

## Что искать в логах

1. **impulse_service**:
   - `✅ Listening to channel` — listener работает
   - `📩 Processing message` — сообщения обрабатываются
   - `Sent impulse alert to N users` — уведомления отправлены

2. **bablo_service**:
   - `✅ Listening to channel` — listener работает
   - `📊 Signal parsed` — сигналы парсятся
   - `Activity alert sent` — алерты активности

3. **master_bot**:
   - `Bot started` — бот запущен
   - `Subscribed to channels` — подписка на Redis каналы
   - `Report queued for N users` — отчёты отправлены
