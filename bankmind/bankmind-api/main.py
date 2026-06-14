"""BankMind API — main FastAPI application."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from database import engine
from models import Banker, Customer, ProductEligibility, Transaction, Conversation, AgentLog  # noqa
from routers import auth, customers, agents, dashboard, demo
from websocket.manager import manager
from services.redis_service import check_redis_health

settings = get_settings()
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("bankmind")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("BankMind API starting...")
    yield
    logger.info("BankMind API shutting down...")


app = FastAPI(
    title="BankMind API",
    description="B2B SaaS banking AI agent platform",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS ────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ─────────────────────────────────────────────────────────────────
API_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(customers.router, prefix=API_PREFIX)
app.include_router(agents.router, prefix=API_PREFIX)
app.include_router(dashboard.router, prefix=API_PREFIX)
app.include_router(demo.router, prefix=API_PREFIX)


# ─── WebSocket ───────────────────────────────────────────────────────────────
@app.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive; client sends pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ─── Health ──────────────────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    db_ok = True
    try:
        with engine.connect() as conn:
            conn.execute(__import__("sqlalchemy").text("SELECT 1"))
    except Exception:
        db_ok = False

    redis_ok = check_redis_health()

    return {
        "status": "healthy" if (db_ok and redis_ok) else "degraded",
        "db": "ok" if db_ok else "error",
        "redis": "ok" if redis_ok else "error",
        "version": "1.0.0",
    }


@app.get("/")
def root():
    return {"message": "BankMind API", "docs": "/docs", "health": "/health"}
