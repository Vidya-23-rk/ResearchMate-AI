from pathlib import Path
from uuid import uuid4

import fitz
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.models.document import Document
from app.services.exceptions import ResearchMateException
from app.services.pdf_extraction_service import pdf_extraction_service


class PDFService:

    async def upload_pdf(self, file: UploadFile, db: Session):

        # ---------------------------------------------------------
        # 1. Validate filename
        # ---------------------------------------------------------
        if not file.filename:
            raise ResearchMateException(
                "File name is missing.",
                status_code=400
            )

        # Only PDF files are allowed
        if Path(file.filename).suffix.lower() != ".pdf":
            raise ResearchMateException(
                "Invalid file type. Only PDF files are allowed.",
                status_code=400
            )

        # ---------------------------------------------------------
        # 2. Generate unique document ID
        # ---------------------------------------------------------
        document_id = str(uuid4())

        # ---------------------------------------------------------
        # 3. Read file in chunks
        # ---------------------------------------------------------
        max_size = settings.max_upload_size_mb * 1024 * 1024

        file_data = bytearray()

        while True:
            chunk = await file.read(1024 * 1024)

            if not chunk:
                break

            file_data.extend(chunk)

            if len(file_data) > max_size:
                raise ResearchMateException(
                    f"File is too large. Maximum allowed size is "
                    f"{settings.max_upload_size_mb} MB.",
                    status_code=400
                )

        # ---------------------------------------------------------
        # 4. Check empty file
        # ---------------------------------------------------------
        if not file_data:
            raise ResearchMateException(
                "Uploaded PDF is empty.",
                status_code=400
            )

        # ---------------------------------------------------------
        # 5. Validate PDF using PyMuPDF
        # ---------------------------------------------------------
        try:
            pdf = fitz.open(
                stream=bytes(file_data),
                filetype="pdf"
            )

            if pdf.needs_pass:
                pdf.close()

                raise ResearchMateException(
                    "Password-protected PDFs are not supported.",
                    status_code=400
                )

            page_count = len(pdf)

            pdf.close()

        except ResearchMateException:
            raise

        except Exception:
            raise ResearchMateException(
                "Invalid or corrupted PDF file.",
                status_code=400
            )

        # ---------------------------------------------------------
        # 6. Create upload directory
        # ---------------------------------------------------------
        upload_directory = Path(settings.upload_directory)

        upload_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        # ---------------------------------------------------------
        # 7. Secure storage filename
        # ---------------------------------------------------------
        stored_filename = f"{document_id}.pdf"

        file_path = upload_directory / stored_filename

        # ---------------------------------------------------------
        # 8. Save PDF
        # ---------------------------------------------------------
        try:
            file_path.write_bytes(bytes(file_data))

        except Exception:
            raise ResearchMateException(
                "Failed to store the uploaded PDF.",
                status_code=500
            )

        # ---------------------------------------------------------
        # 9. Save document metadata
        # ---------------------------------------------------------
        document = Document(
            document_id=document_id,
            file_name=file.filename,
            file_path=str(file_path),
            file_size=len(file_data),
            page_count=page_count,
            status="uploaded"
        )

        try:
            db.add(document)
            db.commit()
            db.refresh(document)

        except Exception:

            db.rollback()

            if file_path.exists():
                file_path.unlink()

            raise ResearchMateException(
                "Failed to save document information.",
                status_code=500
            )

        # ---------------------------------------------------------
        # 10. Extract PDF text page-by-page
        # ---------------------------------------------------------
        extraction_result = pdf_extraction_service.extract_pages(
            document=document,
            db=db
        )

        # ---------------------------------------------------------
        # 11. Return final result
        # ---------------------------------------------------------
        return {
            "success": True,
            "document_id": document.document_id,
            "file_name": document.file_name,
            "file_size": document.file_size,
            "page_count": document.page_count,
            "status": extraction_result["status"],
            "message": extraction_result["message"]
        }


pdf_service = PDFService()