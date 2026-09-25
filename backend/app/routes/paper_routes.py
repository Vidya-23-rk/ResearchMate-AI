from fastapi import APIRouter, Query

from app.schemas.paper import (
    PaperResponse,
    PaperSearchResponse,
    CitationResponse
)

from app.services.paper_search_service import paper_search_service
from app.services.paper_details_service import paper_details_service
from app.services.citation_service import citation_service


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