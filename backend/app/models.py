from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    games_as_player = relationship("GamePlayer", back_populates="user")
    messages = relationship("ChatMessage", back_populates="user")

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(20), default="waiting")  # waiting, active, finished
    current_turn = Column(Integer, default=0)
    board_state = Column(JSON, nullable=True)  # 15x15 board
    bag_tiles = Column(JSON, nullable=True)  # Remaining tiles
    created_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    
    # Relationships
    players = relationship("GamePlayer", back_populates="game")
    moves = relationship("GameMove", back_populates="game")
    messages = relationship("ChatMessage", back_populates="game")

class GamePlayer(Base):
    __tablename__ = "game_players"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    player_order = Column(Integer, nullable=False)  # 0-3
    score = Column(Integer, default=0)
    rack = Column(JSON, nullable=True)  # 7 tiles
    is_active = Column(Boolean, default=True)
    
    # Relationships
    game = relationship("Game", back_populates="players")
    user = relationship("User", back_populates="games_as_player")

class GameMove(Base):
    __tablename__ = "game_moves"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    move_number = Column(Integer, nullable=False)
    word = Column(String(15), nullable=True)
    tiles_played = Column(JSON, nullable=True)  # [{letter, row, col, is_blank}]
    score = Column(Integer, default=0)
    is_pass = Column(Boolean, default=False)
    is_exchange = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    game = relationship("Game", back_populates="moves")

class Dictionary(Base):
    __tablename__ = "dictionary"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(15), unique=True, index=True, nullable=False)
    language = Column(String(10), default="EN")

class Ranking(Base):
    __tablename__ = "rankings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    total_games = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    total_score = Column(Integer, default=0)
    highest_score = Column(Integer, default=0)
    rating = Column(Integer, default=1000)  # ELO-like rating
    
    # Relationships
    user = relationship("User")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    game = relationship("Game", back_populates="messages")
    user = relationship("User", back_populates="messages")
