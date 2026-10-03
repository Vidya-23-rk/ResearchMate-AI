# ResearchMate AI Database Plan

## Database Technology

SQLite will be used during the development phase because it does not require
a separate database server or installation.

The project may migrate to PostgreSQL during production deployment.

## Planned Tables

### 1. Users

| Column | Description |
|---|---|
| id | Unique user ID |
| name | User's name |
| email | User's email |
| created_at | Account creation time |

### 2. Papers

| Column | Description |
|---|---|
| id | Internal paper ID |
| external_paper_id | ID from the academic API |
| title | Paper title |
| abstract | Paper abstract |
| publication_year | Publication year |
| doi | Digital Object Identifier |
| paper_url | Link to the paper |
| citation_count | Number of citations |
| created_at | Record creation time |

### 3. Documents

| Column | Description |
|---|---|
| id | Unique document ID |
| file_name | Uploaded file name |
| file_path | Location of the file |
| page_count | Number of pages |
| processing_status | Processing state |
| uploaded_at | Upload timestamp |

### 4. Document Chunks

| Column | Description |
|---|---|
| id | Unique chunk ID |
| document_id | Related document |
| chunk_text | Extracted text |
| page_number | Page containing the text |
| chunk_index | Position of the chunk |

### 5. Bookmarks

| Column | Description |
|---|---|
| id | Unique bookmark ID |
| user_id | Related user |
| paper_id | Related paper |
| created_at | Bookmark creation time |

### 6. Notes

| Column | Description |
|---|---|
| id | Unique note ID |
| user_id | Related user |
| paper_id | Related paper |
| note_text | User's research note |
| created_at | Note creation time |