#!/bin/bash
set -e

# Cleanup
echo "Cleaning up old containers..."
echo "kuba" | sudo -S docker rm -f scrabble_db scrabble_backend scrabble_frontend || true
echo "kuba" | sudo -S docker network rm scrabble_net || true

# Create network
echo "Creating network..."
echo "kuba" | sudo -S docker network create scrabble_net

# Start Database
echo "Starting Database..."
echo "kuba" | sudo -S docker run -d \
  --name scrabble_db \
  --network scrabble_net \
  -e POSTGRES_DB=scrabble \
  -e POSTGRES_USER=scrabble_user \
  -e POSTGRES_PASSWORD=scrabble_pass \
  -v scrabble_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:15-alpine

echo "Waiting for DB to be ready..."
sleep 5

# Build and Start Backend
echo "Building Backend..."
echo "kuba" | sudo -S docker build -t scrabble_backend ./backend

echo "Starting Backend..."
echo "kuba" | sudo -S docker run -d \
  --name scrabble_backend \
  --network scrabble_net \
  -e DATABASE_URL=postgresql://scrabble_user:scrabble_pass@scrabble_db:5432/scrabble \
  -e SECRET_KEY=your-secret-key-change-in-production \
  -e ALGORITHM=HS256 \
  -e ACCESS_TOKEN_EXPIRE_MINUTES=30 \
  -v $(pwd)/backend:/app \
  -p 8000:8000 \
  scrabble_backend \
  sh -c "python seed_database.py && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

# Build and Start Frontend
echo "Building Frontend..."
echo "kuba" | sudo -S docker build -t scrabble_frontend ./frontend

echo "Starting Frontend..."
# Note: Anonymous volume for node_modules to preserve installed deps
echo "kuba" | sudo -S docker run -d \
  --name scrabble_frontend \
  --network scrabble_net \
  -e REACT_APP_API_URL=http://localhost:8000 \
  -e REACT_APP_WS_URL=ws://localhost:8000 \
  -v $(pwd)/frontend:/app \
  -v /app/node_modules \
  -p 3000:3000 \
  scrabble_frontend

echo "Application started!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
