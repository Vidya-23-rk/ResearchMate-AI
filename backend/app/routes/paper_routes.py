
import csv
import io

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from app.schemas.paper import (
    PaperResponse,
    PaperSearchResponse,
    CitationResponse
)

from app.schemas.comparison import (
    PaperComparisonRequest,
    PaperComparisonResponse
)

from app.schemas.recommendation import (
    RecommendationResponse
)

from app.schemas.opportunity import (
    ResearchOpportunityResponse
)

from app.schemas.evidence import (
    EvidenceResponse
)

from app.services.paper_search_service import (
    paper_search_service
)

from app.services.paper_details_service import (
    paper_details_service
)

from app.services.citation_service import (
    citation_service
)

from app.services.comparison_service import (
    comparison_service
)

from app.services.recommendation_service import (
    recommendation_service
)

from app.services.opportunity_service import (
    opportunity_service
)

from app.services.evidence_service import (
    evidence_service
)


router = APIRouter(
    prefix="/papers",
    tags=["Papers"]
)


@router.get(
    "/search",
    response_model=PaperSearchResponse
)
def search_papers(
    query: str = Query(
        ...,
        min_length=1,
        description="Research topic or keywords"
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Number of results to return"
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Number of results to skip"
    )
):
    return paper_search_service.search_papers(
        query=query,
        limit=limit,
        offset=offset
    )


@router.get(
    "/{paper_id}/citation",
    response_model=CitationResponse
)
def generate_paper_citation(
    paper_id: str
):
    paper = paper_details_service.get_paper_details(
        paper_id
    )

    citations = citation_service.generate_citations(
        paper
    )

    return {
        "success": True,
        "paper_id": paper_id,
        "apa": citations["apa"],
        "ieee": citations["ieee"],
        "mla": citations["mla"]
    }


@router.post(
    "/compare",
    response_model=PaperComparisonResponse
)
def compare_papers(
    request: PaperComparisonRequest
):
    if not request.paper_ids:
        return {
            "success": False,
            "papers": []
        }

    papers = comparison_service.compare_papers(
        request.paper_ids
    )

    return {
        "success": True,
        "papers": papers
    }


@router.post(
    "/compare/csv"
)
def compare_papers_csv(
    request: PaperComparisonRequest
):
    if not request.paper_ids:
        return {
            "success": False,
            "message": "At least one paper ID is required."
        }

    papers = comparison_service.compare_papers(
        request.paper_ids
    )

    output = io.StringIO()

    writer = csv.DictWriter(
        output,
        fieldnames=[
            "paper_id",
            "title",
            "authors",
            "year",
            "problem",
            "methodology",
            "dataset",
            "results",
            "limitations"
        ]
    )

    writer.writeheader()

    for paper in papers:
        writer.writerow({
            "paper_id": paper.get(
                "paper_id",
                ""
            ),
            "title": paper.get(
                "title",
                ""
            ),
            "authors": ", ".join(
                paper.get(
                    "authors",
                    []
                )
            ),
            "year": paper.get(
                "year",
                ""
            ),
            "problem": paper.get(
                "problem",
                ""
            ),
            "methodology": paper.get(
                "methodology",
                ""
            ),
            "dataset": paper.get(
                "dataset",
                ""
            ),
            "results": paper.get(
                "results",
                ""
            ),
            "limitations": paper.get(
                "limitations",
                ""
            )
        })

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                "attachment; "
                "filename=literature_review_matrix.csv"
            )
        }
    )


@router.get(
    "/{paper_id}/recommendations",
    response_model=RecommendationResponse
)
def get_paper_recommendations(
    paper_id: str,
    limit: int = Query(
        5,
        ge=1,
        le=20,
        description="Number of related papers to return"
    )
):
    recommendations = (
        recommendation_service.get_recommendations(
            paper_id=paper_id,
            limit=limit
        )
    )

    return {
        "success": True,
        "source_paper_id": paper_id,
        "recommendations": [
            {
                "paper_id": paper.get(
                    "paper_id",
                    ""
                ),
                "title": paper.get(
                    "title",
                    "Untitled paper"
                ),
                "authors": [
                    author.get("name", "")
                    for author in paper.get(
                        "authors",
                        []
                    )
                    if author.get("name")
                ],
                "abstract": paper.get(
                    "abstract"
                ),
                "year": paper.get(
                    "year"
                ),
                "url": paper.get(
                    "url"
                ),
                "similarity_score": paper.get(
                    "similarity_score",
                    0.0
                )
            }
            for paper in recommendations
        ]
    }


@router.get(
    "/{paper_id}/opportunities",
    response_model=ResearchOpportunityResponse
)
def get_research_opportunities(
    paper_id: str
):
    opportunities = (
        opportunity_service.get_opportunities(
            paper_id=paper_id
        )
    )

    return {
        "success": True,
        "paper_id": paper_id,
        "opportunities": opportunities
    }


@router.get(
    "/{paper_id}/evidence",
    response_model=EvidenceResponse
)
def get_paper_evidence(
    paper_id: str
):
    evidence = evidence_service.get_evidence(
        paper_id=paper_id
    )

    return {
        "success": True,
        "paper_id": paper_id,
        "evidence": evidence
    }


@router.get(
    "/{paper_id}",
    response_model=PaperResponse
)
def get_paper_details(
    paper_id: str
):
    return paper_details_service.get_paper_details(
        paper_id
    )
