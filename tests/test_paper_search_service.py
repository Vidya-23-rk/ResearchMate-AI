from unittest.mock import Mock, patch

from app.services.paper_search_service import PaperSearchService
from app.services.exceptions import ResearchMateException


def test_empty_query_is_rejected():
    service = PaperSearchService()

    try:
        service.search_papers("   ")
        assert False, "Expected an exception"

    except ResearchMateException as error:
        assert error.status_code == 400


@patch("app.services.paper_search_service.requests.get")
def test_successful_search(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200

    mock_response.json.return_value = {
        "total": 1,
        "offset": 0,
        "next": None,
        "data": [
            {
                "paperId": "paper-123",
                "title": "Test Paper",
                "authors": [
                    {
                        "authorId": "author-1",
                        "name": "Test Author"
                    }
                ],
                "abstract": "Test abstract",
                "year": 2024,
                "externalIds": {
                    "DOI": "10.1234/test"
                },
                "url": "https://example.com/paper",
                "citationCount": 10
            }
        ]
    }

    mock_get.return_value = mock_response

    service = PaperSearchService()
    result = service.search_papers("artificial intelligence")

    assert result["success"] is True
    assert result["total"] == 1
    assert len(result["papers"]) == 1
    assert result["papers"][0]["paper_id"] == "paper-123"
    assert result["papers"][0]["citation_count"] == 10


@patch("app.services.paper_search_service.requests.get")
def test_rate_limit_error(mock_get):
    mock_response = Mock()
    mock_response.status_code = 429

    mock_get.return_value = mock_response

    service = PaperSearchService()

    try:
        service.search_papers("machine learning")
        assert False, "Expected a rate-limit exception"

    except ResearchMateException as error:
        assert error.status_code == 429