"""
Search and Query Routes
"""
import ast
from datetime import datetime
import httpx
from fastapi import APIRouter, HTTPException, File, UploadFile

from config import settings
from models.requests import SearchQueryRequest, ExtractEmbedStoreRequest
from models.responses import SearchLLMResult, OrchestratorResult
from services import embedding_service, search_service, llm_service
from utils.exceptions import (
    EmbeddingServiceError,
    SearchServiceError,
    LLMServiceError,
    ServiceUnavailableError,
)
from utils.logging import log_search_step, log_error

router = APIRouter(prefix="/api/v1/orchestrator", tags=["search"])


async def extract_content_from_result(result: dict) -> tuple:
    """
    Extract content and title from search result
    
    Args:
        result: Search result dictionary
    
    Returns:
        Tuple of (snippet, title)
    """
    content_data = result.get("content", {})
    
    if isinstance(content_data, dict):
        # Content fields are nested in dict
        snippet = str(
            content_data.get("content") or
            content_data.get("text") or
            content_data.get("description") or
            ""
        ).strip()
        title = content_data.get("title", "Untitled")
    else:
        # Fallback if content is a string
        snippet = str(content_data).strip()
        title = result.get("title", "Untitled")
    
    # Truncate snippet to 2000 chars to preserve content detail
    if len(snippet) > 2000:
        snippet = snippet[:2000] + "..."
    
    return snippet, title


async def build_context_from_results(search_results: list) -> str:
    """
    Build LLM context from search results
    
    Args:
        search_results: List of search results
    
    Returns:
        Formatted context string
    """
    context_lines = ["Semantic Search Results (ranked by relevance):"]
    
    if not search_results:
        context_lines.append("No documents found matching the query. Answering based on general knowledge.")
    
    for idx, result in enumerate(search_results, start=1):
        snippet, title = await extract_content_from_result(result)
        similarity_score = result.get("score", 0)
        
        context_lines.append(
            f"{idx}. [Score: {similarity_score}] {title} - {snippet}"
        )
    
    return "\n".join(context_lines)


