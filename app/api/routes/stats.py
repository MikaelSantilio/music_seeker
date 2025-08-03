"""
Statistics API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Dict

from app.db.database import get_db
from app.models.song import Song
from app.services.embedding_service import EmbeddingService
from app.api.schemas import StatsResponse

router = APIRouter()


@router.get("/stats", response_model=StatsResponse)
async def get_statistics(db: Session = Depends(get_db)):
    """
    Get comprehensive statistics about the music dataset
    
    Returns information about:
    - Total songs and artists
    - Embedding coverage
    - Top artists by song count
    - Year range of songs
    - Average lyrics length
    """
    try:
        # Basic counts
        total_songs = db.query(Song).count()
        total_artists = db.query(Song.artist_name).distinct().count()
        
        # Embedding statistics (simple version)
        songs_with_embeddings = db.query(Song).filter(Song.embedding.isnot(None)).count()
        embedding_coverage = round((songs_with_embeddings / total_songs * 100), 2) if total_songs > 0 else 0
        
        # Top artists
        top_artists_result = db.execute(text("""
            SELECT artist_name, COUNT(*) as song_count 
            FROM songs 
            GROUP BY artist_name 
            ORDER BY COUNT(*) DESC 
            LIMIT 10
        """))
        
        top_artists = [
            {
                "artist_name": row[0],
                "song_count": row[1]
            }
            for row in top_artists_result
        ]
        
        # Year statistics
        year_stats = db.execute(text("""
            SELECT 
                MIN(year) as min_year,
                MAX(year) as max_year,
                COUNT(DISTINCT year) as unique_years
            FROM songs 
            WHERE year IS NOT NULL
        """)).fetchone()
        
        year_range = {
            "min_year": year_stats[0] if year_stats[0] else None,
            "max_year": year_stats[1] if year_stats[1] else None,
            "unique_years": year_stats[2] if year_stats[2] else 0
        }
        
        # Average lyrics length
        avg_lyrics_length = db.execute(text("""
            SELECT AVG(LENGTH(lyrics)) as avg_length 
            FROM songs 
            WHERE lyrics IS NOT NULL AND lyrics != ''
        """)).fetchone()[0]
        
        return StatsResponse(
            total_songs=total_songs,
            total_artists=total_artists,
            songs_with_embeddings=songs_with_embeddings,
            embedding_coverage=embedding_coverage,
            top_artists=top_artists,
            year_range=year_range,
            average_lyrics_length=round(avg_lyrics_length, 2) if avg_lyrics_length else 0
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating statistics: {str(e)}")


@router.get("/stats/artists")
async def get_artist_statistics(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get detailed statistics for artists
    
    - **limit**: Maximum number of artists to return
    """
    try:
        result = db.execute(text("""
            SELECT 
                artist_name,
                COUNT(*) as song_count,
                MIN(year) as earliest_year,
                MAX(year) as latest_year,
                AVG(LENGTH(lyrics)) as avg_lyrics_length
            FROM songs 
            WHERE lyrics IS NOT NULL AND lyrics != ''
            GROUP BY artist_name 
            ORDER BY COUNT(*) DESC 
            LIMIT :limit
        """), {"limit": limit})
        
        artists = []
        for row in result:
            artists.append({
                "artist_name": row[0],
                "song_count": row[1],
                "earliest_year": row[2],
                "latest_year": row[3],
                "avg_lyrics_length": round(row[4], 2) if row[4] else 0
            })
        
        return {
            "artists": artists,
            "total_artists": len(artists)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting artist statistics: {str(e)}")


@router.get("/stats/years")
async def get_year_statistics(db: Session = Depends(get_db)):
    """
    Get statistics by year
    """
    try:
        result = db.execute(text("""
            SELECT 
                year,
                COUNT(*) as song_count,
                COUNT(DISTINCT artist_name) as artist_count
            FROM songs 
            WHERE year IS NOT NULL
            GROUP BY year 
            ORDER BY year DESC
        """))
        
        years = []
        for row in result:
            years.append({
                "year": row[0],
                "song_count": row[1],
                "artist_count": row[2]
            })
        
        return {
            "years": years,
            "total_years": len(years)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting year statistics: {str(e)}")


@router.get("/stats/embeddings")
async def get_embedding_statistics(db: Session = Depends(get_db)):
    """
    Get detailed embedding statistics
    """
    try:
        embedding_service = EmbeddingService()
        stats = embedding_service.get_embedding_statistics(db)
        
        # Additional embedding stats
        result = db.execute(text("""
            SELECT 
                COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as with_embeddings,
                COUNT(CASE WHEN embedding IS NULL THEN 1 END) as without_embeddings,
                COUNT(*) as total
            FROM songs
        """)).fetchone()
        
        return {
            **stats,
            "detailed_counts": {
                "with_embeddings": result[0],
                "without_embeddings": result[1],
                "total": result[2]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting embedding statistics: {str(e)}")
