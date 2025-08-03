"""
SQLAlchemy models for MusicSeeker application
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.db.database import Base


class Song(Base):
    """
    Song model with lyrics and vector embeddings
    """
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    track_name = Column(String(255), nullable=False, index=True)
    artist_name = Column(String(255), nullable=False, index=True)
    album = Column(String(255), nullable=True)
    year = Column(Integer, nullable=True, index=True)
    date = Column(String(50), nullable=True)
    lyrics = Column(Text, nullable=False)
    full_text = Column(Text, nullable=False)  # Combined: track_name + artist_name + lyrics
    embedding = Column(Vector(1536), nullable=True)  # OpenAI text-embedding-3-small dimensions
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Song(id={self.id}, track='{self.track_name}', artist='{self.artist_name}')>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "track_name": self.track_name,
            "artist_name": self.artist_name,
            "album": self.album,
            "year": self.year,
            "date": self.date,
            "lyrics": self.lyrics,
            "full_text": self.full_text,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
