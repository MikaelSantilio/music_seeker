#!/bin/bash

# Build script para Digital Ocean App Platform
echo "🚀 Building MusicSeeker for production..."

# Install system dependencies for pgvector
apt-get update
apt-get install -y postgresql-client libpq-dev gcc

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify critical dependencies
python -c "import psycopg2; print('✅ psycopg2 installed')"
python -c "import openai; print('✅ openai installed')"
python -c "import fastapi; print('✅ fastapi installed')"

echo "✅ Build completed successfully!"
