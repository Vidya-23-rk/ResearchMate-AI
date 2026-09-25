from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.document import Document
from app.models.document_page import DocumentPage
from app.schemas.document import (
    DocumentAskRequest,
    DocumentAskResponse,
    DocumentPagesResponse,
    DocumentUploadResponse
)
from app.services.exceptions import ResearchMateException
from app.services.pdf_service import pdf_service
from app.services.retrieval_service import retrieval_service
from app.services.llm_service import llm_service


router = APIRouter(
    prefix="/papers",
    tags=["Papers"]
)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse
)
async def upload_paper(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return await pdf_service.upload_pdf(
        file=file,
        db=db
    )


@router.get(
    "/documents/{document_id}/pages",
    response_model=DocumentPagesResponse
)
def get_document_pages(
    document_id: str,
    db: Session = Depends(get_db)
):
    # ---------------------------------------------------------
    # 1. Check whether document exists
    # ---------------------------------------------------------
    document = (
        db.query(Document)
        .filter(Document.document_id == document_id)
        .first()
    )

    if not document:
        raise ResearchMateException(
            "Document not found.",
            status_code=404
        )

    # ---------------------------------------------------------
    # 2. Get extracted pages
    # ---------------------------------------------------------
    pages = (
        db.query(DocumentPage)
        .filter(DocumentPage.document_id == document_id)
        .order_by(DocumentPage.page_number)
        .all()
    )

    # ---------------------------------------------------------
    # 3. Return pages
    # ---------------------------------------------------------
    return {
        "success": True,
        "document_id": document_id,
        "page_count": document.page_count or 0,
        "pages": [
            {
                "page_number": page.page_number,
                "text": page.text
            }
            for page in pages
        ]
    }
    
@router.post(
    "/documents/{document_id}/ask",
    response_model=DocumentAskResponse
)
def ask_document(
    document_id: str,
    request: DocumentAskRequest,
    db: Session = Depends(get_db)
):
    document = (
        db.query(Document)
        .filter(Document.document_id == document_id)
        .first()
    )

    if not document:
        raise ResearchMateException(
            "Document not found.",
            status_code=404
        )

    question = request.question.strip()

    if not question:
        raise ResearchMateException(
            "Question cannot be empty.",
            status_code=400
        )

    try:
        retrieved_chunks = retrieval_service.retrieve(
            document_id=document_id,
            question=question,
            top_k=5
        )

    except FileNotFoundError:
        raise ResearchMateException(
            "Search index is not available for this document.",
            status_code=404
        )

    llm_result = llm_service.generate_answer(
        question=question,
        retrieved_chunks=retrieved_chunks
    )

    return {
        "success": True,
        "document_id": document_id,
        "question": question,
        "answer": llm_result["answer"],
        "sources": llm_result["sources"]
    }