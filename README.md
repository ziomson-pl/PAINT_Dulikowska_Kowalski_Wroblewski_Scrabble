# PAINT - Scrabble Game

A full-stack, dockerized Scrabble game implementation for the PAINT course at Warsaw University of Technology.

## Features

### Frontend (React + JavaScript)
- **Authentication**: Login and registration pages with JWT token management
- **Lobby**: Browse and join available games, create new games
- **Game Board**: Interactive 15x15 Scrabble board with premium squares (double/triple word/letter)
- **Player Rack**: Display and manage your 7 tiles
- **Real-time Chat**: WebSocket-based chat for each game
- **Profile**: View game history and personal statistics
- **Rankings**: Global leaderboard with player ratings and statistics

### Backend (Python FastAPI)
- **Game Logic**: Complete Scrabble rules implementation
  - Tile distribution and scoring
  - Word validation against dictionary
  - Premium square multipliers
  - Turn management (up to 4 players per game)
- **Authentication**: JWT-based user authentication
- **REST API**: Endpoints for all game operations
- **WebSocket**: Real-time chat functionality
- **Database**: PostgreSQL for persistent storage

### Database (PostgreSQL)
- Users and authentication
- Games and game state
- Player statistics and rankings
- Word dictionary (seeded with common English words)
- Chat messages

## Architecture

```
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── models.py      # SQLAlchemy models
│   │   ├── schemas.py     # Pydantic schemas
│   │   ├── auth.py        # JWT authentication
│   │   ├── routes/        # API endpoints
│   │   └── services/      # Game logic
│   ├── database.py        # Database configuration
│   ├── main.py           # FastAPI app
│   ├── seed_database.py  # Database seeding
│   └── tests/            # Backend tests
├── frontend/          # React application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API and WebSocket services
│   │   └── styles/        # CSS files
│   └── public/           # Static files
└── docker-compose.yml    # Docker orchestration
```

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd PAINT_Dulikowska_Kowalski_Wroblewski_Scrabble
   ```

2. **Start the application**:
   Use the provided start script to build and run the application. This script handles container cleanup, network creation, and correct startup order better than standard docker-compose for this project setup.
   ```bash
   bash start_app.sh
   ```

   *Note: You may be prompted for your password as the script uses `sudo` to manage Docker containers.*

   The script will:
   - Clean up any existing Scrabble containers
   - Create a dedicated Docker network
   - Start the PostgreSQL database
   - Build and start the Backend (FastAPI)
   - Build and start the Frontend (React/Vite)

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

4. **Test with pre-created users**:
   - Username: `player1`, `player2`, `player3`, or `player4`
   - Password: `password123`

## Development

### Running Tests

Backend tests:
```bash
cd backend
docker-compose exec backend pytest
```


### Database Access

The application uses **PostgreSQL**. You can connect to it using the following credentials:
- **Host**: `localhost`
- **Port**: `5432`
- **Database**: `scrabble`
- **Username**: `scrabble_user`
- **Password**: `scrabble_pass`

### API Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

#### Games
- `GET /api/games` - List all games
- `POST /api/games` - Create new game
- `GET /api/games/{id}` - Get game details
- `POST /api/games/{id}/join` - Join a game
- `POST /api/games/{id}/start` - Start the game
- `POST /api/games/{id}/moves` - Make a move
- `GET /api/games/{id}/moves` - Get move history
- `GET /api/games/{id}/messages` - Get chat messages

#### Profile & Rankings
- `GET /api/profile` - Get current user profile
- `GET /api/rankings` - Get global rankings
- `GET /api/history` - Get user's game history

#### WebSocket
- `WS /ws/chat/{game_id}` - Real-time chat for a game

## Game Rules

- **Players**: 2-4 players per game
- **Tiles**: Standard Scrabble distribution (100 tiles including 2 blanks)
- **Board**: 15x15 grid with premium squares
- **Scoring**: Based on letter values and multipliers
- **Dictionary**: Pre-seeded with common English words
- **Turns**: Players take turns placing tiles to form words
- **Actions**: Play word, pass turn, or exchange tiles
- **End Game**: When tile bag is empty and a player uses all their tiles

## Technology Stack

- **Frontend**: React 18, React Router, Axios, WebSocket
- **Backend**: Python 3.11, FastAPI, SQLAlchemy, WebSockets
- **Database**: PostgreSQL 15
- **Authentication**: JWT tokens with bcrypt
- **Containerization**: Docker, Docker Compose

## Project Structure Details

### Backend Models
- `User`: User accounts and authentication
- `Game`: Game state and board
- `GamePlayer`: Player-game association with scores and racks
- `GameMove`: Move history
- `Dictionary`: Valid Scrabble words
- `Ranking`: Player statistics and ratings
- `ChatMessage`: Chat messages per game

### Frontend Components
- `Login/Register`: Authentication forms
- `Lobby`: Game browser and creation
- `Game`: Main game interface
- `GameBoard`: Interactive board display
- `PlayerRack`: Tile management
- `Chat`: Real-time messaging
- `Profile`: User statistics
- `Rankings`: Leaderboard

## License

This project was created for educational purposes as part of the PAINT course at Warsaw University of Technology.

## Authors

- Dulikowska
- Kowalski
- Wróblewski
