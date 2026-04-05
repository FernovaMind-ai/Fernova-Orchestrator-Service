"""
Logging utilities for Fernova Orchestrator Service
"""
import logging
from typing import Any, Dict

# Create logger
logger = logging.getLogger("orchestrator")


def log_section(title: str) -> None:
    """Log a formatted section header"""
    logger.info("=" * 80)
    logger.info(f"  {title}")
    logger.info("=" * 80)


def log_embedding_step(dimensions: int, method: str, first_values: list) -> None:
    """Log embedding conversion step"""
    logger.info(f"✓ Query embedding converted: {dimensions} dimensions, method={method}")
    logger.debug(f"  Embedding vector (first 5 values): {first_values}")


def log_search_step(result_count: int, top_score: float = None) -> None:
    """Log search results step"""
    logger.info(f"✓ Semantic search returned {result_count} results")
    if top_score is not None and result_count > 0:
        logger.debug(f"  Top result score: {top_score}")


def log_llm_step(provider: str, model: str, context_length: int, has_api_key: bool) -> None:
    """Log LLM query step"""
    log_section(f"STEP: Querying LLM Service")
    logger.info(f"Provider: {provider}")
    logger.info(f"Model: {model}")
    logger.info(f"API Key Present: {has_api_key}")
    logger.info(f"Context Length: {context_length} chars")


def log_llm_response(status_code: int, response_keys: list = None) -> None:
    """Log LLM response"""
    logger.info(f"✓ LLM Response Status: {status_code}")
    if response_keys:
        logger.debug(f"  Response Keys: {response_keys}")


def log_error(error_type: str, message: str) -> None:
    """Log error"""
    logger.error(f"✗ {error_type}: {message}")


def log_warning(message: str) -> None:
    """Log warning"""
    logger.warning(f"⚠ {message}")
