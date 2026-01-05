from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# User schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Game schemas
class GameCreate(BaseModel):
    pass

class TilePlacement(BaseModel):
    letter: str
    row: int
    col: int
    is_blank: bool = False

class MoveCreate(BaseModel):
    tiles: List[TilePlacement]
    is_pass: bool = False
    is_exchange: bool = False
    exchange_tiles: Optional[List[str]] = None

class MoveResponse(BaseModel):
    id: int
    word: Optional[str]
    score: int
    is_pass: bool
    is_exchange: bool
    created_at: datetime

    class Config:
        from_attributes = True

class PlayerInfo(BaseModel):
    id: int
    username: str
    score: int
    player_order: int
    is_active: bool

class GameResponse(BaseModel):
    id: int
    status: str
    current_turn: int
    board_state: Optional[List[List[Optional[Dict[str, Any]]]]]
    players: List[PlayerInfo]
    created_at: datetime
    
    class Config:
        from_attributes = True

class GameDetailResponse(GameResponse):
    rack: Optional[List[str]] = None
    remaining_tiles: int = 0

# Chat schemas
class ChatMessageCreate(BaseModel):
    message: str = Field(..., max_length=500)

class ChatMessageResponse(BaseModel):
    id: int
    user_id: int
    username: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True

# Ranking schemas
class RankingResponse(BaseModel):
    id: int
    username: str
    total_games: int
    wins: int
    losses: int
    total_score: int
    highest_score: int
    rating: int

    class Config:
        from_attributes = True

# History schemas
class GameHistoryResponse(BaseModel):
    id: int
    status: str
    player_score: int
    player_rank: int
    total_players: int
    created_at: datetime
    finished_at: Optional[datetime]

    class Config:
        from_attributes = True
