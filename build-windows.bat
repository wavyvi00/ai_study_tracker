@echo off
echo 🏗️  Building FocusWin for Windows...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    exit /b 1
)

REM Create/activate virtual environment
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo 📥 Installing build dependencies...
python -m pip install --upgrade pip
pip install -r requirements-windows.txt

REM Clean previous builds
echo 🧹 Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec

REM Build the app with PyInstaller
echo 🔨 Building application bundle...
pyinstaller ^
    --name "FocusWin" ^
    --windowed ^
    --onedir ^
    --add-data "templates;templates" ^
    --add-data "static;static" ^
    --hidden-import "engineio.async_drivers.threading" ^
    --hidden-import "flask" ^
    --hidden-import "pywebview" ^
    --collect-all "flask" ^
    --collect-all "pywebview" ^
    desktop_app.py

echo.
echo ✅ Build complete!
echo.
echo 📦 Your standalone app is located at:
echo    dist\FocusWin\FocusWin.exe
echo.
echo To run the app:
echo    1. Navigate to the dist\FocusWin folder
echo    2. Double-click FocusWin.exe
echo.
echo ⚠️  Note: Windows may show a security warning on first run.
echo    Click "More info" then "Run anyway"
echo.
