from sqlalchemy.orm import Session
from app.models import Ranking

class RankingService:
    def __init__(self, db: Session):
        self.db = db

    def add_score(self, user_id: int, score: int):
        ranking = (
            self.db.query(Ranking)
            .filter(Ranking.user_id == user_id)
            .first()
        )

        if not ranking:
            return None, "Ranking not found"

        ranking.total_score += score

        if score > ranking.highest_score:
            ranking.highest_score = score

        ranking.rating = ranking.total_score // max(ranking.total_games, 1)

        self.db.commit()
        self.db.refresh(ranking)

        return ranking, None
