# backend/utils/image_uploader.py

import os
from fastapi import UploadFile, HTTPException, status
from uuid import uuid4

def save_image(upload: UploadFile, upload_dir="static/images") -> str:
    """Save uploaded image with comprehensive validation."""
    
    # 🔍 File validation
    if not upload:
        return None
    
    # Check file size (max 10MB)
    if upload.size and upload.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 10MB."
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
    
    # Create upload directory
    os.makedirs(upload_dir, exist_ok=True)

    # Generate secure filename
    filename = f"{uuid4().hex}{file_extension}"
    file_path = os.path.join(upload_dir, filename)

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            content = upload.file.read()
            buffer.write(content)
        
        # Verify file was saved and is actually an image
        if os.path.getsize(file_path) == 0:
            os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty."
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

