from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.document_page import DocumentPage
from app.models.document_chunk import DocumentChunk


class ChunkingService:

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str):
        """
        Split text into overlapping chunks while
        trying to preserve complete words.
        """

        text = text.strip()

        if not text:
            return []

        chunks = []

        start = 0
        text_length = len(text)

        while start < text_length:

            end = min(
                start + self.chunk_size,
                text_length
            )

            # Try to avoid cutting a word in half
            if end < text_length:
                last_space = text.rfind(" ", start, end)

                if last_space > start:
                    end = last_space

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= text_length:
                break

            start = end - self.chunk_overlap

        return chunks

    def create_chunks(
        self,
        document_id: str,
        db: Session
    ):
        """
        Create chunks from all extracted pages
        belonging to a document.
        """
# Remove existing chunks for this document
        db.query(DocumentChunk).filter(
              DocumentChunk.document_id == document_id
                ).delete()
        db.commit()
        pages = (
            db.query(DocumentPage)
            .filter(
                DocumentPage.document_id == document_id
            )
            .order_by(
                DocumentPage.page_number
            )
            .all()
        )

        if not pages:
            return []

        created_chunks = []

        for page in pages:

            page_chunks = self.chunk_text(
                page.text
            )

            for index, chunk_text in enumerate(page_chunks):

                chunk = DocumentChunk(
                    chunk_id=str(uuid4()),
                    document_id=document_id,
                    page_number=page.page_number,
                    chunk_index=index,
                    text=chunk_text
                )

                db.add(chunk)
                created_chunks.append(chunk)

        db.commit()

        return created_chunks


chunking_service = ChunkingService()