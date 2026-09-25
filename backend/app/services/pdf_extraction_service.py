from pathlib import Path

import fitz
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_page import DocumentPage
from app.services.exceptions import ResearchMateException
from app.services.chunking_service import chunking_service
from app.services.faiss_service import faiss_service


class PDFExtractionService:

    def extract_pages(
        self,
        document: Document,
        db: Session
    ):
        file_path = Path(document.file_path)

        # ---------------------------------------------------------
        # 1. Check whether stored PDF exists
        # ---------------------------------------------------------
        if not file_path.exists():
            document.status = "failed"
            db.commit()

            raise ResearchMateException(
                "Stored PDF file could not be found.",
                status_code=404
            )

        # ---------------------------------------------------------
        # 2. Mark document as processing
        # ---------------------------------------------------------
        document.status = "processing"
        db.commit()

        try:
            # -----------------------------------------------------
            # 3. Open PDF using PyMuPDF
            # -----------------------------------------------------
            pdf = fitz.open(file_path)

            # -----------------------------------------------------
            # 4. Reject password-protected PDF
            # -----------------------------------------------------
            if pdf.needs_pass:
                pdf.close()

                document.status = "failed"
                db.commit()

                raise ResearchMateException(
                    "Password-protected PDFs cannot be processed.",
                    status_code=400
                )

            # -----------------------------------------------------
            # 5. Extract every page
            # -----------------------------------------------------
            extracted_pages = []

            for page_index in range(len(pdf)):

                page = pdf.load_page(page_index)

                # PyMuPDF page numbers start from 0.
                # We store them starting from 1.
                page_number = page_index + 1

                text = page.get_text("text").strip()

                extracted_pages.append(
                    {
                        "page_number": page_number,
                        "text": text
                    }
                )

            pdf.close()

            # -----------------------------------------------------
            # 6. Check whether PDF contains extractable text
            # -----------------------------------------------------
            total_text = "".join(
                page["text"]
                for page in extracted_pages
            ).strip()

            if not total_text:
                document.status = "no_text"
                db.commit()

                return {
                    "success": True,
                    "document_id": document.document_id,
                    "status": "no_text",
                    "page_count": document.page_count,
                    "message": (
                        "PDF uploaded successfully, but no selectable "
                        "text was found. The PDF may be scanned or "
                        "image-only. OCR is required for text extraction."
                    )
                }

            # -----------------------------------------------------
            # 7. Store page-wise extracted text
            # -----------------------------------------------------
            for page_data in extracted_pages:

                document_page = DocumentPage(
                    document_id=document.document_id,
                    page_number=page_data["page_number"],
                    text=page_data["text"]
                )

                db.add(document_page)

            db.commit()

            # -----------------------------------------------------
            # 8. Create chunks from extracted pages
            # -----------------------------------------------------
            chunks = chunking_service.create_chunks(
                document_id=document.document_id,
                db=db
            )

            # -----------------------------------------------------
            # 9. Build FAISS index from chunks
            # -----------------------------------------------------
            faiss_result = faiss_service.build_index(
                document_id=document.document_id,
                db=db
            )

            if not faiss_result["success"]:
                document.status = "failed"
                db.commit()

                raise ResearchMateException(
                    "Failed to build document search index.",
                    status_code=500
                )

            # -----------------------------------------------------
            # 10. Mark processing as completed
            # -----------------------------------------------------
            document.status = "completed"
            db.commit()

            return {
                "success": True,
                "document_id": document.document_id,
                "status": "completed",
                "page_count": document.page_count,
                "chunk_count": len(chunks),
                "vector_dimension": faiss_result["vector_dimension"],
                "message": (
                    "PDF text extracted, chunked, embedded, "
                    "and indexed successfully."
                )
            }

        except ResearchMateException:
            raise

        except Exception:
            db.rollback()

            document.status = "failed"
            db.commit()

            raise ResearchMateException(
                "Failed to extract text from the PDF.",
                status_code=500
            )


pdf_extraction_service = PDFExtractionService()