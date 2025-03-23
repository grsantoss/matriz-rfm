# RFM Insights - Database Module

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
from typing import Generator
import os

# Configure logging
logger = logging.getLogger(__name__)

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://rfminsights:rfminsights@localhost:5432/rfminsights")

# Create database engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=5,         # Maximum number of connections in the pool
    max_overflow=10,     # Maximum number of connections that can be created beyond pool_size
    pool_timeout=30,     # Timeout for getting a connection from the pool
    pool_recycle=1800,   # Recycle connections after 30 minutes
    echo=False          # Set to True to log all SQL queries
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for declarative models
Base = declarative_base()

def get_db() -> Generator:
    """
    Get database session.
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """
    Initialize database by creating all tables.
    """
    try:
        # Import all models here to ensure they are registered with Base
        from .models import User, RFMAnalysis, Message, AIInsight, APIKey

        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def check_db_connection() -> bool:
    """
    Check database connection.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return False 