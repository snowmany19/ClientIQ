# backend/utils/logger.py

import logging
import sys
import os
from datetime import datetime
from typing import Any, Dict, Optional

# Fallback to standard logging if structlog is not available
try:
    import structlog
    USE_STRUCTLOG = True
except ImportError:
    USE_STRUCTLOG = False

def setup_logging(log_level: str = "INFO", log_file: str = "logs/app.log"):
    """Setup logging for the application."""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    if USE_STRUCTLOG:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        return structlog.get_logger()
    else:
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        # Set formatter for all handlers
        fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logger = logging.getLogger("a_incident")
        for handler in logger.handlers:
            handler.setFormatter(logging.Formatter(fmt))
        return logger

def get_logger(name: str = "a_incident") -> logging.Logger:
    if USE_STRUCTLOG:
        return structlog.get_logger(name)
    else:
        return logging.getLogger(name)

def log_security_event(logger, event: str, user_id: Optional[str] = None, 
                      ip_address: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
    message = f"SECURITY_EVENT: {event}"
    if user_id:
        message += f" | User: {user_id}"
    if ip_address:
        message += f" | IP: {ip_address}"
    if details:
        message += f" | Details: {details}"
    logger.warning(message)

def log_api_request(logger, method: str, path: str, 
                   status_code: int, user_id: Optional[str] = None, duration: Optional[float] = None):
    message = f"API_REQUEST: {method} {path} | Status: {status_code}"
    if user_id:
        message += f" | User: {user_id}"
    if duration:
        message += f" | Duration: {duration:.3f}s"
    logger.info(message)

def log_error(logger, error: Exception, context: Optional[Dict[str, Any]] = None):
    message = f"ERROR: {type(error).__name__}: {str(error)}"
    if context:
        message += f" | Context: {context}"
    logger.error(message) 