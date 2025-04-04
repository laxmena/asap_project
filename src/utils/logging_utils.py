import logging
import os
from datetime import datetime
from typing import Optional

class LoggerSetup:
    _instance = None
    _session_id = None
    _consolidated_logger = None

    @classmethod
    def get_logger(cls, session_id: Optional[str] = None, name: str = __name__) -> logging.Logger:
        """Get a logger instance with the specified session ID and name."""
        if cls._instance is None:
            cls._instance = cls()
        
        # Use date-based session ID if not provided
        if session_id is None:
            session_id = datetime.now().strftime("%Y-%m-%d")
        
        # Update session ID if changed
        if cls._session_id != session_id:
            cls._session_id = session_id
            cls._setup_loggers()
        
        # Get component-specific logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # Add handlers if not already added
        if not logger.handlers:
            cls._add_handlers(logger, name)
        
        return logger

    @classmethod
    def _setup_loggers(cls):
        """Set up all loggers with the current session ID."""
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join("logs", cls._session_id)
        os.makedirs(logs_dir, exist_ok=True)
        
        # Setup consolidated logger
        cls._setup_consolidated_logger(logs_dir)
        
        # Clear existing loggers
        logging.getLogger().handlers.clear()
        
        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Add console handler to root logger
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    @classmethod
    def _setup_consolidated_logger(cls, logs_dir: str):
        """Set up the consolidated logger that captures all logs."""
        if cls._consolidated_logger is not None:
            # Remove existing handlers
            for handler in cls._consolidated_logger.handlers[:]:
                cls._consolidated_logger.removeHandler(handler)
        
        cls._consolidated_logger = logging.getLogger("consolidated")
        cls._consolidated_logger.setLevel(logging.DEBUG)
        
        # Add file handler for consolidated logs
        consolidated_file = os.path.join(logs_dir, "consolidated.log")
        file_handler = logging.FileHandler(consolidated_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        cls._consolidated_logger.addHandler(file_handler)

    @classmethod
    def _add_handlers(cls, logger: logging.Logger, name: str):
        """Add handlers to a logger."""
        if cls._session_id is None:
            return
        
        logs_dir = os.path.join("logs", cls._session_id)
        
        # Add file handler for component-specific logs
        component_file = os.path.join(logs_dir, f"{name.split('.')[-1]}.log")
        file_handler = logging.FileHandler(component_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Add handler to forward logs to consolidated logger
        if cls._consolidated_logger is not None:
            # Create a custom handler that forwards logs to the consolidated logger
            class ConsolidatedForwardHandler(logging.Handler):
                def emit(self, record):
                    # Create a new record with the original logger's name
                    new_record = logging.LogRecord(
                        name=record.name,
                        level=record.levelno,
                        pathname=record.pathname,
                        lineno=record.lineno,
                        msg=record.msg,
                        args=record.args,
                        exc_info=record.exc_info,
                        func=record.funcName
                    )
                    cls._consolidated_logger.handle(new_record)
            
            forward_handler = ConsolidatedForwardHandler()
            forward_handler.setLevel(logging.DEBUG)
            forward_handler.setFormatter(file_formatter)
            logger.addHandler(forward_handler) 