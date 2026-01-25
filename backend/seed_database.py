import sys
import time
import os
import io
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from database import Base, DATABASE_URL
from app.models import User, Dictionary, Ranking
from app.auth import get_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PL_FILE = os.path.join(BASE_DIR, "slownik.txt")
EN_FILE = os.path.join(BASE_DIR, "dictionary.txt")


def seed_dictionary_copy(db: Session, filepath: str, language="PL"):
    """Fast bulk loading using PostgreSQL COPY command"""
    print(f"Loading {language} dictionary from {filepath} using COPY...")
    
    try:
        csv_buffer = io.StringIO()
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                word = line.strip().upper()
                if word:
                    csv_buffer.write(f"{word}\t{language}\n")
        
        csv_buffer.seek(0)
        
        raw_connection = db.connection().connection
        cursor = raw_connection.cursor()
        
        cursor.copy_expert(
            "COPY dictionary (word, language) FROM STDIN",
            csv_buffer
        )
        
        raw_connection.commit()
        cursor.close()
        
        print(f"✓ {language} dictionary loaded successfully")
        
    except Exception as e:
        print(f"✗ Error loading {language} dictionary: {e}")
        raise

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

        ranking = Ranking(user_id=user.id)
        db.add(ranking)
        db.commit()

        print(f"Created user {u['username']} with ranking")


def seed_database():
    print("Waiting for database to be ready...")
    time.sleep(5)

    engine = create_engine(DATABASE_URL)

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

    Base.metadata.create_all(bind=engine)
    print("Database tables created")

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        existing_words = db.query(Dictionary).first()
        
        if existing_words is not None:
            print("✓ Dictionary already seeded, skipping...")
        else:
            print("Dictionary empty, seeding with fast COPY command...")
            seed_dictionary_copy(db, PL_FILE, "PL")
            seed_dictionary_copy(db, EN_FILE, "EN")
            print("✓ Dictionary seeding completed")
        
        seed_users(db)

        print("✓ Database seeding completed!")

    except Exception as e:
        print(f"✗ Error seeding database: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
