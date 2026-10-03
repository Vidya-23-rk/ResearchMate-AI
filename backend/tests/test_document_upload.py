import io

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_fake_pdf():
    """
    Create a small valid PDF in memory using PyMuPDF.
    """
    import fitz

    pdf = fitz.open()

    page = pdf.new_page()
    page.insert_text(
        (72, 72),
        "ResearchMate AI PDF test document."
    )

    pdf_bytes = pdf.tobytes()
    pdf.close()

    return pdf_bytes


def test_upload_valid_pdf():
    pdf_bytes = create_fake_pdf()

    response = client.post(
        "/papers/upload",
        files={
            "file": (
                "test_paper.pdf",
                io.BytesIO(pdf_bytes),
                "application/pdf"
            )
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["file_name"] == "test_paper.pdf"
    assert data["page_count"] == 1
    assert data["status"] == "completed"
    assert data["document_id"]


def test_reject_non_pdf():
    response = client.post(
        "/papers/upload",
        files={
            "file": (
                "test_document.docx",
                io.BytesIO(b"This is not a PDF."),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        }
    )

    assert response.status_code == 400

    data = response.json()

    assert data["success"] is False
    assert "Only PDF files are allowed" in data["message"]


def test_get_document_pages():
    pdf_bytes = create_fake_pdf()

    upload_response = client.post(
        "/papers/upload",
        files={
            "file": (
                "pages_test.pdf",
                io.BytesIO(pdf_bytes),
                "application/pdf"
            )
        }
    )

    assert upload_response.status_code == 200

    document_id = upload_response.json()["document_id"]

    response = client.get(
        f"/papers/documents/{document_id}/pages"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["document_id"] == document_id
    assert data["page_count"] == 1
    assert len(data["pages"]) == 1
    assert data["pages"][0]["page_number"] == 1
    assert "ResearchMate AI" in data["pages"][0]["text"]


def test_document_not_found():
    response = client.get(
        "/papers/documents/INVALID_DOCUMENT_ID/pages"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["success"] is False
    assert data["message"] == "Document not found."