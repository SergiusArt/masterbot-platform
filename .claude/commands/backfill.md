# Backfill Missing Data

Восстановление пропущенных импульсов и сигналов Bablo из истории Telegram каналов.

## Аргументы

- `impulse` или `impulses`: восстановить импульсы
- `bablo` или `signals`: восстановить сигналы Bablo
- `all`: восстановить и то, и другое
- Дополнительно можно указать период: `--days N` (по умолчанию 30)

## Скрипты

### Impulses

Скрипт: `impulse_service/scripts/backfill_impulses.py`

```bash
# На сервере
ssh impulse "cd /root/masterbot-platform && docker compose exec impulse_service python scripts/backfill_impulses.py"

# Локально (если настроен .env)
cd impulse_service && python scripts/backfill_impulses.py
```

### Bablo Signals

Скрипт: `bablo_service/scripts/import_history.py`

```bash
# На сервере
ssh impulse "cd /root/masterbot-platform && docker compose exec bablo_service python scripts/import_history.py --days 30 --limit 1000"

# Локально
cd bablo_service && python scripts/import_history.py --days 30 --limit 1000
```

Параметры:
- `--days N`: количество дней истории (default: 30)
- `--limit N`: максимум сообщений (default: 1000)

## Что делают скрипты

1. Подключаются к Telegram через Telethon (используя SESSION_STRING)
2. Читают историю сообщений из канала за указанный период
3. Парсят каждое сообщение через соответствующий парсер
4. Сохраняют в БД (пропуская дубликаты по telegram_message_id)
5. Выводят статистику: найдено / добавлено / пропущено

## Telegram Channel IDs

- Impulse Channel: `-1002313787119`
- Bablo Channel: `-1001628431640`
- Test Channel: `-1001801996686`

## Когда использовать

- После простоя сервиса (listener был выключен)
- После ошибок подключения к Telegram
- При первоначальной загрузке исторических данных
- После изменений в парсере (перепарсить старые сообщения)

## Важно

- Скрипты идемпотентны — повторный запуск не создаст дубликатов
- Используют тот же SESSION_STRING что и listener
- Не отправляют уведомления пользователям (только сохраняют в БД)
