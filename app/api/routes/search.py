"""
Search API endpoints for semantic search
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import time

from app.db.database import get_db
from app.models.song import Song
from app.services.embedding_service import EmbeddingService
from app.api.schemas import SearchRequest, SearchResponse, SongSearchResult, SongResponse

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def semantic_search(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Perform semantic search on song lyrics using OpenAI embeddings
    
    - **query**: Search query (e.g., "love and heartbreak", "party vibes")
    - **limit**: Maximum number of results (1-50, default: 10)
    - **similarity_threshold**: Minimum similarity score (0.0-1.0, default: 0.5)
    
    Returns songs ranked by semantic similarity to your query.
    """
    start_time = time.time()
    
    try:
        # Check if we have any embeddings
        songs_with_embeddings = db.query(Song).filter(Song.embedding.isnot(None)).count()
        
        if songs_with_embeddings == 0:
            raise HTTPException(
                status_code=503,
                detail="Semantic search is not available. No embeddings found. Please run embedding generation first."
            )
        
        # Initialize embedding service
        embedding_service = EmbeddingService()
        
        # Generate query embedding
        try:
            query_embedding = embedding_service.generate_query_embedding(request.query)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate query embedding: {str(e)}"
            )
        
        # Search for similar songs
        results = embedding_service.search_similar_songs(
            db=db,
            query_embedding=query_embedding,
            limit=request.limit,
            threshold=request.similarity_threshold
        )
        
        # Convert results to response format
        search_results = [
            SongSearchResult(
                song=SongResponse.from_orm(song),
                similarity=song.similarity_score
            )
            for song in results
        ]
        
        processing_time = (time.time() - start_time) * 1000
        
        return SearchResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results),
            processing_time_ms=round(processing_time, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/search/suggestions")
async def get_search_suggestions():
    """
    Get example search queries that work well with semantic search
    """
    return {
        "suggestions": [
            {
                "category": "Emotions",
                "queries": [
                    "heartbreak and sadness",
                    "joy and happiness",
                    "anger and frustration",
                    "nostalgia and memories",
                    "hope and optimism"
                ]
            },
            {
                "category": "Themes",
                "queries": [
                    "love and romance",
                    "friendship and loyalty",
                    "success and ambition",
                    "freedom and independence",
                    "family and home"
                ]
            },
            {
                "category": "Moods",
                "queries": [
                    "party and dancing",
                    "chill and relaxing",
                    "motivation and energy",
                    "peaceful and calm",
                    "rebellious and edgy"
                ]
            },
            {
                "category": "Life Events",
                "queries": [
                    "breakup and moving on",
                    "celebration and victory",
                    "overcoming challenges",
                    "growing up and maturing",
                    "new beginnings"
                ]
            }
        ],
        "tips": [
            "Use descriptive phrases rather than single words",
            "Combine emotions with themes for better results",
            "Try different phrasings if you don't get good results",
            "Lower the similarity threshold to get more results"
        ]
    }


@router.get("/search/status")
async def get_search_status(db: Session = Depends(get_db)):
    """
    Get the current status of the search system
    """
    try:
        embedding_service = EmbeddingService()
        stats = embedding_service.get_embedding_statistics(db)
        
        return {
            "search_available": stats["songs_with_embeddings"] > 0,
            "total_songs": stats["total_songs"],
            "songs_with_embeddings": stats["songs_with_embeddings"], 
            "embedding_coverage": stats["embedding_coverage"],
            "embedding_model": stats["embedding_model"],
            "embedding_dimensions": stats["embedding_dimensions"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting search status: {str(e)}")
