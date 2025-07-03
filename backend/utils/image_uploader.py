# backend/utils/image_uploader.py

import os
from fastapi import UploadFile, HTTPException, status
from uuid import uuid4
import hashlib

# File signature (magic bytes) for image validation
IMAGE_SIGNATURES = {
    b'\xff\xd8\xff': 'JPEG',
    b'\x89PNG\r\n\x1a\n': 'PNG',
    b'GIF87a': 'GIF',
    b'GIF89a': 'GIF'
}

def validate_file_content(file_content: bytes) -> bool:
    """Validate file content using magic bytes (file signatures)."""
    for signature, file_type in IMAGE_SIGNATURES.items():
        if file_content.startswith(signature):
            return True
    return False

def calculate_file_hash(file_content: bytes) -> str:
    """Calculate SHA-256 hash of file content for integrity checking."""
    return hashlib.sha256(file_content).hexdigest()

def scan_for_malware(file_content: bytes) -> bool:
    """Basic malware scanning using file signatures and heuristics."""
    # Common malware signatures (basic implementation)
    malware_signatures = [
        b'MZ',  # Executable files
        b'PK\x03\x04',  # ZIP files (potential malware containers)
        b'7F454C46',  # ELF files
    ]
    
    # Check for executable signatures
    for signature in malware_signatures:
        if file_content.startswith(signature):
            return False
    
    # Check for suspicious patterns
    suspicious_patterns = [
        b'<script',  # HTML/JavaScript
        b'<?php',    # PHP code
        b'<%@',      # JSP code
        b'<asp:',    # ASP code
    ]
    
    for pattern in suspicious_patterns:
        if pattern in file_content:
            return False
    
    return True

def save_image(upload: UploadFile, upload_dir="static/images") -> str:
    """Save uploaded image with enhanced security validation."""
    
    # 🔍 File validation
    if not upload:
        return None
    
    # Check file size (max 5MB for security)
    if upload.size and upload.size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 5MB for security reasons."
        )
    
    # Check file extension
    allowed_extensions = ['.jpg', '.jpeg', '.png']
    if not upload.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have a valid filename."
        )
    
    file_extension = os.path.splitext(upload.filename)[-1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG and PNG files are allowed."
        )
    
    # Check MIME type
    allowed_mime_types = ['image/jpeg', 'image/jpg', 'image/png']
    if upload.content_type not in allowed_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPG and PNG images are allowed."
        )
    
    # Read file content for validation
    try:
        content = upload.file.read()
        upload.file.seek(0)  # Reset file pointer for later use
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read uploaded file."
        )
    
    # 🔒 Enhanced security validations
    
    # 1. Validate file content using magic bytes
    if not validate_file_content(content):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file content. File does not contain valid image data."
        )
    
    # 2. Basic malware scanning
    if not scan_for_malware(content):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File appears to contain potentially malicious content."
        )
    
    # 3. Calculate file hash for integrity
    file_hash = calculate_file_hash(content)
    
    # Create upload directory with secure permissions
    os.makedirs(upload_dir, exist_ok=True)
    os.chmod(upload_dir, 0o755)  # Secure directory permissions

    # Generate secure filename with hash
    filename = f"{uuid4().hex}_{file_hash[:8]}{file_extension}"
    file_path = os.path.join(upload_dir, filename)

    # Save file with secure permissions
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Set secure file permissions (read-only for web server)
        os.chmod(file_path, 0o644)
        
        # Verify file was saved and is actually an image
        if os.path.getsize(file_path) == 0:
            os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty."
            )
        
        # Final validation: ensure file is still a valid image
        with open(file_path, 'rb') as f:
            final_content = f.read()
            if not validate_file_content(final_content):
                os.remove(file_path)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File validation failed after save."
                )
        
        return file_path
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save image: {str(e)}"
        )

