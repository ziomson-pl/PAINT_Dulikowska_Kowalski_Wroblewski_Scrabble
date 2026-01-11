import sys
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, DATABASE_URL
from app.models import User, Dictionary, Ranking
from app.auth import get_password_hash


with open("slownik.txt", encoding="utf-8") as f:
    COMMON_WORDS_PL = [line.strip() for line in f if line.strip()]

with open("dictionary.txt", encoding="utf-8") as f:
    COMMON_WORDS_EN = [line.strip() for line in f if line.strip()]

def seed_database():
    """Seed database with initial data"""
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
        # Check if dictionary already seeded
        existing_words = db.query(Dictionary).count()
        if existing_words > 0:
            print(f"Dictionary already seeded with {existing_words} words")
        else:
            # Seed dictionary
            unique_words_pl = sorted(list(set(COMMON_WORDS_PL)))
            print(f"Seeding dictionary with {len(unique_words_pl)} polish words...")
            for word in unique_words_pl:
                dict_entry = Dictionary(word=word.upper(), language="PL")
                db.add(dict_entry)

            unique_words_en = sorted(list(set(COMMON_WORDS_EN)))
            print(f"Seeding dictionary with {len(unique_words_en)} english words...")
            for word in unique_words_en:
                dict_entry = Dictionary(word=word.upper(), language="EN")
                db.add(dict_entry)
            
            db.commit()
            print("Dictionary seeded successfully")
        
        # Check if test users exist
        test_user = db.query(User).filter(User.username == "player1").first()
        if not test_user:
            print("Creating test users...")
            
            # Create test users
            test_users = [
                {"username": "player1", "email": "player1@example.com", "password": "password123"},
                {"username": "player2", "email": "player2@example.com", "password": "password123"},
                {"username": "player3", "email": "player3@example.com", "password": "password123"},
                {"username": "player4", "email": "player4@example.com", "password": "password123"},
            ]
            
            for user_data in test_users:
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=get_password_hash(user_data["password"])
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                
                # Create ranking for user
                ranking = Ranking(user_id=user.id)
                db.add(ranking)
            
            db.commit()
            print("Test users created successfully")
        else:
            print("Test users already exist")
        
        print("Database seeding completed!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
