from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.models import User, Ranking, Game, GamePlayer
from app.schemas import RankingResponse, GameHistoryResponse, UserResponse
from app.auth import get_current_user
from database import get_db

router = APIRouter(prefix="/api", tags=["profile"])

@router.get("/profile", response_model=UserResponse)
def get_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@router.get("/rankings", response_model=List[RankingResponse])
def get_rankings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get global rankings"""
    rankings = db.query(Ranking, User).join(User, Ranking.user_id == User.id).order_by(Ranking.rating.desc()).limit(100).all()
    
    result = []
    for ranking, user in rankings:
        result.append(RankingResponse(
            id=ranking.id,
            username=user.username,
            total_games=ranking.total_games,
            wins=ranking.wins,
            losses=ranking.losses,
            total_score=ranking.total_score,
            highest_score=ranking.highest_score,
            rating=ranking.rating
        ))
    
    return result

@router.get("/history", response_model=List[GameHistoryResponse])
def get_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get user's game history"""
    # Get all games where user participated
    game_players = db.query(GamePlayer).filter(GamePlayer.user_id == current_user.id).all()
    
    history = []
    for gp in game_players:
        game = db.query(Game).filter(Game.id == gp.game_id).first()
        if not game:
            continue
        
        # Get all players in the game to determine rank
        all_players = db.query(GamePlayer).filter(GamePlayer.game_id == game.id).order_by(GamePlayer.score.desc()).all()
        
        player_rank = 0
        for idx, player in enumerate(all_players):
            if player.user_id == current_user.id:
                player_rank = idx + 1
                break
        
        history.append(GameHistoryResponse(
            id=game.id,
            status=game.status,
            player_score=gp.score,
            player_rank=player_rank,
            total_players=len(all_players),
            created_at=game.created_at,
            finished_at=game.finished_at
        ))
    
    return history