@router.post("/search-and-query", response_model=SearchLLMResult)
async def search_and_query(request: SearchQueryRequest) -> SearchLLMResult:
    """
    Search documents using embedding-based semantic search, then query LLM
    
    This endpoint performs the following steps:
    1. Convert query to embeddings
    2. Perform semantic search on indexed documents
    3. Build context from search results
    4. Query LLM with context
    5. Return search results and LLM response
    
    Args:
        request: SearchQueryRequest with query and LLM configuration
    
    Returns:
        SearchLLMResult with search results and LLM response
    
    Raises:
        HTTPException: If any service call fails
    """
    try:
        # Step 1: Convert query to embeddings
        try:
            embed_data = await embedding_service.embed_text(
                request.query,
                method=request.embedding_method
            )
        except EmbeddingServiceError as e:
            raise HTTPException(status_code=502, detail=str(e))
        except ServiceUnavailableError as e:
            raise HTTPException(status_code=503, detail=str(e))
        
        # Step 2: Perform semantic search
        try:
            search_data = await search_service.semantic_search(
                query=request.query,
                top_k=request.top,
                method=request.embedding_method
            )
        except SearchServiceError as e:
            raise HTTPException(status_code=502, detail=str(e))
        except ServiceUnavailableError as e:
            raise HTTPException(status_code=503, detail=str(e))
        
        search_results = search_data.get("results", [])
        log_search_step(len(search_results))
        
        # Step 3: Build context from search results
        context = await build_context_from_results(search_results)
        
        # Step 4: Query LLM
        llm_data = {}
        try:
            llm_data = await llm_service.query(
                query=request.query,
                context=context,
                provider=request.llm_provider,
                model=request.llm_model,
                api_key=request.api_key,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                response_type=request.response_type,
            )
        except LLMServiceError as e:
            # Don't fail on LLM error, return what we have
            log_error("LLMServiceError", str(e))
            llm_data = {"error": str(e), "status": "error"}
        except ServiceUnavailableError as e:
            log_error("ServiceUnavailableError", str(e))
            llm_data = {"error": str(e), "status": "unavailable"}
        except Exception as e:
            log_error("UnexpectedError", str(e))
            llm_data = {"error": str(e), "status": "error"}
        
        # Step 5: Return final response
        return SearchLLMResult(
            status="success",
            query=request.query,
            search_results=search_results,
            llm_response=llm_data,
            created_at=datetime.now().isoformat(),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        log_error("OrchestratorError", str(e))
        raise HTTPException(status_code=500, detail=f"Orchestrator error: {str(e)}")


@router.post("/extract-embed-store", response_model=OrchestratorResult)
async def extract_embed_store(
    file: UploadFile = File(...),
    doc_id_prefix: str = "doc",
    method: str = "ensemble",
    category: str = "general",
    split_by_page: bool = True,
    include_full_text: bool = True
) -> OrchestratorResult:
    """
    Extract content from uploaded file, generate embeddings, and store in search service
    
    This endpoint orchestrates the following workflow:
    1. Send file to OCR service for extraction (handles PDFs, images, etc.)
    2. Extract text content from OCR response
    3. Generate embeddings using specified method
    4. Store documents in search service
    5. Return extraction and indexing results
    
    Args:
        file: Uploaded file (PDF, image, text, etc.)
        doc_id_prefix: Prefix for generated document IDs
        method: Embedding method to use (ensemble, bge, etc.)
        category: Category for the document
        split_by_page: Whether to split extracted content by pages
        include_full_text: Include full text in OCR extraction
    
    Returns:
        OrchestratorResult with extraction and indexing details
    
    Raises:
        HTTPException: If file processing or service calls fail
    """
    try:
        # Generate document ID
        doc_id = f"{doc_id_prefix}_{file.filename}_{int(datetime.now().timestamp())}"
        
        # Step 1: Send file to OCR service for extraction
        ocr_response = {}
        file_text = ""
        source_pages = 0
        
        try:
            # Read file content
            file_content = await file.read()
            
            # Call OCR service
            async with httpx.AsyncClient(timeout=httpx.Timeout(settings.TIMEOUT_SECONDS)) as client:
                files_to_send = {"file": (file.filename, file_content)}
                ocr_response = await client.post(
                    f"{settings.OCR_SERVICE_URL}/api/v1/extract",
                    files=files_to_send,
                    params={"include_full_text": include_full_text}
                )
            
            if ocr_response.status_code >= 400:
                raise HTTPException(
                    status_code=ocr_response.status_code,
                    detail=f"OCR extraction failed: {ocr_response.text}"
                )
            
            ocr_data = ocr_response.json()
            
            # Extract text from OCR response
            # The OCR service returns different formats depending on file type
            if "full_text" in ocr_data:
                file_text = ocr_data["full_text"]
            elif "text" in ocr_data:
                file_text = ocr_data["text"]
            elif "content" in ocr_data:
                file_text = ocr_data["content"]
            else:
                file_text = str(ocr_data)
            
            source_pages = ocr_data.get("page_count", ocr_data.get("total_pages", 1))
            
        except EmbeddingServiceError as e:
            raise HTTPException(status_code=502, detail=f"OCR extraction error: {str(e)}")
        except ServiceUnavailableError as e:
            raise HTTPException(status_code=503, detail=f"OCR service unavailable: {str(e)}")
        
        # Step 2: Split extracted content into documents
        documents = []
        if split_by_page and "\f" in file_text:
            # Split by page break character
            pages = file_text.split("\f")
            documents = [
                {
                    "doc_id": f"{doc_id}_page_{idx}",
                    "title": f"{file.filename} - Page {idx + 1}",
                    "description": f"Page {idx + 1} of {file.filename}",
                    "content": page.strip(),
                    "category": category,
                    "metadata": {
                        "source_file": file.filename,
                        "page_number": idx + 1,
                        "total_pages": len(pages)
                    }
                }
                for idx, page in enumerate(pages)
                if page.strip()
            ]
        else:
            documents = [
                {
                    "doc_id": doc_id,
                    "title": file.filename,
                    "description": f"Document: {file.filename}",
                    "content": file_text,
                    "category": category,
                    "metadata": {
                        "source_file": file.filename,
                        "upload_time": datetime.now().isoformat()
                    }
                }
            ]
        
        if not documents:
            raise HTTPException(
                status_code=400,
                detail="No content extracted from file"
            )
        
        # Step 3: Generate embeddings for each document
        embedding_results = []
        try:
            for doc in documents:
                embed_data = await embedding_service.embed_text(
                    doc["content"],
                    method=method
                )
                doc["embedding"] = embed_data.get("embedding")
                embedding_results.append(embed_data)
        except EmbeddingServiceError as e:
            raise HTTPException(status_code=502, detail=f"Embedding error: {str(e)}")
        except ServiceUnavailableError as e:
            raise HTTPException(status_code=503, detail=f"Embedding service unavailable: {str(e)}")
        
        # Step 4: Store documents in search service
        search_results = {}
        try:
            search_results = await search_service.batch_store_documents(
                documents=documents,
                method=method
            )
        except SearchServiceError as e:
            raise HTTPException(status_code=502, detail=f"Search storage error: {str(e)}")
        except ServiceUnavailableError as e:
            raise HTTPException(status_code=503, detail=f"Search service unavailable: {str(e)}")
        
        # Step 5: Return success response
        return OrchestratorResult(
            status="success",
            doc_id=doc_id,
            source_pages=source_pages,
            documents_indexed=len(documents),
            embedding_method=method,
            ocr_response={
                "status": "success",
                "filename": file.filename,
                "pages": source_pages,
                "extracted_text_length": len(file_text)
            },
            embedding_response={
                "status": "completed",
                "documents": len(documents),
                "method": method
            },
            search_response=search_results,
            created_at=datetime.now().isoformat(),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        log_error("ExtractEmbedStoreError", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Extract-embed-store error: {str(e)}"
        )
