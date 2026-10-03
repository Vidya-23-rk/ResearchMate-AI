# ResearchMate AI — Architecture and Design Document

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ResearchMate AI                          │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼────────────────────┐
          ▼                   ▼                    ▼
   ┌─────────────┐    ┌──────────────┐    ┌──────────────────┐
   │   Frontend  │    │   Backend    │    │   External APIs  │
   │ (React +    │◄──►│  (FastAPI)   │◄──►│ Semantic Scholar │
   │  Tailwind)  │    │  Port 8000   │    │ Google Gemini    │
   └─────────────┘    └──────┬───────┘    └──────────────────┘
                             │
          ┌──────────────────┼────────────────────┐
          ▼                  ▼                    ▼
   ┌─────────────┐    ┌────────────┐    ┌──────────────────┐
   │  SQLite /   │    │  Uploads   │    │   FAISS Index    │
   │ PostgreSQL  │    │  (PDFs)    │    │  (Vector Store)  │
   └─────────────┘    └────────────┘    └──────────────────┘
```

---

## 2. Backend Module Structure

```
backend/
├── app/
│   ├── main.py              ← FastAPI app, middleware, lifespan
│   ├── config.py            ← Pydantic Settings (reads .env)
│   ├── database/
│   │   ├── connection.py    ← SQLAlchemy engine, session factory
│   │   └── init_db.py       ← Create tables on startup
│   ├── models/              ← SQLAlchemy ORM models
│   │   ├── document.py
│   │   ├── document_page.py
│   │   ├── document_chunk.py
│   │   └── library.py
│   ├── schemas/             ← Pydantic request/response schemas
│   │   ├── paper.py
│   │   ├── document.py
│   │   ├── library.py
│   │   ├── comparison.py
│   │   ├── evidence.py
│   │   ├── opportunity.py
│   │   └── recommendation.py
│   ├── routes/              ← FastAPI routers
│   │   ├── paper_routes.py
│   │   ├── document_routes.py
│   │   └── library_routes.py
│   └── services/            ← Business logic
│       ├── paper_search_service.py
│       ├── paper_details_service.py
│       ├── pdf_service.py
│       ├── pdf_extraction_service.py
│       ├── chunking_service.py
│       ├── embedding_service.py
│       ├── faiss_service.py
│       ├── retrieval_service.py
│       ├── llm_service.py
│       ├── summarization_service.py
│       ├── citation_service.py
│       ├── comparison_service.py
│       ├── library_service.py
│       ├── recommendation_service.py
│       ├── opportunity_service.py
│       ├── evidence_service.py
│       ├── exceptions.py
│       └── error_handlers.py
├── tests/                   ← Pytest test suite
│   ├── conftest.py
│   ├── test_paper_search.py
│   ├── test_document_upload.py
│   ├── test_ask.py
│   ├── test_rag.py
│   ├── test_citation.py
│   ├── test_comparison.py
│   ├── test_library.py
│   ├── test_recommendation.py
│   ├── test_opportunity.py
│   └── test_evidence.py
├── Dockerfile
├── pytest.ini
└── requirements.txt
```

---

## 3. Database Schema

### Document

| Column       | Type    | Description                                  |
|-------------|---------|----------------------------------------------|
| document_id  | VARCHAR | UUID primary key                             |
| file_name    | VARCHAR | Original filename uploaded by user           |
| file_path    | VARCHAR | Stored path on server                        |
| file_size    | INTEGER | Size in bytes                                |
| page_count   | INTEGER | Number of pages                              |
| status       | VARCHAR | uploaded / processing / completed / failed / no_text |
| created_at   | DATETIME| Timestamp                                    |

### DocumentPage

| Column      | Type    | Description                    |
|------------|---------|--------------------------------|
| id          | INTEGER | Auto-increment primary key     |
| document_id | VARCHAR | FK → Document.document_id      |
| page_number | INTEGER | 1-indexed page number          |
| text        | TEXT    | Extracted plain text           |

### DocumentChunk

| Column      | Type    | Description                         |
|------------|---------|-------------------------------------|
| chunk_id    | VARCHAR | UUID primary key                    |
| document_id | VARCHAR | FK → Document.document_id           |
| page_number | INTEGER | Source page number                  |
| chunk_index | INTEGER | 0-indexed chunk position in page    |
| text        | TEXT    | Chunk text (≈1000 chars, 200 overlap)|

### ResearchLibrary

| Column        | Type    | Description                         |
|--------------|---------|-------------------------------------|
| library_id    | INTEGER | Auto-increment primary key          |
| paper_id      | VARCHAR | Semantic Scholar paper ID           |
| title         | TEXT    | Paper title                         |
| authors       | TEXT    | Comma-separated author names        |
| year          | INTEGER | Publication year                    |
| folder        | VARCHAR | User-defined folder name            |
| notes         | TEXT    | User notes                          |
| tags          | TEXT    | Comma-separated tags                |
| is_bookmarked | BOOLEAN | Bookmark flag                       |
| is_read       | BOOLEAN | Read status flag                    |
| created_at    | DATETIME| Timestamp                           |

---

## 4. API Contract

| Method | Endpoint                              | Phase | Description                        |
|--------|---------------------------------------|-------|------------------------------------|
| GET    | /health                               | 1     | Health check                       |
| GET    | /papers/search?query=...              | 2     | Search academic papers             |
| GET    | /papers/{paper_id}                    | 3     | Get paper details                  |
| POST   | /papers/upload                        | 3     | Upload and process PDF             |
| GET    | /papers/documents/{id}/pages          | 3     | Get extracted pages                |
| POST   | /papers/documents/{id}/ask            | 4     | RAG question answering             |
| POST   | /papers/documents/{id}/summarize      | 5     | Generate structured summary        |
| GET    | /papers/{id}/citation                 | 5     | Generate APA/IEEE/MLA citation     |
| POST   | /papers/compare                       | 6     | Compare multiple papers            |
| POST   | /papers/compare/csv                   | 6     | Export comparison as CSV           |
| POST   | /library                              | 7     | Save paper to library              |
| GET    | /library                              | 7     | Get library (with filters)         |
| GET    | /library/{id}                         | 7     | Get single library item            |
| PUT    | /library/{id}                         | 7     | Update library item                |
| DELETE | /library/{id}                         | 7     | Remove paper from library          |
| GET    | /papers/{id}/recommendations          | 7     | Get semantically similar papers    |
| GET    | /papers/{id}/opportunities            | 7     | Get research opportunity analysis  |
| GET    | /papers/{id}/evidence                 | 7     | Get evidence links for a paper     |

---

## 5. RAG Pipeline

```
User Question
     │
     ▼
