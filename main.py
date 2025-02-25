from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import sqlite3
import json
from datetime import datetime
from typing import List

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Initialize Database
def init_db():
    with sqlite3.connect("chat.db") as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS chat (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user TEXT,
                        message TEXT,
                        timestamp TEXT
                    )''')
        conn.commit()


init_db()  # Initialize database on app start


# Manage WebSocket Connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        message_json = json.dumps(message)
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                print(f"Error sending message: {e}")


manager = ConnectionManager()


@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(websocket)

    join_message = {"user": username, "message": "has joined the chat!", "status": "join"}
    await manager.broadcast(join_message)

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            sender = message_data.get("user", "Unknown")
            message_text = message_data.get("message", "")
            timestamp = datetime.utcnow().isoformat()

            stored_message = {"user": sender, "message": message_text, "timestamp": timestamp}

            # Save message to database
            with sqlite3.connect("chat.db") as conn:
                conn.execute("INSERT INTO chat (user, message, timestamp) VALUES (?, ?, ?)",
                             (sender, message_text, timestamp))
                conn.commit()

            # Broadcast message
            await manager.broadcast(stored_message)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        leave_message = {"user": username, "message": "has left the chat!", "status": "leave"}
        await manager.broadcast(leave_message)


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
