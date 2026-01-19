from .BaseProjectException import BaseProjectException


class DBConnectionException(BaseProjectException):
    """Exception raised when document DB connection fails."""
    
    def __init__(self, host: str, port: int, error: Exception):
        """
        Initialize DB connection exception.
        
        Args:
            host: ChromaDB host
            port: ChromaDB port
            error: Original error exception
        """
        if host and port:
            message = f"Failed to connect to ChromaDB at {host}:{port}"
        else:
            message = "Failed to connect to ChromaDB"
        
        if error:
            message += f": {str(error)}"
        
        super().__init__(message, error_code="DB_CONNECTION_ERROR")


class DocumentRetrieveException(BaseProjectException):
    """Exception raised when document retrieval fails."""
    
    def __init__(self, query: str, error: Exception):
        """
        Initialize document retrieval exception.
        
        Args:
            query: The query that failed
            error: Original error exception
        """
        if query:
            message = f"Failed to retrieve documents for query: '{query}'"
        else:
            message = "Failed to retrieve documents"
        
        if error:
            message += f": {str(error)}"
        
        super().__init__(message, error_code="DOCUMENT_RETRIEVE_ERROR")


class ModelResponseException(BaseProjectException):
    """Exception raised when model response generation fails."""
    
    def __init__(self, query: str, error: Exception):
        """
        Initialize model response exception.
        
        Args:
            query: The query for which response generation failed
            error: Original error exception
        """
        if query:
            message = f"Failed to generate model response for query: '{query}'"
        else:
            message = "Failed to generate model response"
        
        if error:
            message += f": {str(error)}"
        
        super().__init__(message, error_code="MODEL_RESPONSE_ERROR")


class RAGQueryException(BaseProjectException):
    """Exception raised when RAG Query fails."""
    
    def __init__(self, query: str, error: Exception):
        """
        Initialize RAG query exception.
        
        Args:
            query: The query that failed
            error: Original error exception
        """
        if query:
            message = f"Failed to execute RAG query: '{query}'"
        else:
            message = "Failed to execute RAG query"
        
        if error:
            message += f": {str(error)}"
        
        super().__init__(message, error_code="RAG_QUERY_ERROR")
