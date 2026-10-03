from typing import List
from pydantic import BaseModel


class PaperComparisonRequest(BaseModel):
    paper_ids: List[str]


class PaperComparisonItem(BaseModel):
    paper_id: str
    title: str
    authors: List[str]
    year: int | None = None
    dataset: str
    model: str
    metric: str
    limitation: str


class PaperComparisonResponse(BaseModel):
    success: bool
    papers: List[PaperComparisonItem]