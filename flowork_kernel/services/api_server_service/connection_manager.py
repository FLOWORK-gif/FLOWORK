#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\connection_manager.py
# JUMLAH BARIS : 29
#######################################################################

from typing import List
from fastapi import WebSocket
class ConnectionManager:
    """
    Manages active WebSocket connections for real-time client tracking.
    This acts as the 'switchboard operator' for the server.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    async def connect(self, websocket: WebSocket):
        """Accepts a new client connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[API Server] New client connected. Total connections: {len(self.active_connections)}") # English Log
    def disconnect(self, websocket: WebSocket):
        """Removes a client connection."""
        self.active_connections.remove(websocket)
        print(f"[API Server] Client disconnected. Total connections: {len(self.active_connections)}") # English Log
    @property
    def connection_count(self) -> int:
        """Returns the current number of active connections."""
        return len(self.active_connections)
