"""
Demo script showing how semantic search will work once embeddings are generated
"""

import os
import sys

# Add app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.database import SessionLocal
from app.models.song import Song


def demo_search_functionality():
    """
    Demonstrate how semantic search will work
    """
    print("=== MusicSeeker Semantic Search Demo ===\n")
    
    try:
        # Initialize database
        db = SessionLocal()
        
        # Get basic statistics
        total_songs = db.query(Song).count()
        songs_with_embeddings = db.query(Song).filter(Song.embedding.isnot(None)).count()
        songs_without_embeddings = total_songs - songs_with_embeddings
        
        print("📊 Current Status:")
        print(f"   - Total songs: {total_songs}")
        print(f"   - Songs with embeddings: {songs_with_embeddings}")
        print(f"   - Songs without embeddings: {songs_without_embeddings}")
        print(f"   - Embedding coverage: {(songs_with_embeddings/total_songs*100):.1f}%")
        
        if songs_with_embeddings == 0:
            print("\n⚠️  No embeddings found!")
            print("   To enable semantic search, first run:")
            print("   python scripts/generate_embeddings.py")
            
            # Show what queries would work
            print("\n🔍 Example queries that will work after embedding generation:")
            sample_queries = [
                "heartbreak and sadness",
                "dancing and party vibes",
                "love and romance", 
                "motivation and success",
                "friendship and loyalty"
            ]
            
            for query in sample_queries:
                print(f"   - '{query}'")
                
            # Show sample songs by artist
            print(f"\n👥 Available artists ({total_songs} songs):")
            
            # Use SQLAlchemy ORM instead of raw SQL
            from sqlalchemy import select, func
            result = db.execute(
                select(
                    Song.artist_name,
                    func.count().label('song_count')
                )
                .group_by(Song.artist_name)
                .order_by(func.count().desc())
                .limit(10)
            )
            
            for row in result:
                artist, count = row.artist_name, row.song_count
                print(f"   - {artist}: {count} songs")
                
            # Show sample songs
            print(f"\n🎵 Sample songs:")
            sample_songs = db.query(Song).limit(5).all()
            for song in sample_songs:
                print(f"   - '{song.track_name}' by {song.artist_name}")
                lyrics_preview = song.lyrics[:60].replace('\n', ' ')
                print(f"     Lyrics: {lyrics_preview}...")
        
        else:
            print("\n🎉 Embeddings are ready!")
            print("   Semantic search is available!")
            print("   You can now search for songs by meaning and concept.")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Demo error: {e}")


if __name__ == "__main__":
    demo_search_functionality()
