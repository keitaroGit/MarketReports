#!/bin/bash
# Setup script for Market Reports Dashboard

echo "=========================================="
echo "Market Reports Dashboard - Setup Script"
echo "=========================================="
echo ""

# Check Python installation
echo "✓ Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "  Found Python $PYTHON_VERSION"
echo ""

# Create virtual environment
echo "✓ Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  Virtual environment created"
else
    echo "  Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate
echo "  Virtual environment activated"
echo ""

# Install dependencies
echo "✓ Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "  Dependencies installed"
echo ""

# Create cache directory
echo "✓ Setting up cache directory..."
mkdir -p cache
echo "  Cache directory ready"
echo ""

# Check for .env file
echo "✓ Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "  ✗ .env file not found!"
    echo ""
    echo "  Please create a .env file with the following variables:"
    echo "  CLAUDE_API_KEY=your_api_key"
    echo "  FRED_API_KEY=your_api_key"
    echo "  NEWSAPI_KEY=your_api_key"
    echo "  FLASK_ENV=development"
    echo "  SECRET_KEY=your_secret_key"
    echo ""
else
    echo "  ✓ .env file found"
fi
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To start the development server:"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "Then open: http://localhost:5000"
echo ""
