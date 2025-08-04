"""
Configuration settings for MusicSeeker application
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings from environment variables"""
    
    # Database Configuration
    _database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+psycopg://musicseeker:musicseeker123@localhost:5432/musicseeker"
    )
    
    @property
    def DATABASE_URL(self) -> str:
        """
        Convert postgresql:// to postgresql+psycopg:// for compatibility
        Digital Ocean injects postgresql:// but we use psycopg (v3)
        """
        if self._database_url.startswith("postgresql://"):
            return self._database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return self._database_url
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    EMBEDDING_DIMENSIONS: int = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))  # Digital Ocean usa PORT
    
    # Application Settings
    APP_NAME: str = "MusicSeeker"
    APP_VERSION: str = os.getenv("APP_VERSION", "2.0.0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Production settings
    CORS_ORIGINS: list = [
        "https://musicseeker-api-*.ondigitalocean.app",
        "http://localhost:3000",
        "http://localhost:8000"
    ] if ENVIRONMENT == "production" else ["*"]
    
    def validate(self) -> None:
        """Validate required settings"""
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")


# Global settings instance
settings = Settings()
