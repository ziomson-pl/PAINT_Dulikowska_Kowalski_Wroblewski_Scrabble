#!/bin/bash

echo "=== Scrabble Game Project Structure Verification ==="
echo ""

# Check directory structure
echo "Checking project structure..."
DIRS=("backend" "frontend" "backend/app" "backend/app/routes" "backend/app/services" "backend/tests" "frontend/src" "frontend/src/components" "frontend/src/pages" "frontend/src/services" "frontend/src/styles")

for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "✓ $dir exists"
    else
        echo "✗ $dir missing"
    fi
done

echo ""
echo "Checking Docker files..."
FILES=("docker-compose.yml" "backend/Dockerfile" "frontend/Dockerfile")
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file missing"
    fi
done

echo ""
echo "Checking backend files..."
BACKEND_FILES=("backend/main.py" "backend/database.py" "backend/requirements.txt" "backend/seed_database.py" "backend/app/models.py" "backend/app/schemas.py" "backend/app/auth.py" "backend/app/routes/auth.py" "backend/app/routes/games.py" "backend/app/routes/profile.py" "backend/app/routes/chat.py" "backend/app/services/game_service.py" "backend/tests/test_api.py")

for file in "${BACKEND_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file missing"
    fi
done

echo ""
echo "Checking frontend files..."
FRONTEND_FILES=("frontend/package.json" "frontend/public/index.html" "frontend/src/index.js" "frontend/src/App.js" "frontend/src/pages/Login.js" "frontend/src/pages/Register.js" "frontend/src/pages/Lobby.js" "frontend/src/pages/Game.js" "frontend/src/pages/Profile.js" "frontend/src/pages/Rankings.js" "frontend/src/components/GameBoard.js" "frontend/src/components/PlayerRack.js" "frontend/src/components/Chat.js" "frontend/src/services/api.js" "frontend/src/services/chat.js")

for file in "${FRONTEND_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file missing"
    fi
done

echo ""
echo "Checking Python syntax..."
cd backend
python3 -m py_compile main.py 2>&1
if [ $? -eq 0 ]; then
    echo "✓ main.py syntax OK"
else
    echo "✗ main.py has syntax errors"
fi

python3 -m py_compile database.py 2>&1
if [ $? -eq 0 ]; then
    echo "✓ database.py syntax OK"
else
    echo "✗ database.py has syntax errors"
fi

python3 -m py_compile app/models.py 2>&1
if [ $? -eq 0 ]; then
    echo "✓ app/models.py syntax OK"
else
    echo "✗ app/models.py has syntax errors"
fi

cd ..

echo ""
echo "=== Verification Complete ==="
echo ""
echo "Summary:"
echo "- Backend: FastAPI with JWT auth, game logic, WebSocket chat"
echo "- Frontend: React with login, lobby, game board, chat, profile, rankings"
echo "- Database: PostgreSQL with models for users, games, rankings, dictionary"
echo "- Docker: docker-compose with 3 services (frontend, backend, database)"
echo ""
echo "To run the application:"
echo "  docker compose up --build"
echo ""
echo "Access:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
