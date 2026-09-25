from app.database.connection import Base, engine

from app.models.document import Document
from app.models.document_page import DocumentPage
from app.models.document_chunk import DocumentChunk
from app.models.library import ResearchLibrary


def init_db():
    Base.metadata.create_all(bind=engine)