from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_opportunities_success():
    mock_opportunities = [
        {
            "category": "Limitation",
            "statement": (
                "The study uses a limited evaluation setting."
            ),
            "evidence": [
                {
                    "page_number": 3,
                    "section": "Evaluation",
                    "excerpt": (
                        "The paper describes evaluation "
                        "in a limited setting."
                    )
                }
            ]
        },
        {
            "category": "Research Direction",
            "statement": (
                "Future research could investigate "
                "broader evaluation."
            ),
            "evidence": [
                {
                    "page_number": None,
                    "section": None,
                    "excerpt": (
                        "The paper identifies limitations "
                        "in its evaluation."
                    )
                }
            ]
        }
    ]

    with patch(
        "app.routes.paper_routes."
        "opportunity_service.get_opportunities",
        return_value=mock_opportunities
    ):

        response = client.get(
            "/papers/MOCK001/opportunities"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["paper_id"] == "MOCK001"

    assert len(
        data["opportunities"]
    ) == 2

    assert (
        data["opportunities"][0]["category"]
        == "Limitation"
    )

    assert (
        data["opportunities"][0]["evidence"][0]["excerpt"]
        == "The paper describes evaluation in a limited setting."
    )

    assert (
        data["opportunities"][0]["evidence"][0]["page_number"]
        == 3
    )


def test_opportunities_empty_result():

    with patch(
        "app.routes.paper_routes."
        "opportunity_service.get_opportunities",
        return_value=[]
    ):

        response = client.get(
            "/papers/MOCK001/opportunities"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["paper_id"] == "MOCK001"

    assert data["opportunities"] == []


def test_opportunities_service_failure():

    with patch(
        "app.routes.paper_routes."
        "opportunity_service.get_opportunities",
        side_effect=Exception("Service failure")
    ):

        try:
            response = client.get(
                "/papers/MOCK001/opportunities"
            )
        except Exception as error:
            assert str(error) == "Service failure"