from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_compare_papers():
    response = client.post(
        "/papers/compare",
        json={
            "paper_ids": [
                "MOCK001",
                "MOCK002"
            ]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert len(data["papers"]) == 2

    assert data["papers"][0]["paper_id"] == "MOCK001"
    assert data["papers"][1]["paper_id"] == "MOCK002"

    assert "title" in data["papers"][0]
    assert "authors" in data["papers"][0]
    assert "problem" in data["papers"][0]
    assert "methodology" in data["papers"][0]
    assert "dataset" in data["papers"][0]
    assert "results" in data["papers"][0]
    assert "limitations" in data["papers"][0]


def test_compare_papers_empty_list():
    response = client.post(
        "/papers/compare",
        json={
            "paper_ids": []
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is False
    assert data["papers"] == []


def test_compare_papers_csv():
    response = client.post(
        "/papers/compare/csv",
        json={
            "paper_ids": [
                "MOCK001",
                "MOCK002"
            ]
        }
    )

    assert response.status_code == 200

    assert response.headers["content-type"].startswith(
        "text/csv"
    )

    content = response.text

    assert "paper_id" in content
    assert "title" in content
    assert "authors" in content
    assert "year" in content
    assert "problem" in content
    assert "methodology" in content
    assert "dataset" in content
    assert "results" in content
    assert "limitations" in content

    assert "MOCK001" in content
    assert "MOCK002" in content


def test_compare_papers_csv_empty_list():
    response = client.post(
        "/papers/compare/csv",
        json={
            "paper_ids": []
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is False
    assert (
        data["message"]
        == "At least one paper ID is required."
    )