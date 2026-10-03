from typing import List

from pydantic import BaseModel


class OpportunityEvidence(BaseModel):
    page_number: int | None = None
    section: str | None = None
    excerpt: str


class ResearchOpportunity(BaseModel):
    category: str
    statement: str
    evidence: List[OpportunityEvidence] = []


class ResearchOpportunityResponse(BaseModel):
    success: bool
    paper_id: str
    opportunities: List[ResearchOpportunity]