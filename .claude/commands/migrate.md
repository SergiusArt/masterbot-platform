# Apply Database Migrations

Применение SQL миграций к базе данных на продакшн сервере.

## Server Info

- SSH: `ssh impulse`
- Database: `masterbot_db`
- User: `masterbot`
- Container: `postgres`

## Миграции

Все миграции находятся в `shared/database/migrations/`:

1. `001_initial_schema.sql` — базовые таблицы
2. `002_add_bablo_tables.sql` — таблицы Bablo
3. `003_add_notifications_enabled.sql` — флаг уведомлений
4. `004_add_bablo_activity_fields.sql` — поля активности Bablo
5. `005_add_user_timezone.sql` — timezone пользователей
6. `006_add_bablo_timeframe_columns.sql` — колонки timeframe
7. `007_add_performance_indexes.sql` — индексы для производительности

## Команды

Применить конкретную миграцию:
```bash
ssh impulse "cd /root/masterbot-platform && cat shared/database/migrations/007_add_performance_indexes.sql | docker compose exec -T postgres psql -U masterbot -d masterbot_db"
```

Применить все миграции:
```bash
ssh impulse "cd /root/masterbot-platform && for f in shared/database/migrations/*.sql; do cat \$f | docker compose exec -T postgres psql -U masterbot -d masterbot_db; done"
```

Проверить применённые миграции (по наличию таблиц/индексов):
```bash
ssh impulse "docker compose exec postgres psql -U masterbot -d masterbot_db -c '\dt'"
ssh impulse "docker compose exec postgres psql -U masterbot -d masterbot_db -c '\di'"
```

## Важно

- Миграции идемпотентны (IF NOT EXISTS)
- Применять в порядке номеров
- После миграции проверить, что сервисы работают: `/logs all`
