from app.database.connection import Base, engine
from app.models.document import Document
from app.models.document_page import DocumentPage
from app.models.document_chunk import DocumentChunk

# Import models so SQLAlchemy registers them
from app.models.document import Document


def init_db():
    Base.metadata.create_all(bind=engine)