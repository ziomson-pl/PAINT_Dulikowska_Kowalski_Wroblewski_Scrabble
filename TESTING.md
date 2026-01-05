# Testing and Deployment Notes

## Known Issues

### SSL Certificate Issue in Sandboxed Environment
When building with Docker in certain environments, you may encounter SSL certificate verification errors when downloading Python packages from PyPI. This has been addressed in the Dockerfile by adding trusted host flags.

If you still encounter issues, you can:
1. Build on a different network/environment
2. Use pre-built images
3. Modify pip configuration to trust PyPI hosts

## Manual Testing (Without Docker)

### Backend Testing

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Setup database (requires PostgreSQL):
```bash
export DATABASE_URL="postgresql://scrabble_user:scrabble_pass@localhost:5432/scrabble"
export SECRET_KEY="your-secret-key"
python seed_database.py
```

3. Run backend:
```bash
uvicorn main:app --reload
```

4. Run tests:
```bash
pytest
```

### Frontend Testing

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start development server:
```bash
npm start
```

## Production Deployment

For production deployment:

1. Update `SECRET_KEY` in docker-compose.yml to a secure random value
2. Use environment files for sensitive configuration
3. Set up proper SSL/TLS certificates for HTTPS
4. Configure proper CORS settings for your domain
5. Set up database backups
6. Consider using managed PostgreSQL service

## Architecture Validation

The implementation follows the requirements:

✅ **Services**:
- Frontend: React + JavaScript web UI
- Backend: Python FastAPI with game logic
- Database: PostgreSQL

✅ **Features**:
- Authentication (JWT)
- Game lobby and creation
- Full Scrabble game logic (board, tiles, scoring)
- Dictionary validation
- Real-time chat (WebSocket)
- Player rankings and history
- Session management (max 4 players)

✅ **Docker Configuration**:
- docker-compose.yml for orchestration
- Separate Dockerfiles for frontend and backend
- Health checks for database
- Volume persistence for PostgreSQL data

✅ **Testing**:
- Basic backend tests with pytest
- Test coverage for authentication and game creation

✅ **Documentation**:
- Comprehensive README
- API documentation via FastAPI Swagger UI
- Setup instructions

## Security Considerations

- JWT tokens for authentication
- Password hashing with bcrypt
- CORS configuration for frontend-backend communication
- SQL injection prevention via SQLAlchemy ORM
- Input validation with Pydantic

## Game Logic Details

The Scrabble implementation includes:
- Standard 15x15 board
- 100 tiles with standard distribution
- Premium squares (double/triple word/letter)
- Turn-based gameplay
- Word validation against dictionary
- Scoring with multipliers
- Pass and exchange tile actions
- Game end detection
