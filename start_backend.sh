#!/bin/bash

# TITICACA SENTINEL - Backend Start Script

echo "🚀 Starting Titicaca Sentinel Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration."
    exit 1
fi

# Export environment variables
export $(cat .env | grep -v '^#' | xargs)

# Start FastAPI server
echo "✓ Starting FastAPI server on ${API_HOST}:${API_PORT}..."
cd backend
python main.py
