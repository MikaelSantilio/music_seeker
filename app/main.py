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
app.include_router(search.router, prefix="/api/v1", tags=["🔍 Busca Semântica"])
app.include_router(songs.router, prefix="/api/v1", tags=["🎵 Músicas"])
app.include_router(stats.router, prefix="/api/v1", tags=["📊 Estatísticas"])


@app.get("/", tags=["🏠 Sistema"], summary="🏠 Página Inicial da API")
async def root():
    """
    ## 🏠 Bem-vindo ao MusicSeeker API!
    
    ### 🎵 O que é o MusicSeeker?
    
    Uma API de busca semântica de músicas que usa **inteligência artificial** para encontrar
    músicas baseada no **significado** e **sentimento** da sua consulta, não apenas palavras-chave!
    
    ### 🚀 Recursos Principais
    
    - **🔍 Busca Semântica**: Procure por "nostalgia" e encontre "Memories" do Maroon 5
    - **🤖 IA Integrada**: Powered by OpenAI text-embedding-3-small  
    - **⚡ Ultra Rápido**: Respostas em milissegundos
    - **🛡️ Seguro**: Rate limiting e validação robusta
    - **📊 Analytics**: Estatísticas detalhadas da biblioteca
    
    ### 📚 Dados Disponíveis
    
    - **5,949 músicas** com letras completas
    - **21 artistas** populares (Ed Sheeran, Taylor Swift, etc.)
    - **100% cobertura** de embeddings vetoriais
    
    ### 🔗 Links Úteis
    
    - **📖 Documentação Interativa**: [/docs](/docs) 
    - **📘 Documentação Alternativa**: [/redoc](/redoc)
    - **🔍 Fazer uma Busca**: [POST /api/v1/search](/docs#/🔍%20Busca%20Semântica/semantic_search_api_v1_search_post)
    - **📊 Ver Estatísticas**: [GET /api/v1/stats](/docs#/📊%20Estatísticas)
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
