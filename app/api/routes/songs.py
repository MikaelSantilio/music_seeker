"""
Songs API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List, Optional
import math

from app.db.database import get_db
from app.models.song import Song
from app.api.schemas import SongResponse, PaginatedResponse

router = APIRouter()


@router.get("/songs", response_model=PaginatedResponse)
async def list_songs(
    page: int = Query(1, description="Page number", ge=1),
    per_page: int = Query(20, description="Items per page", ge=1, le=100),
    artist: Optional[str] = Query(None, description="Filter by artist name"),
    year: Optional[int] = Query(None, description="Filter by release year"),
    search: Optional[str] = Query(None, description="Search in song title or lyrics"),
    db: Session = Depends(get_db)
):
    """
    List songs with optional filtering and pagination
    
    - **page**: Page number (starts at 1)
    - **per_page**: Number of songs per page (max 100)
    - **artist**: Filter by artist name (partial match)
    - **year**: Filter by release year
    - **search**: Search in song title or lyrics (partial match)
    """
    try:
        # Build query
        query = db.query(Song)
        
        # Apply filters
        if artist:
            query = query.filter(Song.artist_name.ilike(f"%{artist}%"))
        
        if year:
            query = query.filter(Song.year == year)
            
        if search:
            query = query.filter(
                (Song.track_name.ilike(f"%{search}%")) |
                (Song.lyrics.ilike(f"%{search}%"))
            )
        
        # Get total count
        total = query.count()
        
        # Calculate pagination
        total_pages = math.ceil(total / per_page)
        offset = (page - 1) * per_page
        
        # Get paginated results
        songs = query.offset(offset).limit(per_page).all()
        
        return PaginatedResponse(
            items=[SongResponse.from_orm(song) for song in songs],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching songs: {str(e)}")


@router.get("/songs/{song_id}", response_model=SongResponse)
async def get_song(
    song_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific song by ID
    
    - **song_id**: The ID of the song to retrieve
    """
    try:
        song = db.query(Song).filter(Song.id == song_id).first()
        
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")
        
        return SongResponse.from_orm(song)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching song: {str(e)}")


@router.get("/artists", response_model=List[dict])
async def list_artists(
    limit: int = Query(50, description="Maximum number of artists", ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List all artists with song counts
    
    - **limit**: Maximum number of artists to return
    """
    try:
        # Use SQLAlchemy ORM instead of raw SQL
        result = db.execute(
            select(
                Song.artist_name,
                func.count().label('song_count')
            )
            .group_by(Song.artist_name)
            .order_by(func.count().desc())
            .limit(limit)
        )
        
        artists = [
            {
                "artist_name": row.artist_name,
                "song_count": row.song_count
            }
            for row in result
        ]
        
        return artists
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching artists: {str(e)}")


@router.get("/songs/by-artist/{artist_name}", response_model=List[SongResponse])
async def get_songs_by_artist(
    artist_name: str,
    limit: int = Query(20, description="Maximum number of songs", ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get songs by a specific artist
    
    - **artist_name**: Name of the artist
    - **limit**: Maximum number of songs to return
    """
    try:
        songs = db.query(Song).filter(
            Song.artist_name.ilike(f"%{artist_name}%")
        ).limit(limit).all()
        
        if not songs:
            raise HTTPException(status_code=404, detail=f"No songs found for artist: {artist_name}")
        
        return [SongResponse.from_orm(song) for song in songs]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching songs: {str(e)}")
