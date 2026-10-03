from app.database.connection import Base, engine
from app.models.document import Document
from app.models.document_page import DocumentPage


def init_db():
    Base.metadata.create_all(bind=engine)