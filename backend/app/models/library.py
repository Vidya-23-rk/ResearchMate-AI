from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
    Boolean
)

from app.database.connection import Base


class ResearchLibrary(Base):
    __tablename__ = "research_library"

    library_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    paper_id = Column(
        String,
        nullable=False,
        index=True
    )

    title = Column(
        String,
        nullable=False
    )

    authors = Column(
        Text,
        nullable=True
    )

    year = Column(
        Integer,
        nullable=True
    )

    folder = Column(
        String,
        nullable=True,
        default="General"
    )

    notes = Column(
        Text,
        nullable=True
    )

    tags = Column(
        Text,
        nullable=True
    )

    is_bookmarked = Column(
        Boolean,
        default=True,
        nullable=False
    )

    is_read = Column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )