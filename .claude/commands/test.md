# Run Tests

Запуск тестов с правильной изоляцией модулей.

## Аргументы

- Без аргументов: запустить все тесты
- `impulse` или `impulse_service`: тесты impulse_service
- `bablo` или `bablo_service`: тесты bablo_service
- `master_bot` или `bot`: тесты master_bot
- `shared`: тесты shared модулей
- `e2e`: end-to-end тесты
- `integration`: интеграционные тесты

## Важно

**НЕ запускай `pytest` без аргументов!**

Из-за одинаковых имён пакетов (`services/`, `core/`, `models/`) в разных сервисах, тесты должны запускаться с изоляцией. Используй `./run_tests.sh`.

## Команды

Все тесты:
```bash
./run_tests.sh all
```

По сервисам:
```bash
# Impulse service
pytest tests/unit/impulse_service/ -v

# Bablo service
pytest tests/unit/bablo_service/ -v

# Master bot
pytest tests/unit/master_bot/ -v

# Shared
pytest tests/unit/shared/ -v

# Integration
pytest tests/integration/ -v

# E2E
pytest tests/e2e/ -v
```

## После тестов

Показать:
- Количество passed/failed
- Если есть failures — показать детали
- Предложить исправить, если есть ошибки
