from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.library import (
    LibraryCreateRequest,
    LibraryUpdateRequest,
    LibraryResponse,
    LibraryListResponse
)
from app.services.library_service import library_service


router = APIRouter(
    prefix="/library",
    tags=["Research Library"]
)


def convert_to_response(item):
    return LibraryResponse(
        library_id=item.library_id,
        paper_id=item.paper_id,
        title=item.title,
        authors=(
            item.authors.split(",")
            if item.authors
            else []
        ),
        year=item.year,
        folder=item.folder,
        notes=item.notes,
        tags=(
            item.tags.split(",")
            if item.tags
            else []
        ),
        is_bookmarked=item.is_bookmarked,
        is_read=item.is_read
    )


@router.post(
    "",
    response_model=LibraryResponse
)
def save_paper(
    request: LibraryCreateRequest,
    db: Session = Depends(get_db)
):
    item = library_service.create_library_item(
        db,
        request
    )

    return convert_to_response(item)


@router.get(
    "",
    response_model=LibraryListResponse
)
def get_library(
    search: Optional[str] = Query(
        None,
        description="Search papers by title"
    ),
    folder: Optional[str] = Query(
        None,
        description="Filter by folder"
    ),
    is_read: Optional[bool] = Query(
        None,
        description="Filter by read status"
    ),
    is_bookmarked: Optional[bool] = Query(
        None,
        description="Filter by bookmark status"
    ),
    db: Session = Depends(get_db)
):
    items = library_service.get_library_items(
        db=db,
        search=search,
        folder=folder,
        is_read=is_read,
        is_bookmarked=is_bookmarked
    )

    return {
        "success": True,
        "papers": [
            convert_to_response(item)
            for item in items
        ]
    }


@router.get(
    "/{library_id}",
    response_model=LibraryResponse
)
def get_library_item(
    library_id: int,
    db: Session = Depends(get_db)
):
    item = library_service.get_library_item(
        db,
        library_id
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Library item not found."
        )

    return convert_to_response(item)


@router.put(
    "/{library_id}",
    response_model=LibraryResponse
)
def update_library_item(
    library_id: int,
    request: LibraryUpdateRequest,
    db: Session = Depends(get_db)
):
    item = library_service.update_library_item(
        db,
        library_id,
        request
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Library item not found."
        )

    return convert_to_response(item)


@router.delete(
    "/{library_id}"
)
def delete_library_item(
    library_id: int,
    db: Session = Depends(get_db)
):
    deleted = library_service.delete_library_item(
        db,
        library_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Library item not found."
        )

    return {
        "success": True,
        "message": "Paper removed from research library."
    }