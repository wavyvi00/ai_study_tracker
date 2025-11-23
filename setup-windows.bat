@echo off
echo 🚀 Setting up FocusWin for Windows...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    exit /b 1
)

echo ✅ Python found

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements-windows.txt

echo.
echo ✅ Setup complete!
echo.
echo To start developing:
echo   1. Activate the virtual environment: venv\Scripts\activate.bat
echo   2. Run the app: python desktop_app.py
echo.
echo To build a standalone app:
echo   build-windows.bat
echo.
