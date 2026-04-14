#!/bin/bash
# StageMatch Antigravity - Quick Start Script
# This script sets up and starts the Antigravity system

set -e

echo "🚀 Starting StageMatch Antigravity System"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create temp directory
echo "📁 Creating temp directory..."
mkdir -p ~/Documents/stageMatch_temp

# Check for environment file
if [ ! -f ".env" ]; then
    if [ -f ".env.antigravity" ]; then
        echo "📋 Copying environment configuration..."
        cp .env.antigravity .env
        echo "⚠️  Please edit .env file with your actual Supabase credentials"
    else
        echo "❌ Error: No environment file found. Please create .env with your Supabase credentials"
        exit 1
    fi
fi

# Run database migration
echo "🗄️ Running database migration..."
python scripts/migrate_antigravity.py

# Start the server
echo "🌐 Starting FastAPI server..."
echo "=========================================="
echo "✅ Antigravity system ready!"
echo "🌐 API available at: http://localhost:8000"
echo "📚 Documentation at: http://localhost:8000/docs"
echo "=========================================="

uvicorn main:app --reload --host 0.0.0.0 --port 8000