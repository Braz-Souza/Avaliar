"""
Database connection and session management for SQLModel
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Session

from app.core.config import settings

# Create database engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    echo=settings.DATABASE_ECHO
)

# Create session factory with SQLModel Session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)


def get_db() -> Session:
    """
    Dependency to get database session
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db_and_tables():
    """
    Create database tables based on SQLModel metadata
    """
    SQLModel.metadata.create_all(engine)


def get_db_session() -> Session:
    """
    Get a database session directly (for use outside of dependency injection)
    
    Returns:
        Session: Database session
    """
    return SessionLocal()