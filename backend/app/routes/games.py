from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models import User, Game, GamePlayer, GameMove
from app.schemas import GameCreate, GameResponse, GameDetailResponse, MoveCreate, MoveResponse, PlayerInfo
from app.auth import get_current_user
from app.services.game_service import GameService
from database import get_db

router = APIRouter(prefix="/api/games", tags=["games"])

@router.post("", response_model=GameResponse)
def create_game(game: GameCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new game"""
    service = GameService(db)
    game = service.create_game()
    
    # Automatically join as first player
    service.join_game(game.id, current_user.id)
    
    # Reload game with players
    db.refresh(game)
    
    return format_game_response(game, db)

@router.get("", response_model=List[GameResponse])
def list_games(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List all available games"""
    games = db.query(Game).filter(Game.status.in_(["waiting", "active"])).all()
    return [format_game_response(game, db) for game in games]

@router.get("/{game_id}", response_model=GameDetailResponse)
def get_game(game_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get game details including player's rack"""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Get player's info
    player = db.query(GamePlayer).filter(
        GamePlayer.game_id == game_id,
        GamePlayer.user_id == current_user.id
    ).first()
    
    response = format_game_response(game, db)
    
    if player:
        response["rack"] = player.rack
    
    bag_tiles = game.bag_tiles or []
    response["remaining_tiles"] = len(bag_tiles)
    
    return response

@router.post("/{game_id}/join")
def join_game(game_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Join an existing game"""
    service = GameService(db)
    player = service.join_game(game_id, current_user.id)
    
    if not player:
        raise HTTPException(status_code=400, detail="Cannot join game")
    
    return {"message": "Joined game successfully", "player_order": player.player_order}

@router.post("/{game_id}/start")
def start_game(game_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Start the game"""
    # Verify user is in the game
    player = db.query(GamePlayer).filter(
        GamePlayer.game_id == game_id,
        GamePlayer.user_id == current_user.id
    ).first()
    
    if not player:
        raise HTTPException(status_code=403, detail="Not in this game")
    
    service = GameService(db)
    if not service.start_game(game_id):
        raise HTTPException(status_code=400, detail="Cannot start game")
    
    return {"message": "Game started"}

@router.post("/{game_id}/end")
def end_game(game_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Force end the game"""
    service = GameService(db)
    if not service.end_game(game_id, current_user.id):
        raise HTTPException(status_code=400, detail="Cannot end game")
    
    return {"message": "Game ended"}

@router.post("/{game_id}/moves", response_model=MoveResponse)
def make_move(game_id: int, move: MoveCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Make a move in the game"""
    service = GameService(db)
    
    tiles_played = [tile.dict() for tile in move.tiles] if move.tiles else []
    exchange_tiles = move.exchange_tiles if move.is_exchange else None
    
    game_move, error = service.make_move(
        game_id,
        current_user.id,
        tiles_played,
        move.is_pass,
        move.is_exchange,
        exchange_tiles
    )
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return game_move

@router.get("/{game_id}/moves", response_model=List[MoveResponse])
def get_moves(game_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all moves in a game"""
    moves = db.query(GameMove).filter(GameMove.game_id == game_id).order_by(GameMove.move_number).all()
    return moves

def format_game_response(game: Game, db: Session) -> dict:
    """Format game response with player info"""
    players = db.query(GamePlayer).filter(GamePlayer.game_id == game.id).all()
    
    player_info = []
    for player in players:
        user = db.query(User).filter(User.id == player.user_id).first()
        player_info.append(PlayerInfo(
            id=player.user_id,
            username=user.username if user else "Unknown",
            score=player.score,
            player_order=player.player_order,
            is_active=player.is_active
        ))
    
    return {
        "id": game.id,
        "status": game.status,
        "current_turn": game.current_turn,
        "board_state": game.board_state,
        "players": player_info,
        "created_at": game.created_at
    }
