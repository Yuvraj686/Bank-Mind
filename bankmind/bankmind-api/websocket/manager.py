"""WebSocket connection manager for real-time dashboard updates."""
import json
import logging
from typing import Any
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("WebSocket connected. Total: %d", len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info("WebSocket disconnected. Total: %d", len(self.active_connections))

    async def broadcast(self, event_type: str, data: dict[str, Any]):
        """Broadcast a structured event to all connected clients."""
        from datetime import datetime
        message = json.dumps({
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": data,
        })
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.warning("Failed to send to connection: %s", e)
                dead_connections.append(connection)
        for conn in dead_connections:
            self.disconnect(conn)

    async def send_agent_action(
        self,
        customer_id: str,
        customer_name: str,
        agent: str,
        action: str,
        message: str | None,
        reasoning: str | None,
        stage: str,
        log_id: str | None = None,
    ):
        """Convenience method for broadcasting agent actions."""
        await self.broadcast("agent_action", {
            "log_id": log_id,
            "customer_id": customer_id,
            "customer_name": customer_name,
            "agent": agent,
            "action": action,
            "message": message,
            "reasoning": reasoning,
            "stage": stage,
        })

    async def send_stage_change(self, customer_id: str, customer_name: str, from_stage: str, to_stage: str):
        await self.broadcast("stage_change", {
            "customer_id": customer_id,
            "customer_name": customer_name,
            "from_stage": from_stage,
            "to_stage": to_stage,
        })

    async def send_kpi_update(self):
        await self.broadcast("kpi_update", {})

    async def send_demo_progress(self, step: str, status: str, customer_name: str | None = None):
        await self.broadcast("demo_progress", {
            "step": step,
            "status": status,
            "customer_name": customer_name,
        })


# Singleton instance
manager = ConnectionManager()
