from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_library_item():
    response = client.post(
        "/library",
        json={
            "paper_id": "TEST_LIBRARY_001",
            "title": "Test Research Paper",
            "authors": [
                "Alice Smith",
                "Bob Jones"
            ],
            "year": 2025,
            "folder": "AI Research",
            "notes": "Important paper for testing.",
            "tags": [
                "AI",
                "Machine Learning"
            ],
            "is_bookmarked": True,
            "is_read": False
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["paper_id"] == "TEST_LIBRARY_001"
    assert data["title"] == "Test Research Paper"
    assert data["authors"] == [
        "Alice Smith",
        "Bob Jones"
    ]
    assert data["folder"] == "AI Research"
    assert data["tags"] == [
        "AI",
        "Machine Learning"
    ]
    assert data["is_bookmarked"] is True
    assert data["is_read"] is False


def test_get_library():
    response = client.get("/library")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert isinstance(data["papers"], list)


def test_search_library():
    response = client.get(
        "/library?search=Test Research Paper"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert any(
        paper["paper_id"] == "TEST_LIBRARY_001"
        for paper in data["papers"]
    )


def test_filter_library_by_folder():
    response = client.get(
        "/library?folder=AI Research"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert all(
        paper["folder"] == "AI Research"
        for paper in data["papers"]
    )


def test_filter_library_by_read_status():
    response = client.get(
        "/library?is_read=false"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert all(
        paper["is_read"] is False
        for paper in data["papers"]
    )


def test_filter_library_by_bookmark_status():
    response = client.get(
        "/library?is_bookmarked=true"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert all(
        paper["is_bookmarked"] is True
        for paper in data["papers"]
    )


def test_get_library_item():
    create_response = client.post(
        "/library",
        json={
            "paper_id": "TEST_LIBRARY_002",
            "title": "Second Test Paper",
            "authors": ["Test Author"],
            "year": 2024
        }
    )

    assert create_response.status_code == 200

    library_id = create_response.json()["library_id"]

    response = client.get(
        f"/library/{library_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["library_id"] == library_id
    assert data["paper_id"] == "TEST_LIBRARY_002"


def test_update_library_item():
    create_response = client.post(
        "/library",
        json={
            "paper_id": "TEST_LIBRARY_003",
            "title": "Update Test Paper",
            "authors": ["Test Author"]
        }
    )

    assert create_response.status_code == 200

    library_id = create_response.json()["library_id"]

    response = client.put(
        f"/library/{library_id}",
        json={
            "folder": "Updated Folder",
            "notes": "Updated notes.",
            "tags": [
                "Updated",
                "Research"
            ],
            "is_bookmarked": False,
            "is_read": True
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["folder"] == "Updated Folder"
    assert data["notes"] == "Updated notes."
    assert data["tags"] == [
        "Updated",
        "Research"
    ]
    assert data["is_bookmarked"] is False
    assert data["is_read"] is True


def test_delete_library_item():
    create_response = client.post(
        "/library",
        json={
            "paper_id": "TEST_LIBRARY_004",
            "title": "Delete Test Paper",
            "authors": ["Test Author"]
        }
    )

    assert create_response.status_code == 200

    library_id = create_response.json()["library_id"]

    response = client.delete(
        f"/library/{library_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True


def test_get_nonexistent_library_item():
    response = client.get(
        "/library/999999"
    )

    assert response.status_code == 404


def test_update_nonexistent_library_item():
    response = client.put(
        "/library/999999",
        json={
            "folder": "Test"
        }
    )

    assert response.status_code == 404


def test_delete_nonexistent_library_item():
    response = client.delete(
        "/library/999999"
    )

    assert response.status_code == 404