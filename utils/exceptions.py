"""
Custom exceptions for Fernova Orchestrator Service
"""


class OrchestratorException(Exception):
    """Base exception for orchestrator"""
    pass


class EmbeddingServiceError(OrchestratorException):
    """Error from embedding service"""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Embedding service error [{status_code}]: {message}")


class SearchServiceError(OrchestratorException):
    """Error from search service"""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Search service error [{status_code}]: {message}")


class LLMServiceError(OrchestratorException):
    """Error from LLM service"""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"LLM service error [{status_code}]: {message}")


class OCRServiceError(OrchestratorException):
    """Error from OCR service"""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"OCR service error [{status_code}]: {message}")


class ServiceUnavailableError(OrchestratorException):
    """Service is unavailable (connection error)"""
    def __init__(self, service_name: str, error: str):
        self.service_name = service_name
        self.error = error
        super().__init__(f"{service_name} service unavailable: {error}")


class InvalidInputError(OrchestratorException):
    """Invalid input provided"""
    pass


class DataExtractionError(OrchestratorException):
    """Error extracting data from response"""
    pass