┌──────────────────────────────┐
│     Embedding Service        │
│  (all-MiniLM-L6-v2)         │
│  → Question vector           │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       FAISS Index            │
│  cosine similarity search    │
│  → Top-K chunk vectors       │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│   Chunk Metadata Lookup      │
│  (page number, excerpt)      │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      LLM Service             │
│  Google Gemini 2.0           │
│  Prompt: evidence-grounded   │
│  answer only from context    │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│     Answer + Sources         │
│  (page refs + excerpts)      │
└──────────────────────────────┘
```

**Chunking settings:**
- Chunk size: 1000 characters
- Overlap: 200 characters
- Word boundaries preserved

**Retrieval settings:**
- Minimum similarity score: 0.45 (cosine)
- Top-K chunks: 5

---

## 6. AI Evaluation Report

### 6.1 Evaluation Methodology

A small evaluation set was created using academic PDF documents with known content. For each test case, the expected answer topic and source page were recorded before running the system.

### 6.2 Test Cases

| # | Question Type                    | Expected Behavior                              |
|---|----------------------------------|------------------------------------------------|
| 1 | Factual (present in document)    | Correct answer with page reference             |
| 2 | Factual (not in document)        | "Not found in document" response               |
| 3 | Ambiguous question               | Partial answer with appropriate uncertainty    |
| 4 | Out-of-scope question            | Clear statement that answer is not in document |

### 6.3 Observations

- **Source Accuracy:** Retrieved chunks consistently reference the correct page numbers.
- **Hallucination Control:** The LLM prompt explicitly forbids outside knowledge; the model respects this when evidence is absent.
- **Response Time:** Typical RAG query (embedding + FAISS search + LLM) completes in 3–7 seconds depending on document size and network latency.
- **Scanned PDFs:** Image-only PDFs return a `no_text` status. OCR is documented as a known limitation.

### 6.4 Known Limitations

1. **Scanned PDFs** — PyMuPDF cannot extract text from image-only PDFs. OCR support is planned.
2. **Very long abstracts** — Comparison and recommendation quality depends on abstract completeness.
3. **LLM rate limits** — Gemini API free tier has strict rate limits; production use requires a paid plan.
4. **Local embedding model startup** — `all-MiniLM-L6-v2` downloads on first run (~90 MB).

---

## 7. Security Checklist

| Check                                  | Status |
|----------------------------------------|--------|
| API keys stored in environment variables | ✅    |
| No secrets committed to Git             | ✅    |
| .env in .gitignore                      | ✅    |
| File type validated (PDF only)          | ✅    |
| File size validated (max 20 MB)         | ✅    |
| Password-protected PDFs rejected        | ✅    |
| Corrupted PDFs caught and rejected      | ✅    |
| Stack traces not exposed in responses   | ✅    |
| Input validated with Pydantic           | ✅    |
| Upload directory outside web root       | ✅    |
| CORS configured (restrict in production)| ✅    |
