from pathlib import Path
import json

import faiss
import numpy as np

from app.services.embedding_service import embedding_service


class RetrievalService:

    def __init__(self):
        self.index_directory = Path("faiss_index")

    def retrieve(
        self,
        document_id: str,
        question: str,
        top_k: int = 5,
        min_score: float = 0.45
    ):
        if not question or not question.strip():
            return []

        index_path = self.index_directory / f"{document_id}.index"
        metadata_path = self.index_directory / f"{document_id}.json"

        if not index_path.exists():
            raise FileNotFoundError(
                "FAISS index not found for this document."
            )

        if not metadata_path.exists():
            raise FileNotFoundError(
                "FAISS metadata not found for this document."
            )

        index = faiss.read_index(str(index_path))

        metadata = json.loads(
            metadata_path.read_text(encoding="utf-8")
        )

        question_embedding = embedding_service.generate_embedding(
            question
        )

        question_embedding = np.asarray(
            [question_embedding],
            dtype="float32"
        )

        faiss.normalize_L2(question_embedding)

        actual_top_k = min(top_k, index.ntotal)

        scores, indices = index.search(
            question_embedding,
            actual_top_k
        )

        results = []

        for score, index_position in zip(
            scores[0],
            indices[0]
        ):
            if index_position < 0:
                continue

            score = float(score)

            # Ignore weak semantic matches
            if score < min_score:
                continue

            chunk = metadata[index_position]

            results.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "document_id": chunk["document_id"],
                    "page_number": chunk["page_number"],
                    "chunk_index": chunk["chunk_index"],
                    "text": chunk["text"],
                    "score": score
                }
            )

        return results


retrieval_service = RetrievalService()