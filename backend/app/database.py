"""
Database configuration and session management for APOGEE.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database file path
DATABASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATABASE_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(DATABASE_DIR, 'apogee.db')}"

# Create engine with connection pooling
# For SQLite, we use StaticPool to maintain a single connection
# For production with PostgreSQL/MySQL, use QueuePool with pool_size and max_overflow
from sqlalchemy.pool import StaticPool

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    poolclass=StaticPool,  # Single connection pool for SQLite
    pool_pre_ping=True,    # Verify connections before use
    echo=False             # Disable SQL logging for performance
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    """
    Database session dependency for FastAPI routes.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
