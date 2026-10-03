from typing import List

from pydantic import BaseModel


class LibraryCreateRequest(BaseModel):
    paper_id: str
    title: str
    authors: List[str] = []
    year: int | None = None
    folder: str = "General"
    notes: str | None = None
    tags: List[str] = []
    is_bookmarked: bool = True
    is_read: bool = False


class LibraryUpdateRequest(BaseModel):
    folder: str | None = None
    notes: str | None = None
    tags: List[str] | None = None
    is_bookmarked: bool | None = None
    is_read: bool | None = None


class LibraryResponse(BaseModel):
    library_id: int
    paper_id: str
    title: str
    authors: List[str]
    year: int | None = None
    folder: str | None = None
    notes: str | None = None
    tags: List[str]
    is_bookmarked: bool
    is_read: bool


class LibraryListResponse(BaseModel):
    success: bool
    papers: List[LibraryResponse]