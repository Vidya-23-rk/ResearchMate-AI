from typing import Any, Dict, List, Optional
import time
import requests
import concurrent.futures
from app.config import settings
from app.services.exceptions import ResearchMateException

OPENALEX_SEARCH_URL = "https://api.openalex.org/works"
SEMANTIC_SCHOLAR_SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"


class PaperSearchService:

    def __init__(self):
        self.s2_headers = {"Accept": "application/json"}
        if settings.semantic_scholar_api_key:
            self.s2_headers["x-api-key"] = settings.semantic_scholar_api_key

        self.oa_headers = {
            "Accept": "application/json",
            "User-Agent": "ResearchMateAI/1.0 (mailto:researchmate@example.com)"
        }

    # ------------------------------------------------------------------
    # PUBLIC: search_papers — Multi-source discovery + ranking
    # ------------------------------------------------------------------

    def search_papers(
        self,
        query: str,
        limit: int = 40,
        offset: int = 0
    ) -> Dict[str, Any]:
        query = query.strip()
        if not query:
            raise ResearchMateException(
                message="Search query cannot be empty.",
                status_code=400
            )

        if settings.mock_semantic_scholar:
            return self.mock_search(query=query, limit=limit, offset=offset)

        all_papers = []
        total_estimated = 0

        # Concurrent fetching from multiple sources
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_to_source = {
                executor.submit(self._search_openalex, query, limit, offset): "OpenAlex",
                executor.submit(self._search_semantic_scholar, query, limit, offset): "Semantic Scholar"
            }

            for future in concurrent.futures.as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    data = future.result()
                    all_papers.extend(data.get("papers", []))
                    if data.get("total", 0) > total_estimated:
                        total_estimated = data.get("total", 0)
                except Exception as exc:
                    print(f"[{source}] fetch generated an exception: {exc}")

        # Deduplicate results
        unique_papers = self._deduplicate_papers(all_papers)

        # Intelligent Ranking
        ranked_papers = self._rank_papers(unique_papers, query)

        # Truncate to limit
        final_papers = ranked_papers[:limit]

        return {
            "success": True,
            "query": query,
            "total": total_estimated,
            "offset": offset,
            "source": "Aggregated (OpenAlex, Semantic Scholar)",
            "next_offset": offset + limit if offset + limit < total_estimated else None,
            "papers": final_papers
        }

    # ------------------------------------------------------------------
    # DEDUPLICATION & RANKING
    # ------------------------------------------------------------------

    def _deduplicate_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen_dois = set()
        seen_titles = set()
        unique = []

        for p in papers:
            doi = p.get("doi")
            title = p.get("title", "").lower().strip()
            
            is_duplicate = False
            if doi and doi in seen_dois:
                is_duplicate = True
            elif title and title in seen_titles:
                is_duplicate = True
                
            if not is_duplicate:
                if doi:
                    seen_dois.add(doi)
                if title:
                    seen_titles.add(title)
                unique.append(p)
                
        return unique

    def _rank_papers(self, papers: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        query_terms = set(query.lower().split())
        current_year = 2026 # Contextually current

        for p in papers:
            title = p.get("title", "").lower()
            abstract = p.get("abstract", "")
            abstract_lower = abstract.lower() if abstract else ""
            year = p.get("year") or (current_year - 5)
            citations = p.get("citation_count") or 0

            # 1. Semantic Relevance (Heuristic word match for fast ranking)
            relevance_score = 0.0
            for term in query_terms:
                if term in title:
                    relevance_score += 0.4
                if term in abstract_lower:
                    relevance_score += 0.1
            relevance_score = min(relevance_score, 1.0) # Cap at 1.0

            # 2. Recency Score (Decay over 10 years)
            age = max(0, current_year - year)
            recency_score = max(0.0, 1.0 - (age * 0.1))

            # 3. Citation Score (Logarithmic scaling)
            import math
            citation_score = math.log10(citations + 1) / 4.0 # Cap around 10k citations = 1.0
            citation_score = min(citation_score, 1.0)

            # Composite Score (40% relevance, 30% recency, 30% citations)
            composite_score = (relevance_score * 0.4) + (recency_score * 0.3) + (citation_score * 0.3)
            
            p["semantic_relevance"] = round(relevance_score, 2)
            p["composite_score"] = round(composite_score, 3)

            # Assign Overall Evidence Category
            if citations > 100 and year >= (current_year - 5):
                p["overall_evidence"] = "High"
            elif year >= (current_year - 2) and citations > 10:
                p["overall_evidence"] = "Emerging"
            elif citations > 20:
                p["overall_evidence"] = "Medium"
            else:
                p["overall_evidence"] = "Low"

        # Sort descending by composite score
        papers.sort(key=lambda x: x["composite_score"], reverse=True)
        return papers

    # ------------------------------------------------------------------
    # PRIVATE: OpenAlex search
    # ------------------------------------------------------------------

    def _search_openalex(self, query: str, limit: int, offset: int) -> Dict[str, Any]:
        page = (offset // limit) + 1
        per_page = min(limit, 50)

        params = {
            "search": query,
            "per-page": per_page,
            "page": page,
            "select": (
                "id,title,authorships,abstract_inverted_index,"
                "publication_year,doi,primary_location,cited_by_count,open_access"
            ),
            "filter": "is_paratext:false",
            "sort": "cited_by_count:desc"
        }

        response = requests.get(
            OPENALEX_SEARCH_URL,
            params=params,
            headers=self.oa_headers,
            timeout=15
        )

        if response.status_code != 200:
            raise ResearchMateException(message="OpenAlex returned an error.", status_code=502)

        payload = response.json()
        raw_papers = payload.get("results", [])
        total = payload.get("meta", {}).get("count", 0)

        papers = [
            self._normalize_openalex_paper(p)
            for p in raw_papers
            if isinstance(p, dict)
        ]

        return {
            "success": True,
            "total": total,
            "papers": papers
        }

    # ------------------------------------------------------------------
    # PRIVATE: Semantic Scholar search
    # ------------------------------------------------------------------

    def _search_semantic_scholar(self, query: str, limit: int, offset: int) -> Dict[str, Any]:
        params = {
            "query": query,
            "limit": min(limit, 100),
            "offset": offset,
            "fields": "paperId,title,authors,abstract,year,externalIds,url,citationCount"
        }

        response = requests.get(
            SEMANTIC_SCHOLAR_SEARCH_URL,
            params=params,
            headers=self.s2_headers,
            timeout=20
        )

        if response.status_code != 200:
            raise ResearchMateException(message="Semantic Scholar returned an error.", status_code=502)

        payload = response.json()
        raw_papers = payload.get("data", [])
        total = payload.get("total", len(raw_papers))
        papers = [self.normalize_paper(p) for p in raw_papers if isinstance(p, dict)]

        return {
            "success": True,
            "total": total,
            "papers": papers
        }

    # ------------------------------------------------------------------
    # NORMALIZERS
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_openalex_paper(paper: Dict[str, Any]) -> Dict[str, Any]:
        abstract = None
        inverted = paper.get("abstract_inverted_index")
        if inverted and isinstance(inverted, dict):
            try:
                word_positions = []
                for word, positions in inverted.items():
                    for pos in positions:
                        word_positions.append((pos, word))
                word_positions.sort(key=lambda x: x[0])
                abstract = " ".join(w for _, w in word_positions)
            except Exception:
                abstract = None

        authors = []
        for authorship in paper.get("authorships", []):
            author = authorship.get("author", {})
            name = author.get("display_name", "")
            if name:
                authors.append({"author_id": author.get("id", ""), "name": name})

        doi = paper.get("doi")
        if doi and doi.startswith("https://doi.org/"):
            doi = doi.replace("https://doi.org/", "")

        primary_location = paper.get("primary_location") or {}
        landing_page_url = primary_location.get("landing_page_url")
        oa_url = (paper.get("open_access") or {}).get("oa_url")
        url = landing_page_url or oa_url or paper.get("id", "")

        openalex_id = paper.get("id", "")
        paper_id = openalex_id.split("/")[-1] if openalex_id else ""

        return {
            "paper_id": paper_id,
            "title": paper.get("title") or "Untitled Paper",
            "authors": authors,
            "abstract": abstract,
            "year": paper.get("publication_year"),
            "doi": doi,
            "url": url,
            "citation_count": paper.get("cited_by_count", 0)
        }

    @staticmethod
    def normalize_paper(paper: Dict[str, Any]) -> Dict[str, Any]:
        external_ids = paper.get("externalIds") or {}
        raw_authors = paper.get("authors") or []
        authors = []
        if isinstance(raw_authors, list):
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

    @staticmethod
    def mock_search(query: str, limit: int, offset: int) -> Dict[str, Any]:
        mock_papers = [
            {
                "paperId": f"MOCK{str(i).zfill(3)}",
                "title": f"Research on {query.title()} — Study {i}",
                "authors": [{"authorId": f"A{i}01", "name": f"Author {i}"}],
                "abstract": f"This mock paper #{i} explores topics related to {query}.",
                "year": 2026 - (i % 5),
                "externalIds": {"DOI": f"10.1000/mock{str(i).zfill(3)}"},
                "url": f"https://example.com/mock{str(i).zfill(3)}",
                "citationCount": max(0, 50 - i * 3)
            }
            for i in range(1, 41)
        ]

        paginated = mock_papers[offset: offset + limit]
        papers = [PaperSearchService.normalize_paper(p) for p in paginated]
        
        # Adding dummy evidence tags for mock
        for p in papers:
            p["overall_evidence"] = "High" if p["citation_count"] > 30 else "Emerging"
            p["semantic_relevance"] = 0.95

        return {
            "success": True,
            "query": query,
            "total": len(mock_papers),
            "offset": offset,
            "next_offset": offset + limit if offset + limit < len(mock_papers) else None,
            "papers": papers
        }


paper_search_service = PaperSearchService()