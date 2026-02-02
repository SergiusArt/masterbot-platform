"""Mini App Gateway - FastAPI application with WebSocket support."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from auth.telegram import validate_init_data, TelegramUser
from websocket.manager import (
    connection_manager,
    WebSocketMessage,
    WSMessageType,
)
from websocket.handlers import handle_client_message
from services.redis_subscriber import redis_subscriber
from api.router import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting Mini App Gateway...")
    await redis_subscriber.start()
    logger.info("Mini App Gateway started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Mini App Gateway...")
    await redis_subscriber.stop()
    logger.info("Mini App Gateway shut down")


app = FastAPI(
    title="Mini App Gateway",
    description="WebSocket gateway for Telegram Mini App dashboards",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your Mini App domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)


# Root health check (for docker healthcheck)
@app.get("/health")
async def root_health():
    """Root health check endpoint."""
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    initData: str = Query(default=""),
):
    """WebSocket endpoint for real-time updates.

    Clients must provide Telegram initData for authentication.
    """
    # Validate initData
    validation_result = validate_init_data(initData, settings.BOT_TOKEN)

    if not validation_result.valid:
        logger.warning(f"WebSocket auth failed: {validation_result.error}")
        await websocket.close(code=4001, reason=validation_result.error or "Invalid initData")
        return

    user: TelegramUser = validation_result.user
    user_id = user.id

    # Connect
    connected = await connection_manager.connect(websocket, user_id)
    if not connected:
        await websocket.close(code=4002, reason="Connection limit reached")
        return

    # Send welcome message
    welcome_msg = WebSocketMessage(
        type=WSMessageType.CONNECTED,
        data={
            "user_id": user_id,
            "username": user.username,
            "message": "Connected to Mini App Gateway",
        },
    )
    await websocket.send_text(welcome_msg.to_json())

    logger.info(f"User {user_id} (@{user.username}) connected via WebSocket")

    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()

            # Handle the message
            response = await handle_client_message(user_id, data)
            if response:
                await websocket.send_text(response.to_json())

    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        await connection_manager.disconnect(user_id)


@app.websocket("/ws/dev")
async def websocket_dev_endpoint(websocket: WebSocket):
    """Development WebSocket endpoint without authentication.

    WARNING: Only use in development!
    """
    # Use a fake user ID for development
    dev_user_id = 12345

    connected = await connection_manager.connect(websocket, dev_user_id)
    if not connected:
        await websocket.close(code=4002, reason="Connection limit reached")
        return

    welcome_msg = WebSocketMessage(
        type=WSMessageType.CONNECTED,
        data={
            "user_id": dev_user_id,
            "message": "Connected to Mini App Gateway (DEV MODE)",
        },
    )
    await websocket.send_text(welcome_msg.to_json())

    logger.info(f"DEV user {dev_user_id} connected via WebSocket")

    try:
        while True:
            data = await websocket.receive_text()
            response = await handle_client_message(dev_user_id, data)
            if response:
                await websocket.send_text(response.to_json())

    except WebSocketDisconnect:
        logger.info(f"DEV user {dev_user_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for DEV user: {e}")
    finally:
        await connection_manager.disconnect(dev_user_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )
