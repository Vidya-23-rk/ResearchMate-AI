from typing import Any, Dict, List

import numpy as np

from app.services.embedding_service import embedding_service
from app.services.paper_details_service import (
    paper_details_service
)
from app.services.paper_search_service import (
    paper_search_service
)


class RecommendationService:

    def get_recommendations(
        self,
        paper_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:

        # --------------------------------------------------
        # 1. Get the selected paper
        # --------------------------------------------------

        paper = paper_details_service.get_paper_details(
            paper_id
        )

        title = paper.get("title") or ""
        abstract = paper.get("abstract") or ""

        source_text = f"{title}. {abstract}".strip()

        if not source_text:
            return []

        # --------------------------------------------------
        # 2. Generate embedding for selected paper
        # --------------------------------------------------

        source_embedding = (
            embedding_service.generate_embedding(
                source_text
            )
        )

        source_embedding = np.asarray(
            source_embedding,
            dtype="float32"
        )

        # --------------------------------------------------
        # 3. Search for candidate papers
        # --------------------------------------------------

        search_query = title

        search_results = paper_search_service.search_papers(
            query=search_query,
            limit=max(limit + 2, 5),
            offset=0
        )

        candidates = search_results.get(
            "papers",
            []
        )

        recommendations = []

        # --------------------------------------------------
        # 4. Compare each candidate
        # --------------------------------------------------

        for candidate in candidates:

            candidate_id = candidate.get(
                "paper_id"
            )

            # Don't recommend the same paper
            if candidate_id == paper_id:
                continue

            candidate_title = (
                candidate.get("title") or ""
            )

            candidate_abstract = (
                candidate.get("abstract") or ""
            )

            candidate_text = (
                f"{candidate_title}. "
                f"{candidate_abstract}"
            ).strip()

            if not candidate_text:
                continue

            candidate_embedding = (
                embedding_service.generate_embedding(
                    candidate_text
                )
            )

            candidate_embedding = np.asarray(
                candidate_embedding,
                dtype="float32"
            )

            # --------------------------------------------------
            # 5. Cosine similarity
            # --------------------------------------------------

            source_norm = np.linalg.norm(
                source_embedding
            )

            candidate_norm = np.linalg.norm(
                candidate_embedding
            )

            if (
                source_norm == 0
                or candidate_norm == 0
            ):
                continue

            similarity = float(
                np.dot(
                    source_embedding,
                    candidate_embedding
                )
                / (
                    source_norm
                    * candidate_norm
                )
            )

            recommendations.append({
                "paper_id": candidate_id,
                "title": candidate_title,
                "authors": candidate.get(
                    "authors",
                    []
                ),
                "abstract": candidate_abstract,
                "year": candidate.get(
                    "year"
                ),
                "url": candidate.get(
                    "url"
                ),
                "similarity_score": round(
                    similarity,
                    4
                )
            })

        # --------------------------------------------------
        # 6. Sort by semantic similarity
        # --------------------------------------------------

        recommendations.sort(
            key=lambda item: item[
                "similarity_score"
            ],
            reverse=True
        )

        return recommendations[:limit]


recommendation_service = RecommendationService()