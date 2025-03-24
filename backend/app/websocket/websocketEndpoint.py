from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.websocketController import process_message
from app.websocket.connectionManager import manager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Receive a message from the client
            data = await websocket.receive_text()
            # Process the message using controller logic
            response = await process_message(data)
            # Broadcast the processed response to all connected clients
            await manager.broadcast(response)
    except WebSocketDisconnect:
        # Remove the client from active connections when they disconnect
        manager.disconnect(websocket)
        print("Client disconnected")
