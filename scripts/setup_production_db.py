"""
Database setup script for Digital Ocean deployment
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import asyncio
from sqlalchemy import text
from app.db.database import engine, SessionLocal
from app.models.song import Song

async def setup_database():
    """Setup database with pgvector extension and tables"""
    
    print("🔧 Setting up database for production...")
    
    try:
        # Connect to database
        db = SessionLocal()
        
        # Enable pgvector extension
        print("📦 Enabling pgvector extension...")
        db.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        db.commit()
        
        # Create tables
        print("📊 Creating tables...")
        from app.db.database import create_tables
        create_tables()
        
        # Verify setup
        result = db.execute(text("SELECT 1")).fetchone()
        if result:
            print("✅ Database setup completed successfully!")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(setup_database())
