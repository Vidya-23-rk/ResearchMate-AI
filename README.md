# ResearchMate AI

ResearchMate AI is an intelligent academic research assistant designed to support researchers and students in discovering, processing, understanding, and analyzing academic literature. The system integrates academic paper search, document processing, semantic retrieval, AI-powered question answering, research-paper summarization, and citation generation into a unified platform.

## Current Development Phase

**Phase 10 — Final Documentation, Presentation, and Resume**

The backend implementation is complete and provides functionality for academic paper discovery, research document processing, semantic search, retrieval-augmented question answering, structured paper summarization, citation generation, comparison, library management, semantic recommendations, and research opportunity extraction.

## Implemented Features (Backend)

* **Academic Paper Search:** Search papers using the Semantic Scholar API.
* **Paper Details:** Retrieval of detailed academic paper metadata.
* **PDF Document Management:** Upload, validation, and storage of PDF documents.
* **PDF Text Extraction:** Page-level text extraction using PyMuPDF.
* **Semantic Retrieval (RAG):**
  * Document chunking for efficient retrieval.
  * Semantic embedding generation using Sentence Transformers.
  * FAISS-based vector indexing and similarity search.
  * Retrieval-Augmented Generation for document-based question answering.
* **AI Analysis:**
  * Structured summarization of academic research papers.
  * Multi-paper comparison and literature review matrix extraction.
  * Semantic recommendations for related papers.
  * Research opportunity extraction (limitations, future work).
* **Citation Generation:** Citations in APA, IEEE, and MLA formats.
* **Research Library:** Bookmark, organize (folders, tags), and manage papers.
* **Automated Testing:** Comprehensive backend testing using Pytest.

## Technology Stack

### Backend
* Python 3.11+
* FastAPI
* SQLAlchemy & SQLite (PostgreSQL for production)
* Pydantic Settings

### Artificial Intelligence & NLP
* Google Gemini API (LLM)
* Sentence Transformers (Embeddings)
* FAISS (Vector Search)

### Document Processing
* PyMuPDF

### DevOps & Testing
* Pytest
* Docker & Docker Compose
* GitHub Actions (CI)

## System Architecture

See [docs/architecture.md](docs/architecture.md) for full details on the system architecture, database schema, API contract, RAG pipeline, and AI evaluation report.

## Setup Instructions

### Option 1: Docker (Recommended)

1. Clone the repository.
2. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```
3. Add your `SEMANTIC_SCHOLAR_API_KEY` and `LLM_API_KEY` (Google Gemini) to `.env`.
4. Run with Docker Compose:
   ```bash
   docker-compose up -d --build
   ```
5. The API will be available at `http://localhost:8000`. You can view the interactive documentation at `http://localhost:8000/docs`.

### Option 2: Local Setup (Clean Machine)

1. Ensure Python 3.11+ is installed.
2. Clone the repository and navigate to the `backend` folder.
3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Set up environment variables (copy `.env.example` to `.env` in the `backend` folder and add your API keys).
6. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `APP_ENV` | Environment (e.g., development, production) |
| `DATABASE_URL` | Database connection string |
| `SEMANTIC_SCHOLAR_API_KEY` | API key for Semantic Scholar |
| `LLM_API_KEY` | Google Gemini API key |
| `UPLOAD_DIRECTORY` | Directory to store uploaded PDFs |
| `MAX_UPLOAD_SIZE_MB` | Maximum allowed upload size |
| `MOCK_SEMANTIC_SCHOLAR` | Set to `true` to skip real API calls during testing |

## Testing

The backend includes a comprehensive automated test suite.
To run the tests:

```bash
cd backend
python -m pytest tests/ -v
```

Tests cover paper search, document upload, RAG answering, citation generation, summarization, paper comparison, library management, recommendations, and research opportunity extraction.

## Future Scope

* Implement OCR for scanned PDFs.
* Integrate frontend React application.
* Support additional academic APIs.
* Implement user authentication.

## Contributors

* **Member 1**: Backend APIs, database, academic API integration, PDF processing, AI pipeline, testing, and DevOps.
* **Member 2**: React interface, user experience, frontend integration, documentation, screenshots, and presentation.
