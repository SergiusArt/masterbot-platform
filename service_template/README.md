# Service Template

This is a template for creating new microservices for MasterBot Platform.

## How to Create a New Service

1. **Copy this directory:**
   ```bash
   cp -r service_template my_new_service
   ```

2. **Rename files and update references:**
   - Update `Dockerfile` port and paths
   - Update `main.py` service name and description
   - Update `api/router.py` with your endpoints

3. **Add to docker-compose.yml:**
   ```yaml
   my_new_service:
     build: ./my_new_service
     environment:
       - DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
       - REDIS_URL=redis://redis:6379/0
     ports:
       - "8002:8002"
     depends_on:
       postgres:
         condition: service_healthy
       redis:
         condition: service_healthy
     healthcheck:
       test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
       interval: 10s
       timeout: 5s
       retries: 3
     restart: unless-stopped
     networks:
       - masterbot_network
   ```

4. **Register the service:**
   ```bash
   python scripts/register_service.py register \
     --name "my_new_service" \
     --display-name "🆕 My Service" \
     --url "http://my_new_service:8002" \
     --icon "🆕" \
     --order 20
   ```

5. **Create handlers in Master Bot:**
   - Add client in `master_bot/services/`
   - Add handlers in `master_bot/handlers/`
   - Add keyboards in `master_bot/keyboards/`

## API Structure

```
my_new_service/
├── Dockerfile
├── requirements.txt
├── main.py                 # FastAPI application
├── config.py               # Configuration
├── api/
│   ├── __init__.py
│   ├── router.py           # Main router
│   └── endpoints/
│       ├── __init__.py
│       └── health.py       # Health check
├── core/                   # Core business logic
│   └── __init__.py
├── models/                 # SQLAlchemy models
│   └── __init__.py
└── services/               # Service layer
    └── __init__.py
```

## Required Endpoints

Every service must implement:

- `GET /health` - Health check (returns `{"status": "healthy"}`)

## Communication with Master Bot

Services communicate with Master Bot through:

1. **REST API** - Master Bot calls service endpoints
2. **Redis Pub/Sub** - For push notifications

### Publishing events to Redis:

```python
from shared.utils.redis_client import get_redis_client

redis = await get_redis_client()
await redis.publish("your_channel", {
    "event": "your_event",
    "user_id": 123456789,
    "data": {"key": "value"}
})
```

## Best Practices

1. Use async/await for all I/O operations
2. Implement proper error handling
3. Add logging for important operations
4. Write tests for critical functionality
5. Document API endpoints with OpenAPI
