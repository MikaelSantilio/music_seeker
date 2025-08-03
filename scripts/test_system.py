"""
Test script to verify embedding functionality without using API quota
"""

import os
import sys

# Add app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.database import SessionLocal
from app.models.song import Song
from app.config import settings


def test_database_connection():
    """Test database connection and query songs"""
    print("🔍 Testing database connection...")
    
    try:
        db = SessionLocal()
        
        # Test basic query
        total_songs = db.query(Song).count()
        songs_with_embeddings = db.query(Song).filter(Song.embedding.isnot(None)).count()
        songs_without_embeddings = total_songs - songs_with_embeddings
        
        print(f"✅ Database connection successful!")
        print(f"   - Total songs: {total_songs}")
        print(f"   - Songs with embeddings: {songs_with_embeddings}")
        print(f"   - Songs without embeddings: {songs_without_embeddings}")
        
        # Show sample songs
        sample_songs = db.query(Song).limit(3).all()
        print(f"\n📋 Sample songs:")
        for song in sample_songs:
            print(f"   - {song.track_name} by {song.artist_name}")
            print(f"     Full text preview: {song.full_text[:100]}...")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_configuration():
    """Test configuration settings"""
    print("\n⚙️  Testing configuration...")
    
    try:
        print(f"   - Database URL: {settings.DATABASE_URL[:50]}...")
        print(f"   - Embedding model: {settings.EMBEDDING_MODEL}")
        print(f"   - Embedding dimensions: {settings.EMBEDDING_DIMENSIONS}")
        
        # Check if OpenAI API key is set
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "sk-your-openai-api-key-here":
            print(f"   - OpenAI API key: ✅ Set (ending in ...{settings.OPENAI_API_KEY[-4:]})")
            return True
        else:
            print(f"   - OpenAI API key: ❌ Not set or using placeholder")
            print(f"     Please update your .env file with a valid OpenAI API key")
            return False
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def main():
    """Run all tests"""
    print("=== MusicSeeker System Test ===\n")
    
    # Test configuration
    config_ok = test_configuration()
    
    # Test database
    db_ok = test_database_connection()
    
    print(f"\n=== Test Results ===")
    print(f"Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"Database: {'✅ PASS' if db_ok else '❌ FAIL'}")
    
    if config_ok and db_ok:
        print(f"\n🚀 System is ready for embedding generation!")
        print(f"   Run: python scripts/generate_embeddings.py")
    else:
        print(f"\n⚠️  Please fix the issues above before proceeding")


if __name__ == "__main__":
    main()
