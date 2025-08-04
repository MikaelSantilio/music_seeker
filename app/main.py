"""
Main FastAPI application for MusicSeeker
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
import os

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.db.database import get_db, create_tables, test_database_connection
from app.api.routes import songs, search, stats
from app.middleware.security import SecurityMiddleware, add_process_time_header, limit_request_size
from app.utils.logging import setup_logging

# Setup logger
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for FastAPI application"""
    # Startup
    setup_logging()  # Initialize secure logging
    
    # Test database connection
    if not test_database_connection():
        logger.error("Failed to connect to database during startup")
        raise Exception("Database connection failed")
    
    # Try to create tables (will skip if they exist or handle permission errors)
    try:
        create_tables()
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Don't raise here - let the app continue if tables might exist
        
    yield
    # Shutdown (if needed)


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI application
app = FastAPI(
    title="🎵 MusicSeeker API",
    description="""
## 🎵 MusicSeeker - Semantic Music Search API

Busque músicas usando **inteligência artificial** e **similaridade semântica**!

### 🚀 Principais Funcionalidades

* **🔍 Busca Semântica**: Encontre músicas por significado, não apenas palavras-chave
* **🤖 IA Integrada**: Powered by OpenAI text-embedding-3-small
* **📊 Estatísticas**: Insights sobre sua biblioteca musical
* **🛡️ Seguro**: Rate limiting, validação de entrada e headers de segurança
* **⚡ Rápido**: Respostas em milissegundos com PostgreSQL + pgvector

### 💡 Exemplos de Busca

```
"nostalgia and lost love" → Encontra "Memories" do Maroon 5
"party vibes and celebration" → Encontra músicas animadas
"heartbreak and sadness" → Encontra baladas emotivas
"summer and freedom" → Encontra hits de verão
```

### 🛡️ Recursos de Segurança

* **Rate Limiting**: 10 requests por minuto por IP
* **Validação de Input**: Proteção contra SQL injection
* **CORS Seguro**: Origens específicas apenas
* **Headers de Segurança**: X-Frame-Options, CSP, XSS Protection

### 📈 Dados Disponíveis

* **5,949 músicas** com letras completas
* **21 artistas** populares
* **100% cobertura** de embeddings
* **Busca por similaridade** com scores de 0.0 a 1.0
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "MusicSeeker Team",
        "url": "https://github.com/musicseeker",
        "email": "contact@musicseeker.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.musicseeker.com",
            "description": "Production server"
        }
    ],
    tags_metadata=[
        {
            "name": "🔍 Busca Semântica",
            "description": "Endpoints para busca inteligente de músicas usando IA",
        },
        {
            "name": "🎵 Músicas", 
            "description": "CRUD operations para gerenciar músicas na base de dados",
        },
        {
            "name": "📊 Estatísticas",
            "description": "Informações e métricas sobre a biblioteca musical",
        },
        {
            "name": "🏠 Sistema",
            "description": "Endpoints de sistema e health checks",
        }
    ],
    lifespan=lifespan
)

# Set up rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware - CONFIGURAÇÃO DINÂMICA
cors_origins = settings.CORS_ORIGINS if settings.ENVIRONMENT == "production" else [
    "http://localhost:3000", 
    "http://localhost:8080", 
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Add security middleware
app.middleware("http")(limit_request_size)
app.middleware("http")(add_process_time_header)
app.add_middleware(SecurityMiddleware)

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    # Alternative path for Docker container
    static_dir = "/app/static"
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include API routes
app.include_router(search.router, prefix="/api/v1", tags=["🔍 Busca Semântica"])
app.include_router(songs.router, prefix="/api/v1", tags=["🎵 Músicas"])
app.include_router(stats.router, prefix="/api/v1", tags=["📊 Estatísticas"])


# Serve the web interface
@app.get("/search", tags=["🏠 Sistema"], summary="🔍 Interface de Busca Web")
async def search_interface():
    """Interface web para busca semântica de músicas"""
    # Try local development path first
    static_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "index.html")
    if not os.path.exists(static_file):
        # Try Docker container path
        static_file = "/app/static/index.html"
    
    if os.path.exists(static_file):
        return FileResponse(static_file)
    else:
        raise HTTPException(status_code=404, detail="Interface web não encontrada")


@app.get("/debug", tags=["🏠 Sistema"], summary="🐛 Interface de Debug")
async def debug_interface():
    """Interface de debug para testar a API"""
    # Try local development path first
    debug_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "debug.html")
    if not os.path.exists(debug_file):
        # Try Docker container path
        debug_file = "/app/static/debug.html"
    
    if os.path.exists(debug_file):
        return FileResponse(debug_file)
    else:
        raise HTTPException(status_code=404, detail="Interface de debug não encontrada")


@app.get("/", tags=["🏠 Sistema"], summary="🏠 Interface Web Principal")
async def root():
    """
    Interface web principal do MusicSeeker - busca semântica de músicas
    """
    # Try local development path first
    static_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "index.html")
    if not os.path.exists(static_file):
        # Try Docker container path
        static_file = "/app/static/index.html"
    
    if os.path.exists(static_file):
        return FileResponse(static_file)
    else:
        # Fallback to API info if static files not found
        return {
            "message": "Welcome to MusicSeeker API! 🎵",
            "description": "Semantic music search using OpenAI embeddings",
            "version": settings.APP_VERSION,
            "web_interface": "/search",
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
        # Test database connection using SQLAlchemy ORM
        from sqlalchemy import select, literal
        result = db.execute(select(literal(1)))
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
