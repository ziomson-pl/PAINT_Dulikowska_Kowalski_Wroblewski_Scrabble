import sys
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, DATABASE_URL
from app.models import User, Dictionary, Ranking
from app.auth import get_password_hash

# Common English Scrabble words
COMMON_WORDS = [
    # 2-letter words
    "AA", "AB", "AD", "AE", "AG", "AH", "AI", "AL", "AM", "AN", "AR", "AS", "AT", "AW", "AX", "AY",
    "BA", "BE", "BI", "BO", "BY", "DA", "DE", "DO", "ED", "EF", "EH", "EL", "EM", "EN", "ER", "ES", "ET", "EX",
    "FA", "FE", "GI", "GO", "HA", "HE", "HI", "HM", "HO", "ID", "IF", "IN", "IS", "IT",
    "JO", "KA", "KI", "LA", "LI", "LO", "MA", "ME", "MI", "MM", "MO", "MU", "MY",
    "NA", "NE", "NO", "NU", "OD", "OE", "OF", "OH", "OI", "OK", "OM", "ON", "OP", "OR", "OS", "OW", "OX", "OY",
    "PA", "PE", "PI", "PO", "QI", "RE", "SH", "SI", "SO", "TA", "TI", "TO",
    "UH", "UM", "UN", "UP", "US", "UT", "WE", "WO", "XI", "XU", "YA", "YE", "YO", "ZA",
    
    # 3-letter words
    "ACE", "ACT", "ADD", "AGE", "AGO", "AID", "AIM", "AIR", "ALL", "AND", "ANT", "ANY", "APE", "ARC", "ARE", "ARK", "ARM", "ART", "ASH", "ASK", "ATE",
    "BAD", "BAG", "BAN", "BAR", "BAT", "BAY", "BED", "BEE", "BET", "BIG", "BIN", "BIT", "BOX", "BOY", "BUD", "BUG", "BUS", "BUT", "BUY",
    "CAB", "CAN", "CAP", "CAR", "CAT", "COB", "COD", "COG", "COP", "COT", "COW", "COX", "COY", "CRY", "CUB", "CUD", "CUE", "CUP", "CUR", "CUT",
    "DAB", "DAD", "DAM", "DAY", "DEN", "DEW", "DID", "DIE", "DIG", "DIM", "DIN", "DIP", "DOC", "DOE", "DOG", "DOT", "DRY", "DUB", "DUD", "DUE", "DUG", "DUN", "DUO", "DYE",
    "EAR", "EAT", "EEL", "EGG", "EGO", "ELF", "ELK", "ELM", "EMU", "END", "ERA", "ERR", "EVE", "EWE", "EYE",
    "FAD", "FAN", "FAR", "FAT", "FAX", "FED", "FEE", "FEW", "FIG", "FIN", "FIR", "FIT", "FIX", "FLU", "FLY", "FOB", "FOE", "FOG", "FOR", "FOX", "FRY", "FUN", "FUR",
    "GAB", "GAG", "GAL", "GAP", "GAS", "GAY", "GEL", "GEM", "GET", "GIG", "GIN", "GNU", "GOB", "GOD", "GOT", "GUM", "GUN", "GUT", "GUY", "GYM",
    "HAD", "HAG", "HAM", "HAS", "HAT", "HAY", "HEM", "HEN", "HER", "HEW", "HEX", "HEY", "HID", "HIM", "HIP", "HIS", "HIT", "HOB", "HOD", "HOE", "HOG", "HOP", "HOT", "HOW", "HUB", "HUE", "HUG", "HUM", "HUT",
    "ICE", "ICY", "ILL", "IMP", "INK", "INN", "ION", "IRE", "IRK", "ITS", "IVY",
    "JAB", "JAG", "JAM", "JAR", "JAW", "JAY", "JET", "JIG", "JOB", "JOG", "JOT", "JOY", "JUG",
    "KEG", "KEN", "KEY", "KID", "KIN", "KIT",
    "LAB", "LAC", "LAD", "LAG", "LAP", "LAW", "LAX", "LAY", "LEA", "LED", "LEG", "LET", "LID", "LIE", "LIT", "LOG", "LOT", "LOW", "LUG",
    "MAD", "MAN", "MAP", "MAR", "MAT", "MAW", "MAY", "MEN", "MET", "MID", "MIX", "MOB", "MOM", "MOP", "MOW", "MUD", "MUG",
    "NAB", "NAG", "NAP", "NAY", "NET", "NEW", "NIL", "NIT", "NOB", "NOD", "NOR", "NOT", "NOW", "NUB", "NUN", "NUT",
    "OAK", "OAR", "OAT", "ODD", "OFF", "OFT", "OIL", "OLD", "ONE", "OPT", "ORB", "ORC", "ORE", "OUR", "OUT", "OWE", "OWL", "OWN",
    "PAD", "PAL", "PAN", "PAP", "PAR", "PAT", "PAW", "PAX", "PAY", "PEA", "PEG", "PEN", "PEP", "PER", "PET", "PEW", "PIE", "PIG", "PIN", "PIT", "PLY", "POD", "POP", "POT", "POX", "PRO", "PRY", "PUB", "PUG", "PUN", "PUP", "PUS", "PUT",
    "RAG", "RAM", "RAN", "RAP", "RAT", "RAW", "RAY", "RED", "REF", "REM", "REP", "REV", "RIB", "RID", "RIG", "RIM", "RIP", "ROB", "ROD", "ROE", "ROT", "ROW", "RUB", "RUG", "RUM", "RUN", "RUT", "RYE",
    "SAC", "SAD", "SAG", "SAP", "SAT", "SAW", "SAX", "SAY", "SEA", "SET", "SEW", "SEX", "SHE", "SHY", "SIN", "SIP", "SIR", "SIS", "SIT", "SIX", "SKI", "SKY", "SLY", "SOB", "SOD", "SON", "SOP", "SOT", "SOW", "SOX", "SOY", "SPA", "SPY", "STY", "SUB", "SUM", "SUN", "SUP",
    "TAB", "TAD", "TAG", "TAN", "TAP", "TAR", "TAT", "TAX", "TEA", "TEN", "THE", "THY", "TIC", "TIE", "TIN", "TIP", "TIT", "TOE", "TON", "TOO", "TOP", "TOT", "TOW", "TOY", "TRY", "TUB", "TUG", "TUN", "TUX", "TWO",
    "UGH", "UMP", "URN", "USE",
    "VAN", "VAT", "VET", "VEX", "VIA", "VIE", "VOW",
    "WAD", "WAG", "WAR", "WAS", "WAX", "WAY", "WEB", "WED", "WEE", "WET", "WHO", "WHY", "WIG", "WIN", "WIT", "WOE", "WOK", "WON", "WOO", "WOW",
    "YAK", "YAM", "YAP", "YAW", "YEA", "YEN", "YES", "YET", "YEW", "YIN", "YON", "YOU", "YOW", "YUK", "YUM", "YUP",
    "ZAP", "ZEN", "ZIG", "ZIP", "ZIT", "ZOO",
    
    # Common 4+ letter words
    "ABLE", "ACID", "ACRE", "ACTS", "AGED", "AGES", "AIDE", "AIDS", "AIMS", "AIRS", "AJAR", "AKIN", "ALARM", "ALIEN", "ALIGN", "ALIKE", "ALIVE", "ALLOW", "ALONE", "ALONG", "ALOUD", "ALTAR", "ALTER", "ANGEL", "ANGER", "ANGLE", "ANGRY", "APART", "APPLE", "APPLY", "ARENA", "ARGUE", "ARISE", "ARMED", "ARMOR", "AROSE", "ARRAY", "ARROW", "ASIDE", "ASSET", "AVOID", "AWAIT", "AWAKE", "AWARD", "AWARE",
    "BABY", "BACK", "BADGE", "BADLY", "BAKER", "BALLS", "BANDS", "BANKS", "BASED", "BASES", "BASIC", "BASIS", "BEACH", "BEANS", "BEARS", "BEAST", "BEGAN", "BEGIN", "BEGUN", "BEING", "BELOW", "BENCH", "BILLS", "BIRDS", "BIRTH", "BLACK", "BLADE", "BLAME", "BLANK", "BLIND", "BLOCK", "BLOOD", "BLOWN", "BLUES", "BOARD", "BOATS", "BONES", "BOOKS", "BOOTH", "BOOTS", "BOUND", "BOXES", "BRAIN", "BRAND", "BRASS", "BRAVE", "BREAD", "BREAK", "BREED", "BRIEF", "BRING", "BROAD", "BROKE", "BROWN", "BUILD", "BUILT", "BURNS", "BURST", "BUSES",
    "CABIN", "CABLE", "CALIF", "CALLS", "CALM", "CAME", "CAMP", "CANAL", "CARDS", "CARE", "CARGO", "CARRY", "CARS", "CASE", "CASH", "CAST", "CATCH", "CAUSE", "CELLS", "CHAIN", "CHAIR", "CHAOS", "CHARM", "CHART", "CHASE", "CHEAP", "CHECK", "CHEST", "CHIEF", "CHILD", "CHINA", "CHOSE", "CLAIM", "CLASS", "CLEAN", "CLEAR", "CLERK", "CLICK", "CLIFF", "CLIMB", "CLOCK", "CLOSE", "CLOTH", "CLOUD", "CLUBS", "COACH", "COAST", "COATS", "CODES", "COINS", "COLOR", "COMES", "COMIC", "CORAL", "CORPS", "COSTS", "COUCH", "COULD", "COUNT", "COURT", "COVER", "CRACK", "CRAFT", "CRASH", "CRAZY", "CREAM", "CREEK", "CREST", "CREWS", "CRIME", "CROSS", "CROWD", "CROWN", "CRUDE", "CURVE", "CYCLE",
    "DAILY", "DANCE", "DATED", "DATES", "DEALT", "DEATH", "DEBUT", "DECAY", "DECKS", "DEEPLY", "DELTA", "DENSE", "DEPTH", "DEVIL", "DIARY", "DIRTY", "DOUBT", "DOZEN", "DRAFT", "DRAIN", "DRAMA", "DRANK", "DRAWN", "DRAWS", "DREAM", "DRESS", "DRIED", "DRIFT", "DRILL", "DRINK", "DRIVE", "DROPS", "DROVE", "DRUMS", "DRUNK", "DYING",
    "EAGER", "EARLY", "EARTH", "EDGES", "EIGHT", "ELECT", "ELITE", "EMPTY", "ENEMY", "ENJOY", "ENTER", "ENTRY", "EQUAL", "ERROR", "EVENT", "EVERY", "EXACT", "EXIST", "EXTRA",
    "FACED", "FACES", "FACTS", "FADED", "FAILS", "FAIRY", "FAITH", "FALLS", "FALSE", "FANCY", "FARMS", "FATAL", "FATTY", "FAULT", "FAVOR", "FEARS", "FEAST", "FENCE", "FERRY", "FEWER", "FIBER", "FIELD", "FIFTH", "FIFTY", "FIGHT", "FILED", "FILLS", "FILMS", "FINAL", "FINDS", "FIRED", "FIRMS", "FIRST", "FIXED", "FLAGS", "FLAME", "FLASH", "FLEET", "FLESH", "FLIES", "FLOAT", "FLOOD", "FLOOR", "FLOWS", "FLUID", "FOCUS", "FOLKS", "FORCE", "FORMS", "FORTH", "FORTY", "FORUM", "FOUND", "FRAME", "FRANK", "FRAUD", "FRESH", "FRIED", "FRONT", "FROST", "FRUIT", "FULLY", "FUNDS",
    "GAMES", "GATES", "GAUGE", "GENES", "GENRE", "GHOST", "GIANT", "GIFTS", "GIRLS", "GIVEN", "GIVES", "GLAD", "GLASS", "GLOBE", "GLORY", "GLOVE", "GOALS", "GOING", "GOODS", "GRACE", "GRADE", "GRAIN", "GRAND", "GRANT", "GRAPE", "GRAPH", "GRASP", "GRASS", "GRAVE", "GREAT", "GREEK", "GREEN", "GREET", "GROSS", "GROUP", "GROVE", "GROWN", "GUARD", "GUESS", "GUEST", "GUIDE", "GUILD", "GUILT", "HABIT", "HANDS", "HANDY", "HAPPY", "HARSH", "HASTE", "HASTY", "HEART", "HEAVY", "HEDGE", "HELLO", "HELPS", "HENRY", "HERBS", "HILLS", "HINTS", "HOBBY", "HOLDS", "HOLES", "HOLLY", "HOMES", "HONEY", "HONOR", "HOPED", "HOPES", "HORNS", "HORSE", "HOTEL", "HOURS", "HOUSE", "HUMAN", "HUMOR",
    "IDEAL", "IDEAS", "IMAGE", "IMPLY", "INDEX", "INNER", "INPUT", "IRONY", "ISSUE", "ITEMS", "IVORY",
    "JAPAN", "JEANS", "JIMMY", "JOINS", "JOINT", "JOKES", "JONES", "JUDGE", "JUICE", "JUMPS",
    "KEEPS", "KILLS", "KING", "KINDS", "KNEE", "KNIFE", "KNOCK", "KNOWN", "KNOWS",
    "LABEL", "LABOR", "LACKS", "LAKES", "LAMPS", "LANDS", "LANES", "LARGE", "LASER", "LATER", "LAUGH", "LAYER", "LEADS", "LEARN", "LEASE", "LEAST", "LEAVE", "LEGAL", "LEMON", "LEVEL", "LEWIS", "LIGHT", "LIKED", "LIKES", "LIMIT", "LINED", "LINES", "LINKS", "LIONS", "LISTS", "LIVED", "LIVER", "LIVES", "LOADS", "LOANS", "LOCAL", "LOCKS", "LODGE", "LOGIC", "LOOKS", "LOOPS", "LOOSE", "LORDS", "LOSES", "LOVED", "LOVER", "LOVES", "LOWER", "LOYAL", "LUCKY", "LUNAR", "LUNCH", "LYING",
    "MAGIC", "MAJOR", "MAKER", "MAKES", "MALES", "MARCH", "MARKS", "MARRY", "MASKS", "MATCH", "MATES", "MATHS", "MAYBE", "MAYOR", "MEALS", "MEANS", "MEANT", "MEATS", "MEDAL", "MEDIA", "MEETS", "MENUS", "MERCY", "MERGE", "MERIT", "MERRY", "METAL", "METER", "METRO", "MIGHT", "MILES", "MINDS", "MINES", "MINOR", "MINUS", "MIXED", "MODEL", "MODES", "MONEY", "MONTH", "MORAL", "MOTOR", "MOUNT", "MOUSE", "MOUTH", "MOVED", "MOVES", "MOVIE", "MUSIC",
    "NAKED", "NAMED", "NAMES", "NASTY", "NAVAL", "NEEDS", "NERVE", "NEVER", "NEWLY", "NIGHT", "NOBLE", "NODES", "NOISE", "NORMS", "NORTH", "NOTED", "NOTES", "NOVEL", "NURSE",
    "OCCUR", "OCEAN", "OFFER", "OFTEN", "OLDER", "OLIVE", "ORBIT", "ORDER", "ORGAN", "OTHER", "OUGHT", "OUTER", "OVERS", "OWNED", "OWNER",
    "PACKS", "PAGES", "PAINT", "PAIRS", "PANEL", "PANIC", "PANTS", "PAPER", "PARKS", "PARTS", "PARTY", "PASTA", "PASTE", "PATCH", "PATHS", "PATIO", "PAUSE", "PEACE", "PEAKS", "PEARL", "PEERS", "PENNY", "PHASE", "PHONE", "PHOTO", "PIANO", "PICKS", "PIECE", "PILES", "PILOT", "PIPES", "PITCH", "PIZZA", "PLACE", "PLAIN", "PLANE", "PLANS", "PLANT", "PLATE", "PLAYS", "PLAZA", "PLOTS", "POEMS", "POETS", "POINT", "POKER", "POLAR", "POLES", "POLLS", "POOLS", "PORCH", "PORTS", "POSED", "POSTS", "POUND", "POWER", "PRESS", "PRICE", "PRIDE", "PRIME", "PRINT", "PRIOR", "PRIZE", "PROOF", "PROUD", "PROVE", "PULLS", "PULSE", "PUMPS", "PUNCH", "PUPIL", "PURSE", "QUEEN", "QUERY", "QUEST", "QUEUE", "QUICK", "QUIET", "QUILT", "QUITE", "QUOTE",
    "RACE", "RADIO", "RAISE", "RANGE", "RANKS", "RAPID", "RARELY", "RATED", "RATES", "RATIO", "REACH", "REACT", "READS", "READY", "REALM", "REBEL", "REFER", "REIGN", "RELAX", "RELAY", "REPLY", "RESET", "RIDER", "RIDES", "RIDGE", "RIFLE", "RIGHT", "RIGID", "RINGS", "RISEN", "RISES", "RISKS", "RIVAL", "RIVER", "ROADS", "ROBOT", "ROCKS", "ROCKY", "ROGER", "ROLES", "ROLLS", "ROMAN", "ROOMS", "ROOTS", "ROPES", "ROSES", "ROUGH", "ROUND", "ROUTE", "ROYAL", "RUGBY", "RUINS", "RULED", "RULES", "RURAL", "SADLY",
    "SAFER", "SAINT", "SALAD", "SALES", "SALON", "SANTA", "SAUCE", "SAVED", "SAVES", "SCALE", "SCARE", "SCENE", "SCENT", "SCOPE", "SCORE", "SCOTT", "SCOUT", "SCRAP", "SCREW", "SEALS", "SEATS", "SEEDS", "SEEMS", "SELLS", "SENDS", "SENSE", "SERUM", "SERVE", "SETUP", "SEVEN", "SHADE", "SHAFT", "SHAKE", "SHALL", "SHAME", "SHAPE", "SHARE", "SHARK", "SHARP", "SHEEP", "SHEER", "SHEET", "SHELF", "SHELL", "SHIFT", "SHINE", "SHIPS", "SHIRT", "SHOCK", "SHOES", "SHOOT", "SHOPS", "SHORE", "SHORT", "SHOTS", "SHOWN", "SHOWS", "SIDES", "SIGHT", "SIGNS", "SILK", "SILLY", "SIMON", "SINCE", "SIXTH", "SIXTY", "SIZED", "SIZES", "SKILL", "SKINS", "SKIRT", "SLATE", "SLAVE", "SLEEP", "SLIDE", "SLOPE", "SMALL", "SMART", "SMELL", "SMILE", "SMITH", "SMOKE", "SNAKE", "SNAPS", "SNOW", "SOCKS", "SOLAR", "SOLID", "SOLVE", "SONGS", "SORRY", "SORTS", "SOULS", "SOUND", "SOUTH", "SPACE", "SPARE", "SPARK", "SPEAK", "SPEED", "SPELL", "SPEND", "SPENT", "SPIKE", "SPINE", "SPLIT", "SPOKE", "SPORT", "SPOTS", "SPRAY", "SQUAD", "STACK", "STAFF", "STAGE", "STAIN", "STAKE", "STAMP", "STAND", "STARK", "STARS", "START", "STATE", "STAYS", "STEAL", "STEAM", "STEEL", "STEEP", "STEER", "STEMS", "STEPS", "STICK", "STILL", "STOCK", "STONE", "STOOD", "STOPS", "STORE", "STORM", "STORY", "STRAP", "STRAW", "STRIP", "STUCK", "STUDY", "STUFF", "STYLE", "SUGAR", "SUITE", "SUITS", "SUNNY", "SUPER", "SURGE", "SWEET", "SWEPT", "SWIFT", "SWING", "SWISS", "SWORD", "TABLE",
    "TAKEN", "TAKES", "TALES", "TALKS", "TANKS", "TAPES", "TASKS", "TASTE", "TAXES", "TEACH", "TEAMS", "TEARS", "TEENS", "TEETH", "TEMPO", "TENDS", "TENOR", "TENTS", "TERMS", "TESTS", "TEXAS", "TEXTS", "THANK", "THEFT", "THEIR", "THEME", "THERE", "THESE", "THICK", "THING", "THINK", "THIRD", "THOSE", "THREE", "THREW", "THROW", "THUMB", "THUS", "TIDES", "TIGER", "TIGHT", "TILES", "TIMER", "TIMES", "TIRED", "TITLE", "TODAY", "TOMMY", "TONES", "TOOLS", "TOOTH", "TOPIC", "TOTAL", "TOUCH", "TOUGH", "TOURS", "TOWER", "TOWNS", "TOXIC", "TRACK", "TRACT", "TRADE", "TRAIL", "TRAIN", "TRAIT", "TRANS", "TRASH", "TREAT", "TREND", "TRIAL", "TRIBE", "TRICK", "TRIED", "TRIES", "TRIPS", "TROOP", "TRUCK", "TRUNK", "TRUST", "TRUTH", "TUBES", "TUMOR", "TUNED", "TURNS", "TUTOR", "TWICE", "TWINS", "TWIST", "TYPES", "ULTRA",
    "UNCLE", "UNDER", "UNDUE", "UNION", "UNITE", "UNITS", "UNITY", "UNTIL", "UPPER", "UPSET", "URBAN", "URGED", "USAGE", "USERS", "USUAL", "UTTER", "VAGUE", "VALID", "VALUE", "VALVE", "VAULT", "VENUE", "VERGE", "VERSE", "VIDEO", "VIEWS", "VILLA", "VINYL", "VIRAL", "VIRUS", "VISIT", "VITAL", "VIVID", "VOCAL", "VOICE", "VOTER", "VOTES", "WAGES", "WAGON", "WAIST", "WALKS", "WALLS", "WANTS", "WASTE", "WATCH", "WATER", "WAVES", "WAYS", "WEEKS", "WEIGH", "WELLS", "WELSH", "WHALE", "WHEAT", "WHEEL", "WHERE", "WHICH", "WHILE", "WHITE", "WHOLE", "WHOSE", "WIDER", "WIDOW", "WIDTH", "WINDS", "WINES", "WINGS", "WIPED", "WIRED", "WIRES", "WISDOM", "WITCH", "WOMAN", "WOMEN", "WOODS", "WORDS", "WORKS", "WORLD", "WORRY", "WORSE", "WORST", "WORTH", "WOULD", "WOUND", "WRAPPED", "WRIST", "WRITE", "WRONG", "WROTE", "YARDS", "YEARS", "YEAST", "YIELD", "YOUNG", "YOURS", "YOUTH", "ZONES"
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
            print(f"Seeding dictionary with {len(COMMON_WORDS)} words...")
            for word in COMMON_WORDS:
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
