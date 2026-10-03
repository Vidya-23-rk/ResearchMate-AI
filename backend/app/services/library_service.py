from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.library import ResearchLibrary
from app.schemas.library import (
    LibraryCreateRequest,
    LibraryUpdateRequest
)


class LibraryService:

    @staticmethod
    def create_library_item(
        db: Session,
        request: LibraryCreateRequest
    ) -> ResearchLibrary:

        existing = (
            db.query(ResearchLibrary)
            .filter(
                ResearchLibrary.paper_id == request.paper_id
            )
            .first()
        )

        if existing:
            return existing

        item = ResearchLibrary(
            paper_id=request.paper_id,
            title=request.title,
            authors=",".join(request.authors),
            year=request.year,
            folder=request.folder,
            notes=request.notes,
            tags=",".join(request.tags),
            is_bookmarked=request.is_bookmarked,
            is_read=request.is_read
        )

        db.add(item)
        db.commit()
        db.refresh(item)

        return item

    @staticmethod
    def get_library_items(
        db: Session,
        search: Optional[str] = None,
        folder: Optional[str] = None,
        is_read: Optional[bool] = None,
        is_bookmarked: Optional[bool] = None
    ) -> List[ResearchLibrary]:

        query = db.query(ResearchLibrary)

        if search:
            search_pattern = f"%{search}%"

            query = query.filter(
                ResearchLibrary.title.ilike(
                    search_pattern
                )
            )

        if folder:
            query = query.filter(
                ResearchLibrary.folder == folder
            )

        if is_read is not None:
            query = query.filter(
                ResearchLibrary.is_read == is_read
            )

        if is_bookmarked is not None:
            query = query.filter(
                ResearchLibrary.is_bookmarked
                == is_bookmarked
            )

        return (
            query
            .order_by(
                ResearchLibrary.created_at.desc()
            )
            .all()
        )

    @staticmethod
    def get_library_item(
        db: Session,
        library_id: int
    ) -> Optional[ResearchLibrary]:

        return (
            db.query(ResearchLibrary)
            .filter(
                ResearchLibrary.library_id
                == library_id
            )
            .first()
        )

    @staticmethod
    def update_library_item(
        db: Session,
        library_id: int,
        request: LibraryUpdateRequest
    ) -> Optional[ResearchLibrary]:

        item = LibraryService.get_library_item(
            db,
            library_id
        )

        if not item:
            return None

        if request.folder is not None:
            item.folder = request.folder

        if request.notes is not None:
            item.notes = request.notes

        if request.tags is not None:
            item.tags = ",".join(request.tags)

        if request.is_bookmarked is not None:
            item.is_bookmarked = request.is_bookmarked

        if request.is_read is not None:
            item.is_read = request.is_read

        db.commit()
        db.refresh(item)

        return item

    @staticmethod
    def delete_library_item(
        db: Session,
        library_id: int
    ) -> bool:

        item = LibraryService.get_library_item(
            db,
            library_id
        )

        if not item:
            return False

        db.delete(item)
        db.commit()

        return True


library_service = LibraryService()