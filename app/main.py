"""
Main FastAPI application for MusicSeeker
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.db.database import get_db, create_tables
from app.api.routes import songs, search, stats
from app.middleware.security import SecurityMiddleware, add_process_time_header, limit_request_size
from app.utils.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for FastAPI application"""
    # Startup
    setup_logging()  # Initialize secure logging
    create_tables()
    yield
    # Shutdown (if needed)


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="🎵 Semantic music search API using OpenAI embeddings",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Set up rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware - CONFIGURAÇÃO MAIS SEGURA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # Específicos
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Apenas métodos necessários
    allow_headers=["*"],
)

# Add security middleware
app.middleware("http")(limit_request_size)
app.middleware("http")(add_process_time_header)
app.add_middleware(SecurityMiddleware)

# Include API routes
app.include_router(songs.router, prefix="/api/v1", tags=["Songs"])
app.include_router(search.router, prefix="/api/v1", tags=["Search"])
app.include_router(stats.router, prefix="/api/v1", tags=["Statistics"])


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "Welcome to MusicSeeker API! 🎵",
        "description": "Semantic music search using OpenAI embeddings",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "songs": "/api/v1/songs",
            "search": "/api/v1/search",
            "stats": "/api/v1/stats"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint
    """
    try:
        # Test database connection
        from sqlalchemy import text
        result = db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2025-08-03T18:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
