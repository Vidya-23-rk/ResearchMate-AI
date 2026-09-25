from typing import Any, Dict, List, Optional

import requests

from app.config import settings
from app.services.exceptions import ResearchMateException


SEMANTIC_SCHOLAR_SEARCH_URL = (
    "https://api.semanticscholar.org/graph/v1/paper/search"
)


class PaperSearchService:

    def __init__(self):

        self.headers = {
            "Accept": "application/json"
        }

        if settings.semantic_scholar_api_key:
            self.headers["x-api-key"] = (
                settings.semantic_scholar_api_key
            )

    def search_papers(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:

        query = query.strip()

        # -----------------------------------
        # 1. Validate query
        # -----------------------------------

        if not query:
            raise ResearchMateException(
                message="Search query cannot be empty.",
                status_code=400
            )

        # -----------------------------------
        # 2. MOCK MODE
        # -----------------------------------

        if settings.mock_semantic_scholar:
            return self.mock_search(
                query=query,
                limit=limit,
                offset=offset
            )

        # -----------------------------------
        # 3. REAL SEMANTIC SCHOLAR API
        # -----------------------------------

        params = {
            "query": query,
            "limit": limit,
            "offset": offset,
            "fields": (
                "paperId,title,authors,abstract,year,"
                "externalIds,url,citationCount"
            )
        }

        try:

            response = requests.get(
                SEMANTIC_SCHOLAR_SEARCH_URL,
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

        # Rate limit
        if response.status_code == 429:

            retry_after = response.headers.get(
                "Retry-After"
            )

            raise ResearchMateException(
                message="Academic API rate limit reached. Try again later.",
                status_code=429,
                details={
                    "retry_after": retry_after
                }
            )

        # Server error
        if response.status_code >= 500:

            raise ResearchMateException(
                message="Academic API is currently unavailable.",
                status_code=502
            )

        # Other errors
        if response.status_code != 200:

            raise ResearchMateException(
                message="Academic API returned an error.",
                status_code=502,
                details=response.text
            )

        # Parse JSON
        try:

            payload = response.json()

        except ValueError:

            raise ResearchMateException(
                message="Academic API returned invalid JSON.",
                status_code=502
            )

        if not isinstance(payload, dict):

            raise ResearchMateException(
                message="Unexpected academic API response format.",
                status_code=502
            )

        raw_papers = payload.get("data", [])

        if not isinstance(raw_papers, list):

            raise ResearchMateException(
                message="Invalid paper data received from academic API.",
                status_code=502
            )

        papers = [
            self.normalize_paper(paper)
            for paper in raw_papers
            if isinstance(paper, dict)
        ]

        return {
            "success": True,
            "query": query,
            "total": payload.get(
                "total",
                len(papers)
            ),
            "offset": payload.get(
                "offset",
                offset
            ),
            "next_offset": payload.get("next"),
            "papers": papers
        }

    # =========================================================
    # MOCK SEARCH
    # =========================================================

    @staticmethod
    def mock_search(
        query: str,
        limit: int,
        offset: int
    ) -> Dict[str, Any]:

        mock_papers = [

            {
                "paperId": "MOCK001",
                "title": f"Artificial Intelligence Applications in {query.title()}",
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
                    f"This is a mock research paper about "
                    f"{query}. It demonstrates how ResearchMate AI "
                    f"processes academic search results."
                ),
                "year": 2025,
                "externalIds": {
                    "DOI": "10.1000/mock001"
                },
                "url": "https://example.com/mock001",
                "citationCount": 42
            },

            {
                "paperId": "MOCK002",
                "title": f"Machine Learning Approaches for {query.title()}",
                "authors": [
                    {
                        "authorId": "A003",
                        "name": "David Brown"
                    }
                ],
                "abstract": (
                    f"This mock paper explores machine learning "
                    f"methods related to {query}."
                ),
                "year": 2024,
                "externalIds": {
                    "DOI": "10.1000/mock002"
                },
                "url": "https://example.com/mock002",
                "citationCount": 27
            },

            {
                "paperId": "MOCK003",
                "title": f"A Survey of Recent Research on {query.title()}",
                "authors": [
                    {
                        "authorId": "A004",
                        "name": "Sarah Wilson"
                    },
                    {
                        "authorId": "A005",
                        "name": "Michael Lee"
                    }
                ],
                "abstract": (
                    f"This survey reviews recent research trends "
                    f"and developments in {query}."
                ),
                "year": 2023,
                "externalIds": {
                    "DOI": "10.1000/mock003"
                },
                "url": "https://example.com/mock003",
                "citationCount": 18
            },

            {
                "paperId": "MOCK004",
                "title": f"Deep Learning and {query.title()}",
                "authors": [
                    {
                        "authorId": "A006",
                        "name": "Robert Davis"
                    }
                ],
                "abstract": (
                    f"This mock study investigates deep learning "
                    f"techniques applied to {query}."
                ),
                "year": 2022,
                "externalIds": {},
                "url": "https://example.com/mock004",
                "citationCount": 12
            },

            {
                "paperId": "MOCK005",
                "title": f"Future Directions in {query.title()} Research",
                "authors": [
                    {
                        "authorId": "A007",
                        "name": "Lisa Anderson"
                    }
                ],
                "abstract": (
                    f"This paper discusses possible future research "
                    f"directions related to {query}."
                ),
                "year": 2021,
                "externalIds": {
                    "DOI": "10.1000/mock005"
                },
                "url": "https://example.com/mock005",
                "citationCount": 8
            }
        ]

        # Apply pagination
        paginated_papers = mock_papers[
            offset: offset + limit
        ]

        next_offset = None

        if offset + limit < len(mock_papers):
            next_offset = offset + limit

        # Normalize exactly like real API results
        papers = [
            PaperSearchService.normalize_paper(paper)
            for paper in paginated_papers
        ]

        return {
            "success": True,
            "query": query,
            "total": len(mock_papers),
            "offset": offset,
            "next_offset": next_offset,
            "papers": papers
        }

    # =========================================================
    # NORMALIZE PAPER
    # =========================================================

    @staticmethod
    def normalize_paper(
        paper: Dict[str, Any]
    ) -> Dict[str, Any]:

        external_ids = paper.get(
            "externalIds"
        ) or {}

        if not isinstance(external_ids, dict):
            external_ids = {}

        raw_authors = paper.get(
            "authors"
        ) or []

        authors: List[
            Dict[str, Optional[str]]
        ] = []

        if isinstance(raw_authors, list):

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
            ) or "Untitled paper",

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

            "url": paper.get(
                "url"
            ),

            "citation_count": paper.get(
                "citationCount"
            )
        }


paper_search_service = PaperSearchService()