from typing import List, Optional

from pydantic import BaseModel, Field


class AuthorResponse(BaseModel):
    author_id: Optional[str] = None
    name: str


class PaperResponse(BaseModel):
    paper_id: str
    title: str
    authors: List[AuthorResponse] = Field(default_factory=list)
    abstract: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    venue: Optional[str] = None
    url: Optional[str] = None
    citation_count: Optional[int] = None

class PaperSearchResponse(BaseModel):
    success: bool
    query: str
    total: int
    offset: int
    next_offset: Optional[int] = None
    papers: List[PaperResponse]
    
class CitationResponse(BaseModel):
    success: bool
    paper_id: str
    apa: str
    ieee: str
    mla: str
    venue: Optional[str] = None