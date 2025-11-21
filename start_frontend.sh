#!/bin/bash

# TITICACA SENTINEL - Frontend Start Script

echo "🚀 Starting Titicaca Sentinel Frontend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Using defaults..."
fi

# Export environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start Streamlit app
echo "✓ Starting Streamlit on port ${STREAMLIT_PORT:-8501}..."
cd frontend
streamlit run app.py --server.port=${STREAMLIT_PORT:-8501}
