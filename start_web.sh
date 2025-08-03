#!/bin/bash

# MusicSeeker Web Interface Launcher
echo "🎵 Starting MusicSeeker Web Interface..."
echo "========================================"

# Activate virtual environment
source .venv/bin/activate

# Check if database is ready
echo "🔍 Checking database connection..."
python -c "
import sys
sys.path.append('.')
from app.db.database import SessionLocal
try:
    db = SessionLocal()
    db.execute('SELECT 1')
    db.close()
    print('✅ Database connection OK')
except Exception as e:
    print(f'❌ Database error: {e}')
    print('Make sure PostgreSQL is running and configured correctly.')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Database check failed. Exiting..."
    exit 1
fi

echo ""
echo "🚀 Starting FastAPI server..."
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🔍 Web Interface: http://localhost:8000/search"
echo "💻 Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
