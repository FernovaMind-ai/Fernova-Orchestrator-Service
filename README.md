# Fernova Orchestrator Service

New orchestration API for end-to-end OCR -> embeddings -> search ingestion.

## Endpoints

- `GET /api/v1/health` - health check
- `POST /api/v1/orchestrator/extract-embed-store` - upload PDF, extract text, embed texts, store in Fernova AI Search
- `POST /api/v1/orchestrator/search-and-query` - search documents and query LLM with results

## Environment

- `OCR_SERVICE_URL` (default `http://127.0.0.1:8000`)
- `EMBEDDING_SERVICE_URL` (default `http://127.0.0.1:8001`)
- `SEARCH_SERVICE_URL` (default `http://127.0.0.1:8002`)
- `LLM_SERVICE_URL` (default `http://127.0.0.1:8004`)

## Run

```bash
uvicorn main:app --host 0.0.0.0 --port 8003
```
