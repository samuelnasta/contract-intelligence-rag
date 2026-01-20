"""Custom exceptions for the project."""


class BaseProjectException(Exception):
    """Base exception class for the project."""
    
    def __init__(self, message: str, error_code: str):
        """
        Initialize the exception.
        
        Args:
            message: The error message
            error_code: Error code for categorization
        """
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """String representation of the exception."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message
    