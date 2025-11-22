#!/bin/bash

# AI Study Tracker - Build Script
# Creates a standalone macOS application bundle

set -e

echo "🏗️  Building AI Study Tracker standalone app..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create/activate virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing build dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist *.spec

# Build the app with PyInstaller
echo "🔨 Building application bundle..."
pyinstaller \
    --name "AI Study Tracker" \
    --windowed \
    --onedir \
    --add-data "templates:templates" \
    --add-data "static:static" \
    --hidden-import "engineio.async_drivers.threading" \
    --hidden-import "flask" \
    --hidden-import "pywebview" \
    --collect-all "flask" \
    --collect-all "pywebview" \
    --osx-bundle-identifier "com.aistudy.tracker" \
    desktop_app.py

echo ""
echo "✅ Build complete!"
echo ""
echo "📦 Your standalone app is located at:"
echo "   dist/AI Study Tracker.app"
echo ""
echo "To run the app:"
echo "   1. Navigate to the dist folder"
echo "   2. Double-click 'AI Study Tracker.app'"
echo "   3. If macOS blocks it, right-click → Open"
echo ""
echo "⚠️  Note: The app is not code-signed. Users will need to:"
echo "   - Right-click → Open (first time only)"
echo "   - Or allow it in System Settings → Privacy & Security"
echo ""
