from sqlalchemy.orm import Session
from app.models import Ranking

class RankingService:
    def __init__(self, db: Session):
        self.db = db

    def update_after_game(
        self,
        user_id: int,
        score: int,
        is_winner: bool
    ) -> Ranking:
        """
        Update ranking after finished game:
        - creates ranking if not exists
        - adds total_score
        - updates highest_score
        - increments total_games
        - increments wins / losses
        - updates rating
        """

        ranking = (
            self.db.query(Ranking)
            .filter(Ranking.user_id == user_id)
            .first()
        )

        # ---- CREATE RANKING IF NOT EXISTS ----
        if not ranking:
            ranking = Ranking(
                user_id=user_id,
                total_games=0,
                wins=0,
                losses=0,
                total_score=0,
                highest_score=0,
                rating=1000,  # start value
            )
            self.db.add(ranking)
            self.db.flush()  # important: ensures ranking.id exists

        # ---- UPDATE STATS ----
        ranking.total_games += 1
        ranking.total_score += score
        ranking.highest_score = max(ranking.highest_score, score)

        if is_winner:
            ranking.wins += 1
            ranking.rating += 10
        else:
            ranking.losses += 1
            ranking.rating -= 5
        ranking.rating = ranking.total_score * ranking.wins / ranking.total_games

        return ranking
