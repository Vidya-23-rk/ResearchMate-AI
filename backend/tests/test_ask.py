from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

DOCUMENT_ID = "7bc80a82-5dfb-47e5-a599-02491274e969"


def test_ask_document_success():
    response = client.post(
        f"/papers/documents/{DOCUMENT_ID}/ask",
        json={
            "question": "What is MLOPS?"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["document_id"] == DOCUMENT_ID
    assert data["question"] == "What is MLOPS?"
    assert data["answer"]
    assert isinstance(data["sources"], list)

    if data["sources"]:
        for source in data["sources"]:
            assert "page_number" in source
            assert "excerpt" in source
            assert "score" in source


def test_ask_document_not_found():
    fake_document_id = "00000000-0000-0000-0000-000000000000"

    response = client.post(
        f"/papers/documents/{fake_document_id}/ask",
        json={
            "question": "What is MLOPS?"
        }
    )

    assert response.status_code == 404

    data = response.json()

    assert data["success"] is False
    assert data["message"] == "Document not found."