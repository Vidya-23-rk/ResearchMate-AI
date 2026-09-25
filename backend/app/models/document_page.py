from sqlalchemy import Column, ForeignKey, Integer, String, Text

from app.database.connection import Base


class DocumentPage(Base):
    __tablename__ = "document_pages"

    id = Column(Integer, primary_key=True, autoincrement=True)

    document_id = Column(
        String,
        ForeignKey("documents.document_id"),
        nullable=False,
        index=True
    )

    page_number = Column(
        Integer,
        nullable=False
    )

    text = Column(
        Text,
        nullable=False
    )