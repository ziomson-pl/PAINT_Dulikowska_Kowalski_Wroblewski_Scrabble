import sys
import time
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from database import Base, DATABASE_URL
from app.models import User, Dictionary, Ranking
from app.auth import get_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PL_FILE = os.path.join(BASE_DIR, "slownik.txt")
EN_FILE = os.path.join(BASE_DIR, "dictionary.txt")

with open(PL_FILE, encoding="utf-8") as f:
    COMMON_WORDS_PL = [line.strip().upper() for line in f if line.strip()]

with open(EN_FILE, encoding="utf-8") as f:
    COMMON_WORDS_EN = [line.strip().upper() for line in f if line.strip()]


def seed_dictionary(db: Session, words: list[str], language="PL"):
    records = [
        {"word": w.strip().upper(), "language": language}
        for w in words
        if w.strip()
    ]

    db.bulk_insert_mappings(Dictionary, records)
    db.commit()

def seed_users(db):
    test_users = [
        {"username": "player1", "email": "player1@example.com", "password": "password123"},
        {"username": "player2", "email": "player2@example.com", "password": "password123"},
        {"username": "player3", "email": "player3@example.com", "password": "password123"},
        {"username": "player4", "email": "player4@example.com", "password": "password123"},
    ]

    for u in test_users:
        existing_user = db.query(User).filter(User.username == u["username"]).first()
        if existing_user:
            print(f"User {u['username']} already exists")
            continue

        user = User(
            username=u["username"],
            email=u["email"],
            hashed_password=get_password_hash(u["password"])
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create ranking
        ranking = Ranking(user_id=user.id)
        db.add(ranking)
        db.commit()

        print(f"Created user {u['username']} with ranking")


def seed_database():
    print("Waiting for database to be ready...")
    time.sleep(5)

    engine = create_engine(DATABASE_URL)

    # Wait for database connection
    max_retries = 30
    for i in range(max_retries):
        try:
            engine.connect()
            print("Database connection established")
            break
        except Exception as e:
            if i < max_retries - 1:
                print(f"Waiting for database... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                print(f"Could not connect to database: {e}")
                sys.exit(1)

    # Create tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created")

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Seed dictionary - COMMENT OUT AND RELACE COMMON_WORDS WITH SOME SMALL LIST OF WORDS FOR TESTING
        seed_dictionary(db, COMMON_WORDS_PL, "PL")
        seed_dictionary(db, COMMON_WORDS_EN, "EN")

        # Seed users
        seed_users(db)

        print("Database seeding completed!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
