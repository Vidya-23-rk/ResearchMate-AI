from typing import List, Optional

from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    success: bool
    document_id: str
    file_name: str
    file_size: int
    page_count: Optional[int] = None
    status: str
    message: str


class DocumentPageResponse(BaseModel):
    page_number: int
    text: str


class DocumentPagesResponse(BaseModel):
    success: bool
    document_id: str
    page_count: int
    pages: List[DocumentPageResponse]
    
class DocumentAskRequest(BaseModel):
    question: str


class DocumentSourceResponse(BaseModel):
    page_number: int
    excerpt: str
    score: float


class DocumentAskResponse(BaseModel):
    success: bool
    document_id: str
    question: str
    answer: str
    sources: List[DocumentSourceResponse]