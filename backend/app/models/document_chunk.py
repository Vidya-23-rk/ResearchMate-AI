from sqlalchemy import Column, ForeignKey, Integer, String, Text

from app.database.connection import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    chunk_id = Column(
        String,
        primary_key=True,
        index=True
    )

    document_id = Column(
        String,
        ForeignKey("documents.document_id"),
        nullable=False,
        index=True
    )

    page_number = Column(
        Integer,
        nullable=False,
        index=True
    )

    chunk_index = Column(
        Integer,
        nullable=False
    )

    text = Column(
        Text,
        nullable=False
    )
    