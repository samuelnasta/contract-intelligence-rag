import logging
import logging.handlers
from pathlib import Path


class Logger:
    """A logger class for the contract intelligence RAG project."""
    
    _instance = None
    _initialized = False

    def __new__(cls):
        """Implement singleton pattern to ensure only one logger instance."""
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the logger if not already initialized."""
        if Logger._initialized:
            return
        
        self.logger = logging.getLogger("ContractIntelligenceRAG")
        self.logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        self.logger.handlers.clear()

        # Create logs directory if it doesn't exist
        logs_dir = Path(__file__).parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True)

        # Create formatters
        detailed_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        simple_formatter = logging.Formatter("%(levelname)s - %(message)s")

        # Console handler (INFO level)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # File handler (DEBUG level)
        file_handler = logging.handlers.RotatingFileHandler(
            logs_dir / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Error file handler
        error_handler = logging.FileHandler(logs_dir / "error.log")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        
        # Add handlers to logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        
        Logger._initialized = True
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """Log critical message."""
        self.logger.critical(message)


def get_logger() -> Logger:
    """Get the singleton logger instance."""
    return Logger()
