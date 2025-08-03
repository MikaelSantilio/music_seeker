"""
Embedding service for handling OpenAI embeddings in MusicSeeker
"""

from typing import List, Optional
from openai import OpenAI
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.config import settings
from app.models.song import Song


class EmbeddingService:
    """
    Service for managing embeddings using OpenAI API
    """
    
    def __init__(self):
        """Initialize the embedding service"""
        try:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.EMBEDDING_MODEL
            self.dimensions = settings.EMBEDDING_DIMENSIONS
        except Exception as e:
            # Handle OpenAI client initialization gracefully
            self.client = None
            self.model = settings.EMBEDDING_MODEL
            self.dimensions = settings.EMBEDDING_DIMENSIONS
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a search query
        
        Args:
            query: Search query text
            
        Returns:
            List of float values representing the embedding
        """
        response = self.client.embeddings.create(
            model=self.model,
            input=query,
            dimensions=self.dimensions
        )
        
        return response.data[0].embedding
    
    def search_similar_songs(
        self, 
        db: Session, 
        query_embedding: List[float], 
        limit: int = 10,
        similarity_threshold: float = 0.5
    ) -> List[dict]:
        """
        Search for songs similar to the query embedding using cosine similarity
        
        Args:
            db: Database session
            query_embedding: Query embedding vector
            limit: Maximum number of results to return
            similarity_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of songs with similarity scores
        """
        # Use pgvector's cosine similarity operator
        # Note: pgvector uses <=> for cosine distance (1 - cosine similarity)
        # So we calculate similarity as (1 - distance)
        
        results = db.query(
            Song,
            (1 - Song.embedding.cosine_distance(query_embedding)).label('similarity')
        ).filter(
            Song.embedding.isnot(None)
        ).filter(
            (1 - Song.embedding.cosine_distance(query_embedding)) >= similarity_threshold
        ).order_by(
            Song.embedding.cosine_distance(query_embedding)
        ).limit(limit).all()
        
        return [
            {
                "song": song.to_dict(),
                "similarity": float(similarity)
            }
            for song, similarity in results
        ]
    
    def get_embedding_statistics(self, db: Session) -> dict:
        """
        Get statistics about embeddings in the database
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with embedding statistics
        """
        total_songs = db.query(Song).count()
        songs_with_embeddings = db.query(Song).filter(Song.embedding.isnot(None)).count()
        songs_without_embeddings = total_songs - songs_with_embeddings
        
        return {
            "total_songs": total_songs,
            "songs_with_embeddings": songs_with_embeddings,
            "songs_without_embeddings": songs_without_embeddings,
            "embedding_coverage": round(songs_with_embeddings / total_songs * 100, 2) if total_songs > 0 else 0,
            "embedding_model": self.model,
            "embedding_dimensions": self.dimensions
        }
