@echo off
REM StageMatch Antigravity - Quick Start Script (Windows)
REM This script sets up and starts the Antigravity system

echo 🚀 Starting StageMatch Antigravity System
echo ==========================================

REM Check if we're in the right directory
if not exist "requirements.txt" (
    echo ❌ Error: Please run this script from the backend directory
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 🐍 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Create temp directory
echo 📁 Creating temp directory...
if not exist "%USERPROFILE%\Documents\stageMatch_temp" (
    mkdir "%USERPROFILE%\Documents\stageMatch_temp"
)

REM Check for environment file
if not exist ".env" (
    if exist ".env.antigravity" (
        echo 📋 Copying environment configuration...
        copy .env.antigravity .env
        echo ⚠️  Please edit .env file with your actual Supabase credentials
    ) else (
        echo ❌ Error: No environment file found. Please create .env with your Supabase credentials
        pause
        exit /b 1
    )
)

REM Run database migration
echo 🗄️ Running database migration...
python scripts\migrate_antigravity.py

REM Start the server
echo 🌐 Starting FastAPI server...
echo ==========================================
echo ✅ Antigravity system ready!
echo 🌐 API available at: http://localhost:8000
echo 📚 Documentation at: http://localhost:8000/docs
echo ==========================================

uvicorn main:app --reload --host 0.0.0.0 --port 8000