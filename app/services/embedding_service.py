"""
Embedding service for generating and searching song embeddings using OpenAI API
"""

import requests
import json
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import settings
from app.models.song import Song


class EmbeddingService:
    """Service for handling embeddings generation and similarity search"""
    
    def __init__(self):
        """Initialize the embedding service"""
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.EMBEDDING_MODEL
        self.dimensions = settings.EMBEDDING_DIMENSIONS
        self.api_url = "https://api.openai.com/v1/embeddings"
        
        # Set up headers for API requests
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a search query
        
        Args:
            query: Search query text
            
        Returns:
            List of float values representing the embedding
        """
        try:
            payload = {
                "model": self.model,
                "input": query,
                "dimensions": self.dimensions
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            
            data = response.json()
            return data['data'][0]['embedding']
            
        except Exception as e:
            raise Exception(f"Failed to generate query embedding: {str(e)}")
    
    def search_similar_songs(
        self, 
        db: Session, 
        query_embedding: List[float], 
        limit: int = 10,
        threshold: float = 0.0
    ) -> List[Song]:
        """
        Search for songs similar to the query embedding using cosine similarity
        
        Args:
            db: Database session
            query_embedding: The query embedding vector
            limit: Maximum number of results to return
            threshold: Minimum similarity threshold (0-1)
            
        Returns:
            List of similar songs ordered by similarity score
        """
        try:
            # Convert embedding to PostgreSQL array format
            embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
            
            # SQL query using pgvector cosine similarity
            # Only apply threshold filter if threshold > 0
            if threshold > 0:
                sql_query = f"""
                    SELECT *, (1 - (embedding <=> '{embedding_str}'::vector)) as similarity_score
                    FROM songs 
                    WHERE embedding IS NOT NULL
                    AND (1 - (embedding <=> '{embedding_str}'::vector)) >= {threshold}
                    ORDER BY embedding <=> '{embedding_str}'::vector
                    LIMIT {limit}
                """
            else:
                sql_query = f"""
                    SELECT *, (1 - (embedding <=> '{embedding_str}'::vector)) as similarity_score
                    FROM songs 
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <=> '{embedding_str}'::vector
                    LIMIT {limit}
                """
            
            result = db.execute(text(sql_query))
            
            songs = []
            for row in result:
                song = Song(
                    id=row.id,
                    track_name=row.track_name,
                    artist_name=row.artist_name,
                    album=row.album,
                    year=row.year,
                    date=row.date,
                    lyrics=row.lyrics,
                    embedding=row.embedding,
                    created_at=row.created_at
                )
                # Add similarity score as an attribute
                song.similarity_score = row.similarity_score
                songs.append(song)
            
            return songs
            
        except Exception as e:
            raise Exception(f"Failed to search similar songs: {str(e)}")
    
    def semantic_search(
        self, 
        db: Session, 
        query: str, 
        limit: int = 10,
        threshold: float = 0.7
    ) -> List[Song]:
        """
        Perform semantic search for songs
        
        Args:
            db: Database session
            query: Search query text
            limit: Maximum number of results to return
            threshold: Minimum similarity threshold (0-1)
            
        Returns:
            List of similar songs with similarity scores
        """
        # Generate embedding for the query
        query_embedding = self.generate_query_embedding(query)
        
        # Search for similar songs
        return self.search_similar_songs(db, query_embedding, limit, threshold)
