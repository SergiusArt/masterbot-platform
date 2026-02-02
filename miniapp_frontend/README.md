# Mini App Frontend

Telegram Mini App с real-time дашбордами для MasterBot.

## Разработка

### Первый запуск

```bash
# Установка зависимостей
npm install

# Запуск в dev режиме
npm run dev
```

Открыть http://localhost:5173

### Сборка

```bash
npm run build
```

Собранные файлы будут в папке `dist/`.

## Технологии

- React 18
- TypeScript
- Vite
- Tailwind CSS
- Recharts (графики)
- Zustand (state management)

## Структура

```
src/
├── api/              # API клиент
├── components/
│   ├── common/       # Общие компоненты
│   ├── charts/       # Графики
│   ├── impulse/      # Impulse Dashboard
│   └── bablo/        # Bablo Dashboard
├── hooks/
│   ├── useTelegramApp.ts    # Telegram WebApp API
│   └── useWebSocket.ts      # WebSocket подключение
├── store/            # Zustand stores
├── types/            # TypeScript типы
└── utils/            # Утилиты
```

## Dev Mode vs Production

### Dev Mode (вне Telegram)
- WebSocket подключается к `/ws/dev` без аутентификации
- Все функции работают, но без данных пользователя Telegram

### Production (в Telegram)
- WebSocket подключается к `/ws` с `initData` для аутентификации
- Telegram theme поддержка (dark/light)
- Нативная навигация (BackButton)
