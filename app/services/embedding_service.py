"""
Embedding service for generating and searching song embeddings using OpenAI API
"""

import requests
import json
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

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
            # Usar SQLAlchemy ORM com pgvector - MUITO MAIS SEGURO
            from sqlalchemy import func
            
            # Query base com SQLAlchemy ORM
            query = select(
                Song,
                (1 - Song.embedding.cosine_distance(query_embedding)).label('similarity_score')
            ).where(
                Song.embedding.is_not(None)
            )
            
            # Aplicar filtro de threshold se necessário
            if threshold > 0:
                query = query.where(
                    (1 - Song.embedding.cosine_distance(query_embedding)) >= threshold
                )
            
            # Ordenar por similaridade e limitar resultados  
            # CORREÇÃO: Ordenar por similarity_score decrescente (maior = melhor match)
            from sqlalchemy import desc
            query = query.order_by(
                desc((1 - Song.embedding.cosine_distance(query_embedding)))
            ).limit(limit)
            
            # Executar query
            result = db.execute(query)
            
            songs = []
            for row in result:
                song = row.Song  # Acessar o objeto Song da tupla
                # Adicionar similarity score como atributo
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
