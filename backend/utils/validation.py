# utils/validation.py
# Input validation utilities for the A.I.ncident application

import re
import os
from typing import Optional, List
from fastapi import UploadFile, HTTPException, status
from utils.exceptions import ValidationException, FileOperationException
from utils.logger import get_logger

logger = get_logger("validation")

class InputValidator:
    """Centralized input validation for the application."""
    
    # File validation constants
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png"]
    ALLOWED_PDF_TYPES = ["application/pdf"]
    
    # Text validation patterns
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]{3,20}$')
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    STORE_NAME_PATTERN = re.compile(r'^Store #\d{3}$')
    
    @classmethod
    def validate_incident_description(cls, description: str) -> str:
        """Validate incident description."""
        if not description or not description.strip():
            raise ValidationException("Description is required")
        
        description = description.strip()
        
        if len(description) < 10:
            raise ValidationException("Description must be at least 10 characters long")
        
        if len(description) > 2000:
            raise ValidationException("Description must be less than 2000 characters")
        
        return description
    
    @classmethod
    def validate_store_name(cls, store_name: str) -> str:
        """Validate store name format."""
        if not store_name or not store_name.strip():
            raise ValidationException("Store name is required")
        
        store_name = store_name.strip()
        
        # Check if it matches the expected format (Store #XXX)
        if not cls.STORE_NAME_PATTERN.match(store_name):
            raise ValidationException("Store name must be in format 'Store #XXX' (e.g., 'Store #001')")
        
        return store_name
    
    @classmethod
    def validate_location(cls, location: str) -> str:
        """Validate location field."""
        if not location or not location.strip():
            raise ValidationException("Location is required")
        
        location = location.strip()
        
        if len(location) < 2:
            raise ValidationException("Location must be at least 2 characters long")
        
        if len(location) > 100:
            raise ValidationException("Location must be less than 100 characters")
        
        return location
    
    @classmethod
    def validate_offender(cls, offender: str) -> str:
        """Validate offender field."""
        if not offender or not offender.strip():
            raise ValidationException("Offender information is required")
        
        offender = offender.strip()
        
        if len(offender) < 2:
            raise ValidationException("Offender information must be at least 2 characters long")
        
        if len(offender) > 100:
            raise ValidationException("Offender information must be less than 100 characters")
        
        return offender
    
    @classmethod
    def validate_file_upload(cls, file: Optional[UploadFile], required: bool = False) -> Optional[str]:
        """Validate file upload."""
        if not file:
            if required:
                raise ValidationException("File is required")
            return None
        
        # Check file size
        if file.size and file.size > cls.MAX_FILE_SIZE:
            raise ValidationException(f"File size must be less than {cls.MAX_FILE_SIZE // (1024*1024)}MB")
        
        # Check file type
        if file.content_type not in cls.ALLOWED_IMAGE_TYPES:
            raise ValidationException("Only JPG and PNG files are allowed")
        
        # Check filename
        if file.filename:
            filename = file.filename.lower()
            if not any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                raise ValidationException("File must have .jpg, .jpeg, or .png extension")
        
        return file.filename
    
    @classmethod
    def validate_pagination_params(cls, skip: int, limit: int) -> tuple[int, int]:
        """Validate pagination parameters."""
        if skip < 0:
            raise ValidationException("Skip must be 0 or greater")
        
        if limit < 1 or limit > 100:
            raise ValidationException("Limit must be between 1 and 100")
        
        return skip, limit
    
    @classmethod
    def validate_username(cls, username: str) -> str:
        """Validate username format."""
        if not username or not username.strip():
            raise ValidationException("Username is required")
        
        username = username.strip()
        
        if not cls.USERNAME_PATTERN.match(username):
            raise ValidationException("Username must be 3-20 characters long and contain only letters, numbers, and underscores")
        
        return username
    
    @classmethod
    def validate_email(cls, email: str) -> str:
        """Validate email format."""
        if not email or not email.strip():
            raise ValidationException("Email is required")
        
        email = email.strip()
        
        if not cls.EMAIL_PATTERN.match(email):
            raise ValidationException("Invalid email format")
        
        return email
    
    @classmethod
    def validate_password(cls, password: str) -> str:
        """Validate password strength."""
        if not password:
            raise ValidationException("Password is required")
        
        if len(password) < 8:
            raise ValidationException("Password must be at least 8 characters long")
        
        if len(password) > 128:
            raise ValidationException("Password must be less than 128 characters")
        
        # Check for common weak passwords
        weak_passwords = ['password', '123456', 'admin', 'test', 'qwerty']
        if password.lower() in weak_passwords:
            raise ValidationException("Password is too common. Please choose a stronger password")
        
        return password
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitize filename for security."""
        if not filename:
            return ""
        
        # Remove path traversal attempts
        filename = os.path.basename(filename)
        
        # Remove any non-alphanumeric characters except dots and hyphens
        filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
        
        # Ensure it doesn't start with a dot
        if filename.startswith('.'):
            filename = filename[1:]
        
        return filename
    
    @classmethod
    def validate_file_path(cls, file_path: str, allowed_extensions: List[str] = None) -> str:
        """Validate file path for security."""
        if not file_path:
            raise ValidationException("File path is required")
        
        # Check for path traversal attempts
        if '..' in file_path or '/' in file_path or '\\' in file_path:
            raise ValidationException("Invalid file path")
        
        # Check file extension if specified
        if allowed_extensions:
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in allowed_extensions:
                raise ValidationException(f"File must have one of these extensions: {', '.join(allowed_extensions)}")
        
        return file_path

def validate_incident_data(description: str, store: str, location: str, offender: str, file: Optional[UploadFile] = None) -> dict:
    """Validate all incident data at once."""
    validated_data = {
        'description': InputValidator.validate_incident_description(description),
        'store': InputValidator.validate_store_name(store),
        'location': InputValidator.validate_location(location),
        'offender': InputValidator.validate_offender(offender),
        'filename': InputValidator.validate_file_upload(file)
    }
    
    logger.info("Incident data validation successful")
    return validated_data

def validate_user_data(username: str, email: str, password: str) -> dict:
    """Validate all user data at once."""
    validated_data = {
        'username': InputValidator.validate_username(username),
        'email': InputValidator.validate_email(email),
        'password': InputValidator.validate_password(password)
    }
    
    logger.info("User data validation successful")
    return validated_data 