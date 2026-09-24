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

        # Validate the search query
        query = query.strip()

        if not query:
            raise ResearchMateException(
                message="Search query cannot be empty.",
                status_code=400
            )

        # Prepare API parameters
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

        # Handle API response status codes
        if response.status_code == 429:
            raise ResearchMateException(
                message="Academic API rate limit reached. Try again later.",
                status_code=429
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
                details={
                    "provider_status": response.status_code
                }
            )

        # Parse the JSON response
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
            "total": payload.get("total", len(papers)),
            "offset": payload.get("offset", offset),
            "next_offset": payload.get("next"),
            "papers": papers
        }

    @staticmethod
    def normalize_paper(paper: Dict[str, Any]) -> Dict[str, Any]:
        external_ids = paper.get("externalIds") or {}

        raw_authors = paper.get("authors") or []

        authors: List[Dict[str, Optional[str]]] = []

        for author in raw_authors:
            if isinstance(author, dict) and author.get("name"):
                authors.append({
                    "author_id": author.get("authorId"),
                    "name": author["name"]
                })

        return {
            "paper_id": paper.get("paperId", ""),
            "title": paper.get("title") or "Untitled paper",
            "authors": authors,
            "abstract": paper.get("abstract"),
            "year": paper.get("year"),
            "doi": external_ids.get("DOI"),
            "url": paper.get("url"),
            "citation_count": paper.get("citationCount")
        }


paper_search_service = PaperSearchService()