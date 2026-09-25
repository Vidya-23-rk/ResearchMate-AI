from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_evidence_success():
    mock_evidence = [
        {
            "page_number": 3,
            "section": "Introduction",
            "excerpt": (
                "Artificial intelligence is increasingly "
                "used in modern medicine."
            )
        }
    ]

    with patch(
        "app.routes.paper_routes."
        "evidence_service.get_evidence",
        return_value=mock_evidence
    ):

        response = client.get(
            "/papers/MOCK001/evidence"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["paper_id"] == "MOCK001"

    assert len(
        data["evidence"]
    ) == 1

    assert (
        data["evidence"][0]["page_number"]
        == 3
    )

    assert (
        data["evidence"][0]["section"]
        == "Introduction"
    )


def test_evidence_empty_result():

    with patch(
        "app.routes.paper_routes."
        "evidence_service.get_evidence",
        return_value=[]
    ):

        response = client.get(
            "/papers/MOCK001/evidence"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["paper_id"] == "MOCK001"

    assert data["evidence"] == []


def test_evidence_null_metadata():
    mock_evidence = [
        {
            "page_number": None,
            "section": None,
            "excerpt": (
                "This paper explores applications "
                "of artificial intelligence in medicine."
            )
        }
    ]

    with patch(
        "app.routes.paper_routes."
        "evidence_service.get_evidence",
        return_value=mock_evidence
    ):

        response = client.get(
            "/papers/MOCK001/evidence"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["evidence"][0]["page_number"] is None

    assert data["evidence"][0]["section"] is None

    assert data["evidence"][0]["excerpt"]


def test_evidence_invalid_paper_id():

    with patch(
        "app.routes.paper_routes."
        "evidence_service.get_evidence",
        side_effect=Exception("Paper not found")
    ):

        try:
            response = client.get(
                "/papers/INVALID/evidence"
            )
        except Exception as error:
            assert str(error) == "Paper not found"