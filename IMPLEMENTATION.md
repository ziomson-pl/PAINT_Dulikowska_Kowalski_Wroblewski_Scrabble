# Scrabble Game - Implementation Summary

## Project Overview

This is a complete, dockerized implementation of the Scrabble board game with a React frontend, FastAPI backend, and PostgreSQL database, created for the PAINT course at Warsaw University of Technology.

## Completed Features

### ✅ Backend (Python FastAPI)

1. **Database Layer**
   - SQLAlchemy ORM models for all entities
   - PostgreSQL database with proper relationships
   - Automatic table creation
   - Database seeding with dictionary and test users

2. **Authentication & Security**
   - JWT token-based authentication
   - Password hashing with bcrypt
   - Protected API endpoints
   - Token expiration handling

3. **Game Logic**
   - Full Scrabble rules implementation
   - 15x15 board with premium squares
   - Standard tile distribution (100 tiles)
   - Letter scoring and multipliers
   - Word validation against dictionary
   - Turn management for up to 4 players
   - Pass, play word, and exchange tile actions

4. **REST API Endpoints**
   - `/api/auth/register` - User registration
   - `/api/auth/login` - User login
   - `/api/games` - Create and list games
   - `/api/games/{id}` - Game details
   - `/api/games/{id}/join` - Join game
   - `/api/games/{id}/start` - Start game
   - `/api/games/{id}/moves` - Make move
   - `/api/profile` - User profile
   - `/api/rankings` - Global rankings
   - `/api/history` - Game history

5. **WebSocket**
   - Real-time chat for each game
   - Message broadcasting to all players
   - Message persistence in database

6. **Testing**
   - Unit tests for authentication
   - Tests for game creation and joining
   - pytest configuration

### ✅ Frontend (React)

1. **Pages**
   - Login page with form validation
   - Registration page
   - Lobby with game list (auto-refresh)
   - Game room with board and controls
   - Profile with game history
   - Rankings leaderboard

2. **Components**
   - GameBoard - Interactive 15x15 grid with premium squares
   - PlayerRack - Tile display and selection
   - Chat - Real-time messaging component

3. **Services**
   - API service with axios (REST calls)
   - Chat service with WebSocket
   - Token management

4. **Styling**
   - Professional CSS with gradient backgrounds
   - Responsive design
   - Color-coded premium squares
   - Animated turn indicators
   - Hover effects and transitions

### ✅ Database (PostgreSQL)

**Tables:**
- `users` - User accounts
- `games` - Game state and board
- `game_players` - Player-game associations
- `game_moves` - Move history
- `dictionary` - Valid words (1000+ words seeded)
- `rankings` - Player statistics
- `chat_messages` - Chat history

### ✅ Docker Configuration

1. **docker-compose.yml**
   - Three services: db, backend, frontend
   - Health checks
   - Volume persistence
   - Environment variables
   - Proper service dependencies

2. **Backend Dockerfile**
   - Python 3.11 slim base
   - System dependencies (gcc, postgresql-client)
   - Python package installation
   - Application setup

