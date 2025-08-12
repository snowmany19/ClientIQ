# utils/exceptions.py
# Custom exception handling for the ContractGuard.ai application

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
from typing import Union
from utils.logger import get_logger

logger = get_logger("exceptions")

class ContractGuardAIException(Exception):
    """Base exception for ContractGuard.ai application."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ValidationException(ContractGuardAIException):
    """Raised when input validation fails."""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)

class AuthenticationException(ContractGuardAIException):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)

class AuthorizationException(ContractGuardAIException):
    """Raised when authorization fails."""
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, status_code=403)

class ResourceNotFoundException(ContractGuardAIException):
    """Raised when a requested resource is not found."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)

class SubscriptionRequiredException(ContractGuardAIException):
    """Raised when an active subscription is required."""
    def __init__(self, message: str = "Active subscription required"):
        super().__init__(message, status_code=402)

class FileOperationException(ContractGuardAIException):
    """Raised when file operations fail."""
    def __init__(self, message: str = "File operation failed"):
        super().__init__(message, status_code=500)

async def custom_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for the FastAPI application."""
    
    # Handle our custom exceptions
    if isinstance(exc, ContractGuardAIException):
        logger.warning(f"Custom exception: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "type": exc.__class__.__name__}
        )
    
    # Handle FastAPI HTTP exceptions
    if isinstance(exc, HTTPException):
        logger.warning(f"HTTP exception: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "type": "HTTPException"}
        )
    
    # Handle Pydantic validation errors
    if isinstance(exc, ValidationError):
        logger.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation error",
                "errors": exc.errors(),
                "type": "ValidationError"
            }
        )
    
    # Handle SQLAlchemy errors
    if isinstance(exc, SQLAlchemyError):
        logger.error(f"Database error: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Database operation failed",
                "type": "DatabaseError"
            }
        )
    
    # Handle IntegrityError specifically
    if isinstance(exc, IntegrityError):
        logger.error(f"Database integrity error: {str(exc)}")
        return JSONResponse(
            status_code=409,
            content={
                "detail": "Data integrity constraint violated",
                "type": "IntegrityError"
            }
        )
    
    # Handle generic exceptions
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": "InternalError"
        }
    )

def handle_database_operation(func):
    """Decorator to handle database operations with proper error handling."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as e:
            logger.error(f"Database operation failed in {func.__name__}: {str(e)}")
            raise ContractGuardAIException(f"Database operation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise ContractGuardAIException(f"Operation failed: {str(e)}")
    return wrapper 