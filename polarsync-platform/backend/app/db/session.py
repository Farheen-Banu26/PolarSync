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

# SQLAlchemy Engine setup (Supports SQLite and PostgreSQL)
if settings.DATABASE_URL:
    try:
        is_sqlite = "sqlite" in settings.DATABASE_URL
        connect_args = {"check_same_thread": False} if is_sqlite else {}
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=not is_sqlite,
            future=True,
            connect_args=connect_args
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        # Auto-create tables for local persistent storage
        try:
            Base.metadata.create_all(bind=engine)
        except Exception as e:
            logger.warning(f"Failed to auto-create database tables: {e}")
    except Exception as e:
        logger.warning(f"Failed to initialize database engine for {settings.DATABASE_URL}: {e}")
        engine = None
        SessionLocal = None
else:
    engine = None
    SessionLocal = None


def get_db() -> Generator:
    """
    Dependency for database session yielding and cleanup.
    """
    if SessionLocal is None:
        yield None
        return

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> dict:
    """
    Health check utility to test database connectivity (SQLite or PostgreSQL).
    Returns status dict without crashing the server if DB is unreachable.
    """
    if not engine:
        return {
            "status": "unconfigured",
            "database": "none",
            "detail": "Simulation Mode (No DATABASE_URL configured; persistent DB storage is optional)"
        }

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_type = "sqlite" if "sqlite" in str(engine.url) else "postgresql"
        return {"status": "connected", "database": db_type}
    except Exception as e:
        logger.debug(f"Database connection check warning: {e}")
        return {"status": "disconnected", "database": "postgresql", "detail": f"Database offline or unreachable: {str(e)}"}
