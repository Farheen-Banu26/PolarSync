"""
PolarSync Platform - Database Engine and Session Management
"""
import logging
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

logger = logging.getLogger("polarsync.db")

Base = declarative_base()

# SQLAlchemy Engine
# Note: For SQLite fallback if postgres not configured, or postgresql via DATABASE_URL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    future=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """
    Dependency for database session yielding and cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> dict:
    """
    Health check utility to test PostgreSQL connectivity.
    Returns status dict without crashing the server if DB is unreachable.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "connected", "database": "postgresql"}
    except Exception as e:
        logger.warning(f"Database connection check warning: {e}")
        return {"status": "disconnected", "database": "postgresql", "detail": "PostgreSQL database offline or unreachable"}
