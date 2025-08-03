"""
Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
import re


class SongBase(BaseModel):
    """
    Base song schema with essential music metadata
    
    Contains the core information that identifies a song uniquely
    """
    track_name: str = Field(
        ..., 
        description="Nome da música",
        example="Shape of You"
    )
    artist_name: str = Field(
        ..., 
        description="Nome do artista ou banda",
        example="Ed Sheeran"
    )
    album: Optional[str] = Field(
        None, 
        description="Nome do álbum (opcional)",
        example="÷ (Divide)"
    )
    year: Optional[int] = Field(
        None, 
        description="Ano de lançamento",
        example=2017,
        ge=1900,
        le=2030
    )
    date: Optional[str] = Field(
        None, 
        description="Data de lançamento no formato YYYY-MM-DD",
        example="2017-01-06"
    )


class SongCreate(SongBase):
    """Schema for creating a new song entry"""
    lyrics: str = Field(
        ..., 
        description="Letra completa da música",
        example="The club isn't the best place to find a lover..."
    )
    full_text: str = Field(
        ..., 
        description="Texto combinado (título + artista + letra) usado para gerar embeddings"
    )


class SongResponse(SongBase):
    """
    Complete song information returned by the API
    
    Includes all metadata plus lyrics and system information
    """
    id: int = Field(
        ..., 
        description="ID único da música no sistema",
        example=1
    )
    lyrics: str = Field(
        ..., 
        description="Letra completa da música",
        example="The club isn't the best place to find a lover..."
    )
    created_at: Optional[datetime] = Field(
        None, 
        description="Timestamp de quando a música foi adicionada ao sistema"
    )
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "track_name": "Shape of You",
                "artist_name": "Ed Sheeran",
                "album": "÷ (Divide)",
                "year": 2017,
                "date": "2017-01-06",
                "lyrics": "The club isn't the best place to find a lover...",
                "created_at": "2024-08-03T10:30:00Z"
            }
        }
    
    @classmethod
    def from_orm(cls, obj):
        """Compatibility method for Pydantic v2"""
        return cls.model_validate(obj)


class SongSearchResult(BaseModel):
    """
    Individual search result with similarity score
    
    Represents one song found in a semantic search with its relevance score
    """
    song: SongResponse = Field(
        ...,
        description="Informações completas da música encontrada"
    )
    similarity: float = Field(
        ..., 
        description="Score de similaridade semântica (0.0 = não similar, 1.0 = idêntico)",
        example=0.85,
        ge=0.0,
        le=1.0
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "song": {
                    "id": 1,
                    "track_name": "Shape of You",
                    "artist_name": "Ed Sheeran",
                    "album": "÷ (Divide)",
                    "year": 2017,
                    "lyrics": "The club isn't the best place to find a lover...",
                },
                "similarity": 0.85
            }
        }


class SearchRequest(BaseModel):
    """
    Semantic search request parameters
    
    Use natural language to describe the mood, theme, or feeling you're looking for
    """
    query: str = Field(
        ..., 
        description="Consulta em linguagem natural descrevendo o que você procura",
        min_length=1, 
        max_length=100,
        example="nostalgia and lost love"
    )
    limit: Optional[int] = Field(
        10, 
        description="Número máximo de resultados (1-20)",
        ge=1, 
        le=20,
        example=10
    )
    similarity_threshold: Optional[float] = Field(
        0.0, 
        description="Score mínimo de similaridade para incluir nos resultados",
        ge=0.0, 
        le=1.0,
        example=0.3
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "nostalgia and lost love",
                "limit": 10,
                "similarity_threshold": 0.3
            }
        }
    
    @validator('query')
    def validate_query(cls, v):
        """Validate search query for security"""
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        
        # Remove potential SQL injection patterns
        dangerous_patterns = [';', '--', '/*', '*/', 'xp_', 'sp_', 'DROP', 'DELETE', 'INSERT', 'UPDATE']
        query_upper = v.upper()
        for pattern in dangerous_patterns:
            if pattern in query_upper:
                raise ValueError(f'Query contains forbidden pattern: {pattern}')
        
        # Allow only safe characters
        if not re.match(r'^[a-zA-Z0-9\s\-\'\".,!?()&]+$', v):
            raise ValueError('Query contains invalid characters')
            
        return v.strip()


class SearchResponse(BaseModel):
    """
    Complete search response with results and metadata
    
    Contains the search results plus helpful metadata about the search performance
    """
    query: str = Field(
        ..., 
        description="Consulta original que foi processada",
        example="nostalgia and lost love"
    )
    results: List[SongSearchResult] = Field(
        ..., 
        description="Lista de músicas encontradas ordenada por similaridade"
    )
    total_results: int = Field(..., description="Number of results found")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class StatsResponse(BaseModel):
    """Schema for statistics responses"""
    total_songs: int = Field(..., description="Total number of songs")
    total_artists: int = Field(..., description="Total number of artists")
    songs_with_embeddings: int = Field(..., description="Songs with embeddings")
    embedding_coverage: float = Field(..., description="Percentage of songs with embeddings")
    top_artists: List[dict] = Field(..., description="Top artists by song count")
    year_range: dict = Field(..., description="Year range of songs")
    average_lyrics_length: float = Field(..., description="Average lyrics length in characters")


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")


class PaginatedResponse(BaseModel):
    """Schema for paginated responses"""
    items: List[SongResponse] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
