from typing import List
from pydantic import BaseModel


class GapDetectionRequest(BaseModel):
    paper_ids: List[str]


class GapDetectionResponse(BaseModel):
    success: bool
    opportunities: List[str]
