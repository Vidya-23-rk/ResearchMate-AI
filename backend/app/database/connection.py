from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings


# SQLite requires this setting for FastAPI applications
connect_args = {
    "check_same_thread": False
}


# Create the database engine
engine = create_engine(
    settings.database_url,
    connect_args={
        "check_same_thread": False
    }
)


# Create database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base class for database models
Base = declarative_base()


# Database dependency for FastAPI routes
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()