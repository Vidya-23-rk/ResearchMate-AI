from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


# --------------------------------------------------
# TEST 1 — Normal paper search
# --------------------------------------------------

def test_search_papers_success():

    response = client.get(
        "/papers/search",
        params={
            "query": "deep learning",
            "limit": 3,
            "offset": 0
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["query"] == "deep learning"
    assert data["total"] == 5
    assert len(data["papers"]) == 3


# --------------------------------------------------
# TEST 2 — Check paper fields
# --------------------------------------------------

def test_paper_response_fields():

    response = client.get(
        "/papers/search",
        params={
            "query": "medicine",
            "limit": 1,
            "offset": 0
        }
    )

    assert response.status_code == 200

    paper = response.json()["papers"][0]

    assert "paper_id" in paper
    assert "title" in paper
    assert "authors" in paper
    assert "abstract" in paper
    assert "year" in paper
    assert "doi" in paper
    assert "url" in paper
    assert "citation_count" in paper


# --------------------------------------------------
# TEST 3 — Pagination
# --------------------------------------------------

def test_search_pagination():

    response = client.get(
        "/papers/search",
        params={
            "query": "artificial intelligence",
            "limit": 2,
            "offset": 2
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["offset"] == 2
    assert len(data["papers"]) == 2


# --------------------------------------------------
# TEST 4 — Empty query
# --------------------------------------------------

def test_empty_query():

    response = client.get(
        "/papers/search",
        params={
            "query": ""
        }
    )

    assert response.status_code == 422


# --------------------------------------------------
# TEST 5 — Invalid limit
# --------------------------------------------------

def test_invalid_limit():

    response = client.get(
        "/papers/search",
        params={
            "query": "machine learning",
            "limit": 0
        }
    )

    assert response.status_code == 422