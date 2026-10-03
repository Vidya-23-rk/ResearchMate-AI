from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_recommendations_success():
    mock_recommendations = [
        {
            "paper_id": "MOCK002",
            "title": "Machine Learning Approaches for Medicine",
            "authors": [
                {
                    "author_id": "A003",
                    "name": "David Brown"
                }
            ],
            "abstract": (
                "This paper explores machine learning "
                "methods for medical applications."
            ),
            "year": 2024,
            "url": "https://example.com/mock002",
            "similarity_score": 0.8421
        }
    ]

    with patch(
        "app.routes.paper_routes."
        "recommendation_service.get_recommendations",
        return_value=mock_recommendations
    ):

        response = client.get(
            "/papers/MOCK001/recommendations"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["source_paper_id"] == "MOCK001"

    assert len(
        data["recommendations"]
    ) == 1

    assert (
        data["recommendations"][0]["paper_id"]
        == "MOCK002"
    )


def test_recommendations_limit():
    mock_recommendations = []

    with patch(
        "app.routes.paper_routes."
        "recommendation_service.get_recommendations",
        return_value=mock_recommendations
    ):

        response = client.get(
            "/papers/MOCK001/recommendations"
            "?limit=10"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True


def test_recommendations_invalid_limit():
    response = client.get(
        "/papers/MOCK001/recommendations"
        "?limit=0"
    )

    assert response.status_code == 422