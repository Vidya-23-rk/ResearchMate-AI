# ResearchMate AI API Plan

## Basic Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | Check the API welcome message |
| GET | /health | Check backend status |

## Research Paper Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /papers/search | Search for academic papers |
| GET | /papers/{paper_id} | Get paper details |
| POST | /papers/compare | Compare multiple papers |

## Document Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /papers/upload | Upload a research paper |
| POST | /documents/{document_id}/ask | Ask questions about a paper |
| POST | /documents/{document_id}/summarize | Generate a paper summary |

## Citation Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /papers/{paper_id}/citation | Generate a citation |

## Library Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /library | View saved papers |
| POST | /papers/{paper_id}/bookmark | Bookmark a paper |

## Future Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /literature-matrix/generate | Generate a literature review matrix |

## Paper Search API

### Endpoint

GET `/papers/search`

### Query Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| query | string | Yes | Research topic or keywords |
| limit | integer | No | Number of results; default 10 |
| offset | integer | No | Number of results to skip |

### Example Request

`GET /papers/search?query=machine%20learning&limit=5`

### Response Format

```json
{
  "success": true,
  "query": "machine learning",
  "total": 100,
  "offset": 0,
  "next_offset": 5,
  "papers": [
    {
      "paper_id": "paper-id",
      "title": "Paper title",
      "authors": [
        {
          "author_id": "author-id",
          "name": "Author name"
        }
      ],
      "abstract": "Paper abstract",
      "year": 2024,
      "doi": "10.xxxx/example",
      "url": "https://example.com",
      "citation_count": 25
    }
  ]
}