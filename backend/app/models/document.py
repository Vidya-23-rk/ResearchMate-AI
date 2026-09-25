from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.database.connection import Base


class Document(Base):
    __tablename__ = "documents"

    document_id = Column(
        String,
        primary_key=True,
        index=True
    )

    file_name = Column(
        String,
        nullable=False
    )

    file_path = Column(
        String,
        nullable=False
    )

    file_size = Column(
        Integer,
        nullable=False
    )

    page_count = Column(
        Integer,
        nullable=True
    )

    status = Column(
        String,
        nullable=False,
        default="uploaded"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )