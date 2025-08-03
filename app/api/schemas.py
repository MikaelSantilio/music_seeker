"""
Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class SongBase(BaseModel):
    """Base song schema"""
    track_name: str = Field(..., description="Song title")
    artist_name: str = Field(..., description="Artist name")
    album: Optional[str] = Field(None, description="Album name")
    year: Optional[int] = Field(None, description="Release year")
    date: Optional[str] = Field(None, description="Release date")


class SongCreate(SongBase):
    """Schema for creating a song"""
    lyrics: str = Field(..., description="Song lyrics")
    full_text: str = Field(..., description="Combined text for embedding")


class SongResponse(SongBase):
    """Schema for song responses"""
    id: int = Field(..., description="Song ID")
    lyrics: str = Field(..., description="Song lyrics")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        """Compatibility method for Pydantic v2"""
        return cls.model_validate(obj)


class SongSearchResult(BaseModel):
    """Schema for search results with similarity scores"""
    song: SongResponse
    similarity: float = Field(..., description="Similarity score (0-1)")


class SearchRequest(BaseModel):
    """Schema for search requests"""
    query: str = Field(..., description="Search query", min_length=1, max_length=500)
    limit: Optional[int] = Field(10, description="Maximum number of results", ge=1, le=50)
    similarity_threshold: Optional[float] = Field(0.5, description="Minimum similarity score", ge=0.0, le=1.0)


class SearchResponse(BaseModel):
    """Schema for search responses"""
    query: str = Field(..., description="Original search query")
    results: List[SongSearchResult] = Field(..., description="Search results")
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
