from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict
import uuid
import uvicorn
import os

app = FastAPI(title="Connection Relay - esgroup (TM)")

# Each account gets its own room with unique server_link and client_link
rooms: Dict[str, WebSocket] = {}  # room_id -> server_ws
client_rooms: Dict[str, WebSocket] = {}  # room_id -> client_ws

@app.get("/")
async def home():
    room_id = str(uuid.uuid4())[:8]
    server_link = f"wss://{_get_url()}/server/{room_id}"
    client_link = f"wss://{_get_url()}/client/{room_id}"
    return {
        "account_created": room_id,
        "server_connect_here": server_link,
        "client_connect_here": client_link,
        "how_to_use": "Give the client link to the scammer's exe. Use the server link in your python app to control."
    }

def _get_url():
    return os.getenv("RENDER_EXTERNAL_URL", "your-service-name.onrender.com")

@app.websocket("/server/{room_id}")
async def server_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    rooms[room_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            if room_id in client_rooms:
                await client_rooms[room_id].send_text(data)
    except WebSocketDisconnect:
        rooms.pop(room_id, None)

@app.websocket("/client/{room_id}")
async def client_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    client_rooms[room_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            if room_id in rooms:
                await rooms[room_id].send_text(data)
    except WebSocketDisconnect:
        client_rooms.pop(room_id, None)
