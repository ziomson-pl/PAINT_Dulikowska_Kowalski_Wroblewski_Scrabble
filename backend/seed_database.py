import sys
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, DATABASE_URL
from app.models import User, Dictionary, Ranking
from app.auth import get_password_hash

# Common English Scrabble words
# Common Polish Scrabble words (Subset for seeding)
COMMON_WORDS = [
    # 2-letter words
    "AA", "AB", "AD", "AG", "AJ", "AL", "AM", "AR", "AS", "AT", "AU", "AŻ",
    "BA", "BE", "BI", "BO", "BU", "BY",
    "CI", "CO", "DA", "DE", "DO", "DÓ", "DY",
    "EF", "EH", "EJ", "EL", "EM", "EN", "EO", "EP", "ER", "ES", "ET", "EW", "EZ",
    "FA", "FE", "FI", "FU",
    "GĘ", "GO", "GU",
    "HA", "HE", "HI", "HM", "HO", "HU",
    "ID", "IF", "II", "IL", "IM", "IN", "IW", "IŻ",
    "JA", "JE", "JO",
    "KA", "KI", "KO", "KU",
    "LA", "LI", "LU",
    "MA", "ME", "MI", "MU", "MY",
    "NA", "NI", "NO", "NY",
    "OB", "OD", "OJ", "OK", "OM", "ON", "OP", "OR", "OS", "OT", "OZ", "OŚ", "OŻ",
    "PA", "PE", "PI", "PO",
    "RE", "RO", "RU",
    "SĄ", "SE", "SI", "SU",
    "TA", "TĘ", "TE", "TO", "TU", "TY",
    "UD", "UF", "UL", "UT",
    "WE", "WU", "WY",
    "ZA", "ZE", "DŻ",
    
    # 3-letter words
    "ABC", "ACH", "ACT", "ADU", "ADY", "AGA", "AGE", "AGI", "AGO", "AHA", "AIR", "AIS", "AKR", "AKT", "ALA", "ALE", "ALF", "ALI", "ALK", "ALO", "ALP", "AŁA", "AMY", "ANA", "ANI", "ANŁ", "ANT", "ARA", "ARB", "ARD", "ARE", "ARF", "ARG", "ARH", "ARI", "ARK", "ARM", "ARO", "ARP", "ARS", "ARY", "ASA", "ASI", "ASK", "ASU", "ASY", "ATA", "ATE", "ATU", "ATY", "AUT", "AUA", "AWE", "AZA", "AZY",
    "BAB", "BAC", "BAD", "BAG", "BAI", "BAJ", "BAK", "BAL", "BAM", "BAN", "BAO", "BAR", "BAS", "BAT", "BAU", "BAW", "BAZ", "BAŚ", "BĄK", "BEG", "BEJ", "BEK", "BEL", "BER", "BET", "BEZ", "BĘC", "BID", "BIG", "BIJ", "BIK", "BIL", "BIM", "BIN", "BIO", "BIS", "BIT", "BIZ", "BOA", "BOB", "BOC", "BOD", "BOI", "BOJ", "BOK", "BOL", "BOM", "BON", "BOO", "BOP", "BOR", "BOT", "BOY", "BÓB", "BÓG", "BÓJ", "BÓL", "BÓR", "BRR", "BRU", "BRY", "BRZ", "BUC", "BUDA", "BUF", "BUG", "BUK", "BUL", "BUM", "BUN", "BUR", "BUS", "BUT", "BUU", "BUZ", "BYK", "BYL", "BYŁ", "BYM", "BYŚ", "BYT", "BZM", "BZY",
    "CAL", "CAP", "CAR", "CEK", "CEL", "CEN", "CEP", "CER", "CES", "CET", "CEW", "CĘT", "CHA", "CHE", "CHI", "CHO", "CHU", "CHY", "CIA", "CIC", "CIE", "CIĘ", "CII", "CIN", "CIP", "CIS", "CIT", "CIU", "CKA", "CŁA", "CŁO", "CNA", "CNY", "COF", "COL", "COM", "CON", "COR", "COS", "COŚ", "CÓR", "CÓŻ", "CUD", "CUG", "CUM", "CUP", "CUR", "CYC", "CYG", "CYK", "CYM", "CYN", "CYP", "CYR", "CYT", "CZA", "CZC", "CZE", "CZY",
    "DAĆ", "DAG", "DAI", "DAJ", "DAK", "DAL", "DAM", "DAN", "DAO", "DAR", "DAS", "DAT", "DBA", "DĘB", "DĘT", "DIL", "DIM", "DIN", "DIP", "DIS", "DIT", "DLA", "DNI", "DNU", "DNY", "DOB", "DOG", "DOI", "DOK", "DOL", "DOM", "DON", "DOR", "DOŚ", "DOZ", "DÓŁ", "DÓW", "DRĄ", "DRE", "DRG", "DRR", "DRU", "DRW", "DRY", "DUALE", "DUCH", "DUDA", "DUG", "DUH", "DUJ", "DUK", "DUM", "DUO", "DUP", "DUR", "DUS", "DUT", "DUX", "DUŻ", "DWA", "DYB", "DYG", "DYL", "DYM", "DYN", "DYP", "DYS", "DYZ", "DZI",
    
    # Common 4+ letter words
    "ADAM", "ALBO", "ALEJ", "AUTO", "BABA", "BACA", "BADA", "BALI", "BANA", "BARK", "BANI", "BAZA", "BĘDĘ", "BIAŁ", "BIEG", "BIED", "BILI", "BLOK", "BŁĄD", "BOCZ", "BOGA", "BOIS", "BOJE", "BOKI", "BOLA", "BORA", "BOŻE", "BRAK", "BRAT", "BREW", "BROŃ", "BRUD", "BRUK", "BRUZ", "BRWI", "BRYD", "BRYK", "BRYM", "BRZE", "BUCE", "BUDA", "BUDE", "BUDK", "BUDY", "BUKS", "BULA", "BULE", "BULI", "BUŁA", "BUMA", "BURA", "BURE", "BURK", "BURT", "BURY", "BURZ", "BUSA", "BUSE", "BUSY", "BUTA", "BUTY", "BUZI", "BYKA", "BYKI", "BYKU", "BYLE", "BYLI", "BYŁA", "BYŁO", "BYŁY", "BYTE", "BYTU", "BYTY", "BZIE", "BZIK", "BZOM", "BZÓW", "CACK", "CALE", "CAŁA", "CAŁE", "CAŁY", "CARY", "CECH", "CELE", "CELI", "CELU", "CENA", "CENI", "CENY", "CERA", "CERK", "CERY", "CEWA", "CEWY", "CHAC", "CHAM", "CHCE", "CHIC", "CHIN", "CHLA", "CHLE", "CHCI", "CHOD", "CHOI", "CHOR", "CHOW", "CHÓD", "CHÓR", "CHRY", "CHCE", "CHUJ", "CHWY", "CHYL", "CHYŻ", "CIAŁ", "CIĄG", "CICH", "CIEC", "CIEK", "CIEN", "CIEŃ", "CIER", "CIES", "CIĘĆ", "CIMA", "CIOS", "CIPO", "CISA", "CISI", "CISZ", "CITA", "CITY", "CIUCH", "CIUL", "CIUP", "CIUT", "CIŻB", "CKNI", "CŁA", "CMOK", "CNOT", "COFA", "COLA", "COLE", "COLO", "CORA", "CÓRA", "CUDO", "CUDY", "CUKR", "CWAŁ", "CWEL", "CYAN", "CYBE", "CYCE", "CYCK", "CYCY", "CYFRA", "CYGA", "CYKL", "CYNA", "CYNK", "CYNY", "CYTO", "CZAD", "CZAI", "CZAK", "CZAP", "CZAR", "CZAS", "CZAT", "CZĄD", "CZCI", "CZEK", "CZEP", "CZER", "CZES", "CZĘŚ", "CZKA", "CZŁE", "CZOŁ", "CZUB", "CZUE", "CZUJ", "CZUL", "CZUŁ", "CZUM", "CZUW", "CZUŻ", "CZYI", "CZYJ", "CZYM", "CZYN", "CZYT", "DACH", "DAGA", "DAJE", "DAJĄ", "DALA", "DALE", "DALI", "DAMA", "DAMY", "DANA", "DANE", "DANI", "DANO", "DANY", "DARA", "DARM", "DARY", "DATA", "DATE", "DATK", "DATY", "DAWA", "DAWĆ", "DĄSA", "DBAĆ", "DBAM", "DBAŁ", "DECH", "DECK", "DECO", "DEDA", "DEDY", "DEEM", "DEIZ", "DEKA", "DEKI", "DELE", "DELI", "DEMO", "DEMY", "DENK", "DENN", "DERE", "DERK", "DERY", "DESA", "DESK", "DESM", "DESU", "DESZ", "DETA", "DEWY", "DĘBA", "DĘBI", "DĘBU", "DĘTE", "DĘTY", "DIAD", "DIAL", "DIAS", "DIES", "DIET", "DILU", "DIMU", "DINA", "DINO", "DISS", "DITA", "DITO", "DITY", "DIWA", "DIWY", "DLA", "DMIE", "DMĄ", "DMUCH"
]

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
            unique_words = sorted(list(set(COMMON_WORDS)))
            print(f"Seeding dictionary with {len(unique_words)} words...")
            for word in unique_words:
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
