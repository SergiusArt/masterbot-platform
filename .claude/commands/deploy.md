# Deploy to Production

Деплой изменений на продакшн сервер через автодеплой GitHub webhook.

## Шаги

1. Проверить `git status` — есть ли незакоммиченные изменения
2. Если есть изменения:
   - Показать `git diff --stat`
   - Спросить пользователя о commit message (или предложить на основе изменений)
   - Выполнить `git add` для изменённых файлов (НЕ добавлять .env, credentials)
   - Создать коммит с Co-Authored-By
3. Выполнить `git push origin main`
4. Сообщить, что автодеплой подхватит изменения через GitHub webhook

## После деплоя показать

```
✅ Изменения запушены в main

Автодеплой должен сработать автоматически.
Для проверки используй /logs <service>

Ручная проверка:
ssh impulse
docker compose ps
docker compose logs master_bot --tail=20
```

## Production Server Info

- SSH: `ssh impulse` (или `ssh root@178.212.12.186`)
- Path: `/root/masterbot-platform`
- Autodeploy: GitHub webhook → git pull → docker compose up -d --build
