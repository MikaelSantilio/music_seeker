"""
Database configuration and connection management for MusicSeeker
"""

import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError, OperationalError
from app.config import settings

# Setup logger
logger = logging.getLogger(__name__)

# Database URL from settings
DATABASE_URL = settings.DATABASE_URL

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=settings.DEBUG)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_tables_exist():
    """
    Check if required tables already exist
    """
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        required_tables = ['songs']
        
        for table in required_tables:
            if table not in existing_tables:
                logger.info(f"Table '{table}' does not exist")
                return False
        
        logger.info("All required tables exist")
        return True
    except Exception as e:
        logger.warning(f"Error checking tables: {e}")
        return False


def create_tables():
    """
    Create all tables in the database with proper error handling
    """
    try:
        # First check if tables already exist
        if check_tables_exist():
            logger.info("Tables already exist, skipping creation")
            return True
            
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully")
        return True
        
    except ProgrammingError as e:
        if "permission denied" in str(e).lower():
            logger.warning("Permission denied creating tables - assuming they exist in managed database")
            # In managed databases, tables might already exist or be created externally
            return True
        else:
            logger.error(f"Database programming error: {e}")
            raise
            
    except OperationalError as e:
        logger.error(f"Database operational error: {e}")
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error creating tables: {e}")
        raise


def test_database_connection():
    """
    Test database connection and basic operations
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
