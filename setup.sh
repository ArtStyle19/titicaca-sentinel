#!/bin/bash

# TITICACA SENTINEL - Setup Script

echo "🌊 Titicaca Sentinel - Setup"
echo "================================"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Authenticate with Google Earth Engine:"
echo "   earthengine authenticate"
echo ""
echo "2. Copy .env.example to .env and configure:"
echo "   cp .env.example .env"
echo "   nano .env  # Edit with your configuration"
echo ""
echo "3. (Optional) Export ROI to GeoJSON:"
echo "   source venv/bin/activate"
echo "   python gee/gee_processor.py"
echo ""
echo "4. Start the backend:"
echo "   ./start_backend.sh"
echo ""
echo "5. Start the frontend (in another terminal):"
echo "   ./start_frontend.sh"
echo ""
