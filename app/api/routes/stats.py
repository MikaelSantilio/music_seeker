"""
Statistics API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func, case
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
        
        # Top artists usando SQLAlchemy ORM - SEGURO
        top_artists_query = select(
            Song.artist_name,
            func.count().label('song_count')
        ).group_by(
            Song.artist_name
        ).order_by(
            func.count().desc()
        ).limit(10)
        
        top_artists_result = db.execute(top_artists_query)
        
        top_artists = [
            {
                "artist_name": row.artist_name,
                "song_count": row.song_count
            }
            for row in top_artists_result
        ]
        
        # Year statistics usando SQLAlchemy ORM - SEGURO
        year_stats_query = select(
            func.min(Song.year).label('min_year'),
            func.max(Song.year).label('max_year'),
            func.count(func.distinct(Song.year)).label('unique_years')
        ).where(Song.year.is_not(None))
        
        year_stats_result = db.execute(year_stats_query).first()
        
        year_range = {
            "min_year": year_stats_result.min_year if year_stats_result.min_year else None,
            "max_year": year_stats_result.max_year if year_stats_result.max_year else None,
            "unique_years": year_stats_result.unique_years if year_stats_result.unique_years else 0
        }
        
        # Average lyrics length usando SQLAlchemy ORM - SEGURO
        avg_length_query = select(
            func.avg(func.length(Song.lyrics)).label('avg_length')
        ).where(
            Song.lyrics.is_not(None),
            Song.lyrics != ''
        )
        
        avg_lyrics_result = db.execute(avg_length_query).first()
        avg_lyrics_length = float(avg_lyrics_result.avg_length) if avg_lyrics_result.avg_length else 0.0
        
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
        # Artist statistics usando SQLAlchemy ORM - SEGURO
        artist_stats_query = select(
            Song.artist_name,
            func.count().label('song_count'),
            func.min(Song.year).label('earliest_year'),
            func.max(Song.year).label('latest_year'),
            func.avg(func.length(Song.lyrics)).label('avg_lyrics_length')
        ).where(
            Song.lyrics.is_not(None),
            Song.lyrics != ''
        ).group_by(
            Song.artist_name
        ).order_by(
            func.count().desc()
        ).limit(limit)
        
        result = db.execute(artist_stats_query)
        
        artists = []
        for row in result:
            artists.append({
                "artist_name": row.artist_name,
                "song_count": row.song_count,
                "earliest_year": row.earliest_year,
                "latest_year": row.latest_year,
                "avg_lyrics_length": round(float(row.avg_lyrics_length), 2) if row.avg_lyrics_length else 0
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
        # Use SQLAlchemy ORM instead of raw SQL
        result = db.execute(
            select(
                Song.year,
                func.count().label('song_count'),
                func.count(func.distinct(Song.artist_name)).label('artist_count')
            )
            .where(Song.year.is_not(None))
            .group_by(Song.year)
            .order_by(Song.year.desc())
        )
        
        years = []
        for row in result:
            years.append({
                "year": row.year,
                "song_count": row.song_count,
                "artist_count": row.artist_count
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
        
        # Additional embedding stats using SQLAlchemy ORM
        result = db.execute(
            select(
                func.count(case((Song.embedding.is_not(None), 1))).label('with_embeddings'),
                func.count(case((Song.embedding.is_(None), 1))).label('without_embeddings'),
                func.count().label('total')
            )
        ).fetchone()
        
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
