#!/bin/bash
# Скрипт для локальной разработки Mini App
# Запускает gateway на Python и frontend в dev режиме

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 Запуск Mini App в режиме разработки..."
echo ""

# Проверяем, что .env существует
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "❌ Файл .env не найден. Скопируйте .env.example в .env и заполните значения."
    exit 1
fi

# Загружаем переменные окружения
export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | xargs)

# Функция для остановки всех процессов при выходе
cleanup() {
    echo ""
    echo "🛑 Остановка сервисов..."
    kill $GATEWAY_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM

# Проверяем, что Redis и Postgres запущены (через docker или локально)
echo "📦 Проверка зависимостей..."

# Запускаем Redis и Postgres если нужно
if ! docker ps | grep -q "masterbot-platform.*redis"; then
    echo "  Запускаем Redis и Postgres..."
    docker compose -f "$PROJECT_ROOT/docker-compose.yml" up -d postgres redis
    sleep 3
fi

# Устанавливаем зависимости gateway если нужно
if [ ! -d "$PROJECT_ROOT/miniapp_gateway/.venv" ]; then
    echo "📥 Создаём виртуальное окружение для gateway..."
    python3 -m venv "$PROJECT_ROOT/miniapp_gateway/.venv"
    source "$PROJECT_ROOT/miniapp_gateway/.venv/bin/activate"
    pip install -r "$PROJECT_ROOT/miniapp_gateway/requirements.txt"
else
    source "$PROJECT_ROOT/miniapp_gateway/.venv/bin/activate"
fi

# Запускаем gateway
echo ""
echo "🔌 Запуск miniapp_gateway на порту 8003..."
cd "$PROJECT_ROOT/miniapp_gateway"
export REDIS_URL="redis://localhost:6379/0"
export IMPULSE_SERVICE_URL="http://localhost:8001"
export BABLO_SERVICE_URL="http://localhost:8002"
python -m uvicorn main:app --host 0.0.0.0 --port 8003 --reload &
GATEWAY_PID=$!
cd "$PROJECT_ROOT"

# Ждём пока gateway запустится
sleep 2

# Проверяем health gateway
if curl -s http://localhost:8003/health > /dev/null; then
    echo "✅ Gateway запущен"
else
    echo "⚠️  Gateway не отвечает, но продолжаем..."
fi

# Запускаем frontend в dev режиме
echo ""
echo "🌐 Запуск frontend на порту 5173..."
cd "$PROJECT_ROOT/miniapp_frontend"
npm run dev &
FRONTEND_PID=$!
cd "$PROJECT_ROOT"

echo ""
echo "=========================================="
echo "✅ Mini App запущен в режиме разработки"
echo ""
echo "📱 Frontend:    http://localhost:5173"
echo "🔌 Gateway:     http://localhost:8003"
echo "📊 Health:      http://localhost:8003/health"
echo "🔗 WebSocket:   ws://localhost:5173/ws/dev"
echo ""
echo "Нажмите Ctrl+C для остановки"
echo "=========================================="

# Ждём завершения
wait
