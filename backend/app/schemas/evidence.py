from typing import List

from pydantic import BaseModel


class EvidenceItem(BaseModel):
    page_number: int | None = None
    section: str | None = None
    excerpt: str


class EvidenceResponse(BaseModel):
    success: bool
    paper_id: str
    evidence: List[EvidenceItem]