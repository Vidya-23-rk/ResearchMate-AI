from typing import Optional

from fastapi import APIRouter, Query

from app.schemas.paper import PaperSearchResponse
from app.services.paper_search_service import paper_search_service


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