# ResearchMate AI

ResearchMate AI is an intelligent academic research assistant designed to support researchers and students in discovering, processing, understanding, and analyzing academic literature. The system integrates academic paper search, document processing, semantic retrieval, AI-powered question answering, research-paper summarization, and citation generation into a unified platform.

## Current Development Phase

**Phase 5 — Paper Summarization and Citation Generation**

The backend currently provides functionality for academic paper discovery, research document processing, semantic search, retrieval-augmented question answering, structured paper summarization, and citation generation.

## Implemented Features

* Academic paper search using the Semantic Scholar API
* Retrieval of detailed academic paper metadata
* PDF document upload and validation
* PDF text extraction and page-level storage
* Document chunking for efficient retrieval
* Semantic embedding generation using Sentence Transformers
* FAISS-based vector indexing and similarity search
* Retrieval-Augmented Generation (RAG) for document-based question answering
* Structured summarization of academic research papers
* Citation generation in APA, IEEE, and MLA formats
* Handling of incomplete bibliographic metadata without fabricating information
* Automated backend testing using Pytest

## Technology Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic Settings

### Artificial Intelligence and NLP

* Google Gemini API
* Sentence Transformers
* FAISS

### Document Processing

* PyMuPDF

### Testing

* Pytest

### Academic Data

* Semantic Scholar API

## System Architecture

```text
ResearchMate AI
│
├── Academic Paper Search
│   └── Semantic Scholar API
│
├── Document Processing
│   ├── PDF Upload
│   ├── PDF Validation
│   ├── Text Extraction
│   └── Document Chunking
│
├── Semantic Retrieval
│   ├── Sentence Transformer
│   ├── Embedding Generation
│   └── FAISS Vector Index
│
├── AI Research Assistant
│   ├── Document Question Answering
│   └── Research Paper Summarization
│
├── Citation Generation
│   ├── APA
│   ├── IEEE
│   └── MLA
│
└── Testing
    └── Pytest
```

## Development Progress

| Phase   | Description                                   | Status    |
| ------- | --------------------------------------------- | --------- |
| Phase 0 | Backend Foundation and Database Configuration | Completed |
| Phase 1 | Core Backend Infrastructure                   | Completed |
| Phase 2 | Academic Paper Search                         | Completed |
| Phase 3 | PDF Processing and Document Management        | Completed |
| Phase 4 | RAG and Document Question Answering           | Completed |
| Phase 5 | Paper Summarization and Citation Generation   | Completed |
| Phase 6 | Next Development Stage                        | Upcoming  |

## Testing

The backend currently includes automated tests covering:

* Academic paper search
* Search pagination and validation
* PDF upload and validation
* Document page retrieval
* Document retrieval
* Semantic retrieval
* Document question answering
* Citation generation
* Missing citation metadata handling

Current test result:

```text
15 passed
```

## Project Status

The backend implementation has successfully completed **Phase 5**. The current implementation provides the core research-assistance pipeline, from academic paper discovery and document processing to semantic retrieval, AI-based question answering, structured summarization, and citation generation.

Further development will focus on the remaining planned phases and integration of the backend services with the complete ResearchMate AI application.
