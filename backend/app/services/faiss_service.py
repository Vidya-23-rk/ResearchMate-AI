from pathlib import Path
import json

import faiss
import numpy as np
from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import embedding_service


class FAISSService:

    def __init__(self):
        self.index_directory = Path("faiss_index")
        self.index_directory.mkdir(
            parents=True,
            exist_ok=True
        )

    def build_index(
        self,
        document_id: str,
        db: Session
    ):
        """
        Build a FAISS index for all chunks
        belonging to one document.
        """

        chunks = (
            db.query(DocumentChunk)
            .filter(
                DocumentChunk.document_id == document_id
            )
            .order_by(
                DocumentChunk.page_number,
                DocumentChunk.chunk_index
            )
            .all()
        )

        if not chunks:
            return {
                "success": False,
                "message": "No chunks found for this document."
            }

        texts = [
            chunk.text
            for chunk in chunks
        ]

        embeddings = embedding_service.generate_embeddings(
            texts
        )

        embeddings = np.asarray(
            embeddings,
            dtype="float32"
        )

        # Normalize vectors so inner-product
        # similarity behaves like cosine similarity.
        faiss.normalize_L2(embeddings)

        dimension = embeddings.shape[1]

        index = faiss.IndexFlatIP(dimension)

        index.add(embeddings)

        index_path = (
            self.index_directory
            / f"{document_id}.index"
        )

        metadata_path = (
            self.index_directory
            / f"{document_id}.json"
        )

        faiss.write_index(
            index,
            str(index_path)
        )

        metadata = []

        for chunk in chunks:
            metadata.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    "text": chunk.text
                }
            )

        metadata_path.write_text(
            json.dumps(
                metadata,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

        return {
            "success": True,
            "document_id": document_id,
            "chunk_count": len(chunks),
            "vector_dimension": dimension,
            "index_path": str(index_path),
            "metadata_path": str(metadata_path)
        }


faiss_service = FAISSService()