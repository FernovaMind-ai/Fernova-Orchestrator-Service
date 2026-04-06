# Fernova Orchestrator Service - API & Payload Documentation

## Overview

The **Fernova Orchestrator Service** is the central service that coordinates between:
- **Vector Embeddings Service** - Text embedding and chunking
- **Search Service** - Document indexing and retrieval  
- **LLM Service** - Query generation and responses
- **OCR Service** - Document extraction

**Base URL**: `http://localhost:8001`  
**API Prefix**: `/api/v1/orchestrator`

---

## Table of Contents

1. [Search & Query Endpoints](#search--query-endpoints)
2. [Document Processing Endpoints](#document-processing-endpoints)
3. [Embedding Endpoints](#embedding-endpoints)
4. [Health & Diagnostics](#health--diagnostics)
5. [Request Models](#request-models)
6. [Response Models](#response-models)
7. [Error Handling](#error-handling)

---

## Search & Query Endpoints

### 1. POST `/api/v1/orchestrator/search-and-query`

**Description**: Perform semantic search on indexed documents and query LLM with results

**Request Body**:
```json
{
  "query": "explain what is fingerprint reconstruction",
  "llm_provider": "gemini",
  "llm_model": "gemini-2.5-flash",
  "api_key": "your-api-key",
  "temperature": 0.7,
  "max_tokens": null,
  "search_type": "semantic",
  "top": 10,
  "embedding_method": "ensemble",
  "response_type": "analysis"
}
```

**Request Parameters**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| query | string | ✅ | - | The search query string |
| llm_provider | string | ❌ | openai | LLM provider (openai, gemini, anthropic, etc.) |
| llm_model | string | ❌ | gpt-3.5-turbo | LLM model name |
| api_key | string | ❌ | "" | API key for the LLM provider |
| temperature | float | ❌ | 0.7 | Temperature for LLM (0.0 - 2.0) |
| max_tokens | integer | ❌ | null | Maximum tokens in LLM response (optional) |
| search_type | string | ❌ | semantic | Type of search (semantic, full_text, hybrid) |
| top | integer | ❌ | 10 | Number of top search results (1-100) |
| embedding_method | string | ❌ | ensemble | Embedding method (ensemble, bge, etc.) |
| response_type | string | ❌ | summary | Response type (general, analysis, summary, qna, next_query, creative) |

**Response Model** (`SearchLLMResult`):
```json
{
  "status": "success",
  "query": "explain what is fingerprint reconstruction",
  "search_results": [
    {
      "doc_id": "doc-001-chunk-1",
      "title": "Fingerprint Analysis Guide",
      "content": "Fingerprint reconstruction is the process...",
      "score": 0.95,
      "author": "Dr. Smith",
      "source": "forensics_guide.pdf",
      "category": "forensics"
    }
  ],
  "llm_response": {
    "status": "completed",
    "answer": "Fingerprint reconstruction is a forensic technique...",
    "provider": "gemini",
    "model": "gemini-2.5-flash",
    "tokens": 245
  },
  "created_at": "2026-04-05T10:30:45.123456"
}
```

**Status Codes**:
- `200` - Success
- `400` - Bad request (missing required fields)
- `502` - Service unavailable (embedding/search/llm service down)
- `503` - Service unreachable
- `500` - Internal server error

**Example cURL**:
```bash
curl -X POST http://localhost:8001/api/v1/orchestrator/search-and-query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "what is RAG",
    "llm_provider": "openai",
    "llm_model": "gpt-4",
    "api_key": "sk-...",
    "temperature": 0.7,
    "top": 5,
    "response_type": "summary"
  }'
```

---

## Document Processing Endpoints

### 2. POST `/api/v1/orchestrator/extract-embed-store`

**Description**: Upload a PDF file, extract text (OCR), generate embeddings, and store in search index

**Request Type**: `multipart/form-data` (File Upload)

**Form Parameters**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| file | file | ✅ | - | PDF file to upload (max size: check config) |
| doc_id_prefix | string | ❌ | doc | Prefix for generated document IDs |
| method | string | ❌ | ensemble | Embedding method (ensemble, bge, etc.) |
| category | string | ❌ | general | Document category for indexing |
| split_by_page | boolean | ❌ | true | Whether to split content by page |

**Response Model** (`OrchestratorResult`):
```json
{
  "status": "success",
  "doc_id": "doc-001",
  "source_pages": 15,
  "documents_indexed": 18,
  "embedding_method": "ensemble",
  "ocr_response": {
    "status": "success",
    "filename": "fingerprints.pdf",
    "pages": 15,
    "extracted_text_length": 45230
  },
  "embedding_response": {
    "status": "completed",
    "documents": 18,
    "method": "ensemble"
  },
  "search_response": {
    "status": "saved",
    "count": 18,
    "index_size": 2845
  },
  "gap_fixes": {
    "gap_1_rag_chunking": "✅ FIXED - Using Vector Service split_text() for 400-token optimal chunks",
    "gap_2_entity_extraction": "✅ FIXED - Extracted keywords, entities, sentiment for each chunk",
    "gap_3_synonym_seeding": "✅ FIXED - Seeded domain-specific synonyms (AI, ML, API, OCR, RAG, NLP, PDF, LLM)",
    "gap_4_version_tracking": "✅ FIXED - Version initialized to '1.0' for all documents"
  },
  "created_at": "2026-04-05T10:35:20.654321"
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:8001/api/v1/orchestrator/extract-embed-store \
  -F "file=@fingerprints.pdf" \
  -F "doc_id_prefix=fingerprint" \
  -F "method=ensemble" \
  -F "category=forensics"
```

**Processing Steps**:
1. Extract text from PDF (OCR)
2. Split into semantic chunks (400-token optimal)
3. Generate embeddings (1536-dimensional)
4. Extract enrichment data (keywords, entities, sentiment)
5. Store in search index with metadata
6. Return consolidated results

---

## Embedding Endpoints

### 3. POST `/api/v1/orchestrator/embed-text`

**Description**: Generate embedding vector for a single text

**Request Body**:
```json
{
  "text": "The quick brown fox jumps over the lazy dog",
  "method": "ensemble"
}
```

**Request Parameters**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| text | string | ✅ | - | Text to embed (cannot be empty) |
| method | string | ❌ | ensemble | Embedding method (ensemble, bge, etc.) |

**Response Model** (`EmbedTextResponse`):
```json
{
  "status": "success",
  "text": "The quick brown fox jumps over the lazy dog",
  "embedding": [0.123, -0.456, 0.789, ...],
  "dimensions": 1536,
  "method": "ensemble",
  "timestamp": "2026-04-05T10:40:15.789123"
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:8001/api/v1/orchestrator/embed-text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "What is machine learning?",
    "method": "ensemble"
  }'
```

---

### 4. POST `/api/v1/orchestrator/embed-batch`

**Description**: Generate embeddings for multiple texts in batch

**Request Body**:
```json
{
  "texts": [
    "First document text",
    "Second document text",
    "Third document text"
  ],
  "method": "ensemble"
}
```

**Request Parameters**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| texts | array[string] | ✅ | - | List of texts to embed |
| method | string | ❌ | ensemble | Embedding method (ensemble, bge, etc.) |

**Response Model** (`EmbedBatchResponse`):
```json
{
  "status": "success",
  "embeddings": [
    {
      "text": "First document text",
      "embedding": [0.123, -0.456, ...],
      "dimensions": 1536
    },
    {
      "text": "Second document text",
      "embedding": [0.234, -0.567, ...],
      "dimensions": 1536
    }
  ],
  "count": 2,
  "method": "ensemble",
  "timestamp": "2026-04-05T10:45:30.123456"
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:8001/api/v1/orchestrator/embed-batch \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Machine learning basics",
      "Deep neural networks",
      "Transformers and attention"
    ],
    "method": "ensemble"
  }'
```

---

### 5. POST `/api/v1/orchestrator/token-count`

**Description**: Get token count for text using Vector Service tokenizer

**Request Body**:
```json
{
  "text": "The quick brown fox jumps over the lazy dog"
}
```

**Response**:
```json
{
  "status": "success",
  "text": "The quick brown fox jumps over the lazy dog",
  "token_count": 14,
  "tokens": ["The", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
  "timestamp": "2026-04-05T10:50:45.456789"
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:8001/api/v1/orchestrator/token-count \
  -H "Content-Type: application/json" \
  -d '{
    "text": "How many tokens does this text contain?"
  }'
```

---

### 6. POST `/api/v1/orchestrator/chunk-text`

**Description**: Chunk text for RAG using Vector Service tokenizer (optimal for context windows)

**Request Body**:
```json
{
  "text": "Long document text that needs to be chunked...",
  "target_tokens": 400,
  "overlap_tokens": 50
}
```

**Request Parameters**:

| Field | Type | Required | Default | Min | Max | Description |
|-------|------|----------|---------|-----|-----|-------------|
| text | string | ✅ | - | - | - | Text to chunk |
| target_tokens | integer | ❌ | 400 | 100 | 2000 | Target tokens per chunk |
| overlap_tokens | integer | ❌ | 50 | 0 | 500 | Overlap tokens between chunks |

**Response**:
```json
{
  "status": "success",
  "chunks": [
    {
      "content": "First chunk of text...",
      "tokens": 398,
      "start_position": 0,
      "end_position": 2150
    },
    {
      "content": "Second chunk of text...",
      "tokens": 402,
      "start_position": 2100,
      "end_position": 4280
    }
  ],
  "total_chunks": 2,
  "total_tokens": 800,
  "timestamp": "2026-04-05T10:55:20.789456"
}
```

**Chunking Strategy**:
- **Token-Optimal**: 400 tokens target strikes balance between context and precision
- **Overlapping**: 50-token overlap prevents context loss at chunk boundaries
- **Semantic Preservation**: Each chunk maintains semantic coherence
- **RAG-Ready**: Chunks perfectly sized for LLM context windows

**Example cURL**:
```bash
curl -X POST http://localhost:8001/api/v1/orchestrator/chunk-text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your long document text here...",
    "target_tokens": 400,
    "overlap_tokens": 50
  }'
```

---

## Health & Diagnostics

### 7. GET `/api/v1/health`

**Description**: Health check endpoint (returns "healthy" if service is running)

**Response Model** (`HealthResponse`):
```json
{
  "status": "healthy",
  "service": "orchestrator"
}
```

**Example cURL**:
```bash
curl http://localhost:8001/api/v1/health
```

---

### 8. GET `/api/v1/diagnostics`

**Description**: Check connectivity and status of all backend services

**Response Model** (`DiagnosticsResponse`):
```json
{
  "orchestrator": "ok",
  "services": {
    "embeddings": {
      "url": "http://localhost:8002",
      "status": "ok",
      "response": {
        "status": "healthy",
        "service": "embeddings"
      }
    },
    "search": {
      "url": "http://localhost:8003",
      "status": "ok",
      "response": {
        "status": "healthy",
        "service": "search"
      }
    },
    "llm": {
      "url": "http://localhost:8004",
      "status": "ok",
      "response": {
        "status": "healthy",
        "service": "llm"
      }
    }
  }
}
```

**Service Status Values**:
- `ok` - Service is healthy
- `error_{code}` - Service returned error (e.g., `error_500`)
- `unreachable` - Cannot connect to service

**Example cURL**:
```bash
curl http://localhost:8001/api/v1/diagnostics
```

---

## Request Models

### SearchQueryRequest
```python
{
  "query": str,                    # Required: Search query
  "llm_provider": str,             # Optional, default: "openai"
  "llm_model": str,                # Optional, default: "gpt-3.5-turbo"
  "api_key": str,                  # Optional, default: ""
  "temperature": float,            # Optional, default: 0.7 (range: 0.0-2.0)
  "max_tokens": Optional[int],     # Optional, default: None
  "search_type": str,              # Optional, default: "semantic"
  "top": int,                      # Optional, default: 10 (range: 1-100)
  "embedding_method": str,         # Optional, default: "ensemble"
  "response_type": str             # Optional, default: "summary"
}
```

**Response Types**:
- `general` - General question answering
- `analysis` - Detailed analysis
- `summary` - Brief summary
- `qna` - Question & Answer format
- `next_query` - Generate follow-up questions
- `creative` - Creative interpretation

---

### ExtractEmbedStoreRequest
```python
{
  "doc_id_prefix": Optional[str],     # Optional, default: "doc"
  "method": Optional[str],            # Optional, default: "ensemble"
  "category": Optional[str],          # Optional, default: "general"
  "split_by_page": Optional[bool]     # Optional, default: True
}
```

---

### EmbedTextRequest
```python
{
  "text": str,              # Required: Text to embed
  "method": str             # Optional, default: "ensemble"
}
```

---

### EmbedBatchRequest
```python
{
  "texts": List[str],       # Required: List of texts to embed
  "method": str             # Optional, default: "ensemble"
}
```

---

### TokenCountRequest
```python
{
  "text": str               # Required: Text to count tokens for
}
```

---

### ChunkTextRequest
```python
{
  "text": str,              # Required: Text to chunk
  "target_tokens": int,     # Optional, default: 400 (range: 100-2000)
  "overlap_tokens": int     # Optional, default: 50 (range: 0-500)
}
```

---

## Response Models

### SearchLLMResult
```python
{
  "status": str,                        # "success", "error", etc.
  "query": str,                         # Original search query
  "search_results": List[Dict],         # Array of search results
  "llm_response": Dict[str, Any],       # LLM response
  "created_at": str                     # ISO format timestamp
}
```

---

### OrchestratorResult
```python
{
  "status": str,                        # "success", "error", etc.
  "doc_id": str,                        # Generated document ID
  "source_pages": int,                  # Number of pages in PDF
  "documents_indexed": int,             # Total chunks created
  "embedding_method": str,              # Method used (ensemble, bge, etc.)
  "ocr_response": Dict[str, Any],       # OCR Service response
  "embedding_response": Dict[str, Any], # Embedding Service response
  "search_response": Dict[str, Any],    # Search Service response
  "gap_fixes": Dict[str, str],          # Summary of gap solutions
  "created_at": str                     # ISO format timestamp
}
```

---

### EmbedTextResponse
```python
{
  "status": str,              # "success", "error", etc.
  "text": str,                # Original text
  "embedding": List[float],   # 1536-dimensional vector
  "dimensions": int,          # 1536
  "method": str,              # Embedding method used
  "timestamp": str            # ISO format timestamp
}
```

---

### EmbedBatchResponse
```python
{
  "status": str,                        # "success", "error", etc.
  "embeddings": List[Dict],             # Array of {text, embedding, dimensions}
  "count": int,                         # Number of embeddings
  "method": str,                        # Embedding method used
  "timestamp": str                      # ISO format timestamp
}
```

---

### HealthResponse
```python
{
  "status": str,       # "healthy", "degraded", "unhealthy"
  "service": str       # "orchestrator"
}
```

---

### DiagnosticsResponse
```python
{
  "orchestrator": str,                  # "ok", "error", "unreachable"
  "services": {
    "embeddings": {
      "url": str,
      "status": str,
      "response": Optional[Dict],
      "error": Optional[str]
    },
    "search": {...},
    "llm": {...}
  }
}
```

---

## Error Handling

### Error Response Format
All errors follow this format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Query processed successfully |
| 400 | Bad Request | Missing required fields or invalid input |
| 502 | Bad Gateway | Backend service returned error |
| 503 | Service Unavailable | Backend service unreachable |
| 500 | Internal Server Error | Unexpected error in orchestrator |

### Common Error Scenarios

**Missing Required Field**:
```json
{
  "detail": "field required"
}
```

**Service Unavailable**:
```json
{
  "detail": "Embedding service unavailable: Connection refused"
}
```

**Invalid Input**:
```json
{
  "detail": "Text cannot be empty"
}
```

---

## Configuration

The Orchestrator Service reads configuration from `config.py`:

```python
# Service URLs (must be running)
EMBEDDING_SERVICE_URL = "http://localhost:8002"
SEARCH_SERVICE_URL = "http://localhost:8003"
LLM_SERVICE_URL = "http://localhost:8004"

# Timeout for backend service calls
TIMEOUT_SECONDS = 30

# API settings
API_TITLE = "Fernova Orchestrator Service"
API_VERSION = "1.0.0"
```

**Required Services** (must be running for orchestrator to function):
1. Vector Embeddings Service (port 8002)
2. Search Service (port 8003)
3. LLM Service (port 8004)

---

## Usage Examples

### Example 1: Complete RAG Search
```bash
# 1. Upload and process document
curl -X POST http://localhost:8001/api/v1/orchestrator/extract-embed-store \
  -F "file=@research_paper.pdf" \
  -F "method=ensemble" \
  -F "category=research"

# 2. Search and query with LLM
curl -X POST http://localhost:8001/api/v1/orchestrator/search-and-query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main findings?",
    "llm_provider": "openai",
    "llm_model": "gpt-4",
    "api_key": "sk-...",
    "response_type": "summary"
  }'
```

### Example 2: Batch Embedding
```bash
curl -X POST http://localhost:8001/api/v1/orchestrator/embed-batch \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Document 1 text",
      "Document 2 text",
      "Document 3 text"
    ],
    "method": "ensemble"
  }'
```

### Example 3: Text Chunking for RAG
```bash
curl -X POST http://localhost:8001/api/v1/orchestrator/chunk-text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your long document here...",
    "target_tokens": 400,
    "overlap_tokens": 50
  }'
```

### Example 4: Check Service Status
```bash
# Health check
curl http://localhost:8001/api/v1/health

# Full diagnostics
curl http://localhost:8001/api/v1/diagnostics
```

---

## Performance Considerations

### Chunking Optimization
- **400 tokens**: Optimal balance between context window and precision
- **50-token overlap**: Prevents context loss at chunk boundaries
- **Processing time**: ~100-200ms per 1000 tokens for chunking

### Embedding Performance
- **Single text**: ~50-100ms per request
- **Batch**: ~200-500ms per 100 texts (more efficient than single)
- **Vector dimensions**: 1536-dimensional vectors from BAAI/bge-large-en-v1.5

### Search Performance
- **Query processing**: ~200-400ms with LLM response
- **Search-only**: ~50-100ms without LLM
- **Context building**: Scales with number of results (typically 5-10 results = ~10-30ms)

---

## Production Deployment

**Environment Variables** (set before running):
```bash
export EMBEDDING_SERVICE_URL=http://embeddings-service:8002
export SEARCH_SERVICE_URL=http://search-service:8003
export LLM_SERVICE_URL=http://llm-service:8004
export TIMEOUT_SECONDS=30
```

**Docker Run**:
```bash
docker run -p 8001:8001 \
  -e EMBEDDING_SERVICE_URL=http://embeddings-service:8002 \
  -e SEARCH_SERVICE_URL=http://search-service:8003 \
  -e LLM_SERVICE_URL=http://llm-service:8004 \
  fernova-orchestrator:latest
```

---

## Version History

- **v1.0.0** (Current): Complete Orchestrator Service with 4 gap fixes
  - RAG-optimized chunking (400-token, 50-token overlap)
  - Entity extraction (keywords, entities, sentiment)
  - Synonym seeding (8 domain groups)
  - Version tracking for documents

---

*Last Updated: April 5, 2026*  
*Part of Fernova AI Suite*
