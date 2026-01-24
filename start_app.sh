#!/bin/bash
set -e


echo " Stopping old containers..."
docker compose down -v || true
echo

echo " Building and starting containers..."
docker compose up --build -d
echo

echo " Containers status:"
docker compose ps
echo

echo "======================================"
echo " Application started successfully!"
echo " Frontend: http://localhost:3000"
echo " Backend:  http://localhost:8000"
echo " Database: localhost:5432"
echo "======================================"
