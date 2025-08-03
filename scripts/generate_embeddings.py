"""
Embedding generation script for MusicSeeker

This script generates OpenAI embeddings for songs that don't have them yet,
using the text-embedding-3-small model and saves them to the database.
"""

import os
import sys
import time
from typing import List, Optional
from sqlalchemy.orm import Session
from openai import OpenAI

# Add app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.database import SessionLocal
from app.models.song import Song
from app.config import settings


class EmbeddingGenerator:
    """
    Handles embedding generation for songs using OpenAI API
    """
    
    def __init__(self):
        """Initialize the embedding generator"""
        # Validate OpenAI API key
        settings.validate()
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.EMBEDDING_MODEL
        self.dimensions = settings.EMBEDDING_DIMENSIONS
        
        print(f"Initialized EmbeddingGenerator with model: {self.model}")
        print(f"Embedding dimensions: {self.dimensions}")
    
    def get_songs_without_embeddings(self, db: Session, limit: Optional[int] = None) -> List[Song]:
        """
        Get songs that don't have embeddings yet
        
        Args:
            db: Database session
            limit: Maximum number of songs to retrieve
            
        Returns:
            List of songs without embeddings
        """
        query = db.query(Song).filter(Song.embedding.is_(None))
        
        if limit:
            query = query.limit(limit)
            
        return query.all()
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a given text using OpenAI API
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            List of float values representing the embedding
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
                dimensions=self.dimensions
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in a single API call
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List of embeddings
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts,
                dimensions=self.dimensions
            )
            
            return [data.embedding for data in response.data]
            
        except Exception as e:
            print(f"Error generating batch embeddings: {e}")
            raise
    
    def process_songs_batch(self, db: Session, songs: List[Song], batch_size: int = 50) -> int:
        """
        Process a batch of songs to generate embeddings
        
        Args:
            db: Database session
            songs: List of songs to process
            batch_size: Number of songs to process in each API call
            
        Returns:
            Number of songs processed successfully
        """
        total_processed = 0
        
        for i in range(0, len(songs), batch_size):
            batch = songs[i:i + batch_size]
            batch_texts = [song.full_text for song in batch]
            
            print(f"Processing batch {i//batch_size + 1}: {len(batch)} songs")
            
            try:
                # Generate embeddings for the batch
                embeddings = self.generate_embeddings_batch(batch_texts)
                
                # Update songs with embeddings
                for song, embedding in zip(batch, embeddings):
                    song.embedding = embedding
                
                # Commit the batch
                db.commit()
                total_processed += len(batch)
                
                print(f"✅ Successfully processed batch {i//batch_size + 1}")
                
                # Rate limiting - OpenAI has rate limits
                if i + batch_size < len(songs):
                    print("⏱️  Waiting 1 second to respect rate limits...")
                    time.sleep(1)
                
            except Exception as e:
                db.rollback()
                print(f"❌ Error processing batch {i//batch_size + 1}: {e}")
                
                # Try processing songs individually in this batch
                print("🔄 Attempting individual processing for failed batch...")
                for song in batch:
                    try:
                        embedding = self.generate_embedding(song.full_text)
                        song.embedding = embedding
                        db.commit()
                        total_processed += 1
                        print(f"✅ Individual processing successful for song ID {song.id}")
                        time.sleep(0.5)  # Extra delay for individual requests
                    except Exception as individual_error:
                        db.rollback()
                        print(f"❌ Failed individual processing for song ID {song.id}: {individual_error}")
                        continue
        
        return total_processed


def main():
    """
    Main function to execute the embedding generation pipeline
    """
    try:
        print("=== MusicSeeker Embedding Generation Pipeline ===\n")
        
        # Initialize generator
        generator = EmbeddingGenerator()
        
        # Get database session
        db: Session = SessionLocal()
        
        try:
            # Get total count of songs without embeddings
            total_songs_without_embeddings = db.query(Song).filter(Song.embedding.is_(None)).count()
            total_songs = db.query(Song).count()
            
            print(f"Total songs in database: {total_songs}")
            print(f"Songs without embeddings: {total_songs_without_embeddings}")
            
            if total_songs_without_embeddings == 0:
                print("✅ All songs already have embeddings!")
                return
            
            # Confirm before proceeding
            estimated_cost = total_songs_without_embeddings * 0.00002  # Rough estimate for text-embedding-3-small
            print(f"Estimated cost: ~${estimated_cost:.4f}")
            
            # Process in batches
            batch_size = 50  # Adjust based on rate limits
            processed_count = 0
            
            while True:
                # Get next batch of songs without embeddings
                songs_to_process = generator.get_songs_without_embeddings(db, limit=batch_size * 10)
                
                if not songs_to_process:
                    break
                
                print(f"\n🔄 Processing {len(songs_to_process)} songs...")
                
                # Process the batch
                batch_processed = generator.process_songs_batch(db, songs_to_process, batch_size)
                processed_count += batch_processed
                
                print(f"📊 Progress: {processed_count}/{total_songs_without_embeddings} songs processed")
                
                # Check if we're done
                remaining = db.query(Song).filter(Song.embedding.is_(None)).count()
                if remaining == 0:
                    break
            
            print(f"\n=== Embedding generation completed! ===")
            print(f"✅ Successfully processed {processed_count} songs")
            
            # Final statistics
            songs_with_embeddings = db.query(Song).filter(Song.embedding.isnot(None)).count()
            print(f"📊 Final statistics:")
            print(f"   - Total songs: {total_songs}")
            print(f"   - Songs with embeddings: {songs_with_embeddings}")
            print(f"   - Coverage: {songs_with_embeddings/total_songs*100:.1f}%")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error in embedding generation pipeline: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