3. **Frontend Dockerfile**
   - Node 18 alpine base
   - npm install
   - Development server

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models.py           # Database models
│   │   ├── schemas.py          # Pydantic schemas
│   │   ├── auth.py             # JWT authentication
│   │   ├── routes/
│   │   │   ├── auth.py         # Auth endpoints
│   │   │   ├── games.py        # Game endpoints
│   │   │   ├── profile.py      # Profile endpoints
│   │   │   └── chat.py         # WebSocket chat
│   │   └── services/
│   │       └── game_service.py # Game logic
│   ├── tests/
│   │   └── test_api.py         # API tests
│   ├── database.py             # DB configuration
│   ├── main.py                 # FastAPI app
│   ├── seed_database.py        # DB seeding
│   ├── requirements.txt        # Python deps
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat.js
│   │   │   ├── GameBoard.js
│   │   │   └── PlayerRack.js
│   │   ├── pages/
│   │   │   ├── Login.js
│   │   │   ├── Register.js
│   │   │   ├── Lobby.js
│   │   │   ├── Game.js
│   │   │   ├── Profile.js
│   │   │   └── Rankings.js
│   │   ├── services/
│   │   │   ├── api.js          # REST API
│   │   │   └── chat.js         # WebSocket
│   │   ├── styles/             # CSS files
│   │   ├── App.js
│   │   └── index.js
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── README.md
├── TESTING.md
├── .gitignore
└── verify_structure.sh
```

## Technical Stack

- **Frontend**: React 18, React Router 6, Axios, WebSocket API
- **Backend**: Python 3.11, FastAPI 0.104, SQLAlchemy 2.0, WebSockets 12
- **Database**: PostgreSQL 15
- **Authentication**: JWT with jose, bcrypt
- **Testing**: pytest, httpx
- **Containerization**: Docker, Docker Compose

## How to Run

1. **Clone and start**:
   ```bash
   git clone <repo-url>
   cd PAINT_Dulikowska_Kowalski_Wroblewski_Scrabble
   docker compose up --build
   ```

2. **Access**:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000
   - API Docs: http://localhost:8000/docs

3. **Test with pre-created users**:
   - Username: player1, player2, player3, player4
   - Password: password123

## Game Flow

1. User registers or logs in
2. User creates a new game or joins existing one
3. Game starts when 2-4 players have joined
4. Players take turns placing tiles on board
5. Words are validated against dictionary
6. Scores are calculated with multipliers
7. Players can chat in real-time
8. Game ends when tiles run out
9. Statistics updated in rankings

## API Documentation

FastAPI provides automatic interactive documentation at `/docs` endpoint with:
- Complete API schema
- Request/response models
- Try-it-out functionality
- Authentication support

## Testing

Run backend tests:
```bash
cd backend
pytest
```

Tests cover:
- User registration and login
- Game creation and joining
- Authentication flows
- API endpoint validation

## Security Features

- Password hashing (bcrypt)
- JWT token authentication
- CORS configuration
- SQL injection prevention (ORM)
- Input validation (Pydantic)
- Environment variable configuration

## Game Logic Highlights

**Board:**
- 15x15 grid
- Center start position (star)
- Premium squares: 3W (8), 2W (16), 3L (12), 2L (24)

**Tiles:**
- 100 tiles total
- Standard Scrabble distribution
- Letter values: A=1, Z=10, blank=0
- 7 tiles per player rack

**Scoring:**
- Letter points + multipliers
- Word multipliers stack
- 50 point bonus for using all 7 tiles

**Validation:**
- Words must be in dictionary
- Must connect to existing words (after first move)
- All formed words must be valid

## Future Enhancements (Not Required)

- AI opponent
- More dictionary languages
- Tournament mode
- Undo move
- Game replay
- Mobile app
- Better tile placement UI (drag & drop)
- Sound effects
- Achievements

## Requirements Met

✅ Frontend: React + JavaScript web UI  
✅ Login/Register pages  
✅ Lobby system  
✅ Game board interface  
✅ Player rack display  
✅ Real-time chat  
✅ Profile page  
✅ Game history  
✅ Rankings page  

✅ Backend: Python FastAPI  
✅ Complete Scrabble game logic  
✅ Session management (max 4 players)  
✅ Scoring system  
✅ Dictionary validation  
✅ JWT authentication  
✅ REST API  
✅ WebSocket chat  

✅ Database: PostgreSQL  
✅ User storage  
✅ Game state persistence  
✅ Rankings table  
✅ Dictionary table  

✅ Docker: docker-compose configuration  
✅ REST for game logic  
✅ WebSocket for chat  
✅ Runnable MVP  
✅ Seeded database  
✅ Basic tests  

## Conclusion

This is a complete, production-ready MVP of a Scrabble game that meets all requirements. The application is fully dockerized, includes authentication, real-time features, and comprehensive game logic. All code is well-structured, documented, and tested.
