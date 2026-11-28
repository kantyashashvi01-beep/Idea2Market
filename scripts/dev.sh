#!/usr/bin/env bash
set -e

echo "Starting Idea2market local environment..."

# 1. Start local PostgreSQL via Docker if available
if command -v docker &> /dev/null; then
  echo "Starting local PostgreSQL container..."
  docker compose up -d postgres || true
fi

# 2. Check backend environment
if [ ! -f "backend/.env" ]; then
  echo "Copying backend/.env.example to backend/.env"
  cp backend/.env.example backend/.env
fi

if [ ! -f "frontend/.env.local" ]; then
  echo "Copying frontend/.env.example to frontend/.env.local"
  cp frontend/.env.example frontend/.env.local
fi

echo "To run backend:"
echo "  cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000"
echo ""
echo "To run frontend:"
echo "  cd frontend && npm run dev"
