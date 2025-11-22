#!/bin/bash

# AI Study Tracker - Development Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up AI Study Tracker development environment..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start developing:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Run the app: python3 desktop_app.py"
echo ""
echo "To build a standalone app:"
echo "  ./build.sh"
echo ""
