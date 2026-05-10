@echo off
REM Setup script for Market Reports Dashboard (Windows)

echo ==========================================
echo Market Reports Dashboard - Setup Script
echo ==========================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo   Found %PYTHON_VERSION%
echo.

REM Create virtual environment
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo   Virtual environment created
) else (
    echo   Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo   Virtual environment activated
echo.

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo   Dependencies installed
echo.

REM Create cache directory
echo Setting up cache directory...
if not exist "cache" mkdir cache
echo   Cache directory ready
echo.

REM Check for .env file
echo Checking environment configuration...
if not exist ".env" (
    echo   [WARNING] .env file not found!
    echo.
    echo   Please create a .env file with the following variables:
    echo   CLAUDE_API_KEY=your_api_key
    echo   FRED_API_KEY=your_api_key
    echo   NEWSAPI_KEY=your_api_key
    echo   FLASK_ENV=development
    echo   SECRET_KEY=your_secret_key
    echo.
) else (
    echo   ^✓ .env file found
)
echo.

echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo To start the development server:
echo   1. Run: venv\Scripts\activate.bat
echo   2. Run: python app.py
echo.
echo Then open: http://localhost:5000
echo.
pause
