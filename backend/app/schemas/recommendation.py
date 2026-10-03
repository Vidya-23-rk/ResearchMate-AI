from typing import List

from pydantic import BaseModel


class RecommendedPaper(BaseModel):
    paper_id: str
    title: str
    authors: List[str]
    abstract: str | None = None
    year: int | None = None
    url: str | None = None
    similarity_score: float


class RecommendationResponse(BaseModel):
    success: bool
    source_paper_id: str
    recommendations: List[RecommendedPaper]