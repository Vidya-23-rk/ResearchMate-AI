from typing import Any, Dict

import requests

from app.config import settings
from app.services.exceptions import ResearchMateException


SEMANTIC_SCHOLAR_PAPER_URL = (
    "https://api.semanticscholar.org/graph/v1/paper"
)


class PaperDetailsService:

    def __init__(self):

        self.headers = {
            "Accept": "application/json"
        }

        if settings.semantic_scholar_api_key:
            self.headers["x-api-key"] = (
                settings.semantic_scholar_api_key
            )

    def get_paper_details(
        self,
        paper_id: str
    ) -> Dict[str, Any]:

        paper_id = paper_id.strip()

        if not paper_id:

            raise ResearchMateException(
                message="Paper ID cannot be empty.",
                status_code=400
            )

        # -----------------------------------------
        # MOCK MODE
        # -----------------------------------------

        if settings.mock_semantic_scholar:

            return self.mock_paper_details(
                paper_id
            )

        # -----------------------------------------
        # REAL SEMANTIC SCHOLAR API
        # -----------------------------------------

        url = f"{SEMANTIC_SCHOLAR_PAPER_URL}/{paper_id}"

        params = {
            "fields": (
                "paperId,title,authors,abstract,year,"
                "externalIds,venue,url,citationCount"
            )
        }

        try:

            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=15
            )

        except requests.Timeout:

            raise ResearchMateException(
                message="Academic API request timed out.",
                status_code=504
            )

        except requests.RequestException:

            raise ResearchMateException(
                message="Unable to connect to the academic API.",
                status_code=502
            )

        # -----------------------------------------
        # ERROR HANDLING
        # -----------------------------------------

        if response.status_code == 404:

            raise ResearchMateException(
                message="Paper not found.",
                status_code=404
            )

        if response.status_code == 429:

            retry_after = response.headers.get(
                "Retry-After"
            )

            raise ResearchMateException(
                message=(
                    "Academic API rate limit reached. "
                    "Try again later."
                ),
                status_code=429,
                details={
                    "retry_after": retry_after
                }
            )

        if response.status_code >= 500:

            raise ResearchMateException(
                message="Academic API is currently unavailable.",
                status_code=502
            )

        if response.status_code != 200:

            raise ResearchMateException(
                message="Academic API returned an error.",
                status_code=502,
                details=response.text
            )

        try:

            paper = response.json()

        except ValueError:

            raise ResearchMateException(
                message="Academic API returned invalid JSON.",
                status_code=502
            )

        if not isinstance(paper, dict):

            raise ResearchMateException(
                message="Unexpected paper response format.",
                status_code=502
            )

        return self.normalize_paper_details(
            paper
        )

    # ==================================================
    # MOCK PAPER DETAILS
    # ==================================================

    @staticmethod
    def mock_paper_details(
        paper_id: str
    ) -> Dict[str, Any]:

        mock_papers = {

            "MOCK001": {
                "paperId": "MOCK001",
                "title": "Artificial Intelligence Applications in Medicine",
                "authors": [
                    {
                        "authorId": "A001",
                        "name": "John Smith"
                    },
                    {
                        "authorId": "A002",
                        "name": "Emily Johnson"
                    }
                ],
                "abstract": (
                    "This paper explores applications of "
                    "artificial intelligence in modern medicine."
                ),
                "year": 2025,
                "externalIds": {
                    "DOI": "10.1000/mock001"
                },
                "venue": "International Journal of AI Research",
                "url": "https://example.com/mock001",
                "citationCount": 42
            },

            "MOCK002": {
                "paperId": "MOCK002",
                "title": "Machine Learning Approaches for Medicine",
                "authors": [
                    {
                        "authorId": "A003",
                        "name": "David Brown"
                    }
                ],
                "abstract": (
                    "This paper explores machine learning "
                    "methods for medical applications."
                ),
                "year": 2024,
                "externalIds": {
                    "DOI": "10.1000/mock002"
                },
                "venue": "Journal of Machine Learning",
                "url": "https://example.com/mock002",
                "citationCount": 27
            }
        }

        if paper_id not in mock_papers:

            raise ResearchMateException(
                message="Paper not found.",
                status_code=404
            )

        return PaperDetailsService.normalize_paper_details(
            mock_papers[paper_id]
        )

    # ==================================================
    # NORMALIZE PAPER
    # ==================================================

    @staticmethod
    def normalize_paper_details(
        paper: Dict[str, Any]
    ) -> Dict[str, Any]:

        external_ids = (
            paper.get("externalIds") or {}
        )

        if not isinstance(
            external_ids,
            dict
        ):
            external_ids = {}

        raw_authors = (
            paper.get("authors") or []
        )

        authors = []

        if isinstance(
            raw_authors,
            list
        ):

            for author in raw_authors:

                if (
                    isinstance(author, dict)
                    and author.get("name")
                ):

                    authors.append({
                        "author_id": author.get(
                            "authorId"
                        ),
                        "name": author["name"]
                    })

        return {

            "paper_id": paper.get(
                "paperId",
                ""
            ),

            "title": paper.get(
                "title"
            ) or "Title not available",

            "authors": authors,

            "abstract": paper.get(
                "abstract"
            ),

            "year": paper.get(
                "year"
            ),

            "doi": external_ids.get(
                "DOI"
            ),

            "venue": paper.get(
                "venue"
            ),

            "url": paper.get(
                "url"
            ),

            "citation_count": paper.get(
                "citationCount"
            )
        }


paper_details_service = PaperDetailsService()