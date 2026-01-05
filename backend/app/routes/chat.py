from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Dict, List
from datetime import datetime
import json

from app.models import ChatMessage, User, Game
from database import get_db, SessionLocal

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # game_id -> list of websocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, game_id: int):
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        self.active_connections[game_id].append(websocket)

    def disconnect(self, websocket: WebSocket, game_id: int):
        if game_id in self.active_connections:
            self.active_connections[game_id].remove(websocket)
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, game_id: int):
        if game_id in self.active_connections:
            for connection in self.active_connections[game_id]:
                try:
                    await connection.send_text(message)
                except:
                    pass

manager = ConnectionManager()

@router.websocket("/ws/chat/{game_id}")
async def websocket_chat(websocket: WebSocket, game_id: int):
    await manager.connect(websocket, game_id)
    db = SessionLocal()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Extract user info and message
            username = message_data.get("username")
            user_id = message_data.get("user_id")
            message_text = message_data.get("message")
            
            if not username or not message_text or not user_id:
                continue
            
            # Verify game exists
            game = db.query(Game).filter(Game.id == game_id).first()
            if not game:
                continue
            
            # Save message to database
            chat_message = ChatMessage(
                game_id=game_id,
                user_id=user_id,
                message=message_text
            )
            db.add(chat_message)
            db.commit()
            db.refresh(chat_message)
            
            # Broadcast message to all connections in this game
            broadcast_data = {
                "id": chat_message.id,
                "user_id": user_id,
                "username": username,
                "message": message_text,
                "created_at": chat_message.created_at.isoformat()
            }
            await manager.broadcast(json.dumps(broadcast_data), game_id)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, game_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, game_id)
    finally:
        db.close()

@router.get("/api/games/{game_id}/messages")
async def get_messages(game_id: int, db: Session = Depends(get_db)):
    """Get chat history for a game"""
    messages = db.query(ChatMessage, User).join(User, ChatMessage.user_id == User.id).filter(
        ChatMessage.game_id == game_id
    ).order_by(ChatMessage.created_at).all()
    
    result = []
    for msg, user in messages:
        result.append({
            "id": msg.id,
            "user_id": msg.user_id,
            "username": user.username,
            "message": msg.message,
            "created_at": msg.created_at.isoformat()
        })
    
    return result
