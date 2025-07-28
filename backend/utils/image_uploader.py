# backend/utils/image_uploader.py

import os
from fastapi import UploadFile, HTTPException, status
from uuid import uuid4
import hashlib
from PIL import Image
from datetime import datetime
from typing import Optional
from utils.logger import get_logger

logger = get_logger("image_uploader")

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

def save_image(file: UploadFile, mobile_optimized: bool = False) -> Optional[str]:
    """
    Save uploaded image with optional mobile optimization.
    
    Args:
        file: Uploaded file
        mobile_optimized: If True, optimize for mobile viewing
    
    Returns:
        Path to saved image or None if failed
    """
    try:
        # Create upload directory if it doesn't exist
        upload_dir = "static/images"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid4())[:8]
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        filename = f"violation_{timestamp}_{unique_id}{file_extension}"
        file_path = os.path.join(upload_dir, filename)
        
        # Read and process image
        with Image.open(file.file) as img:
            # Mobile optimization
            if mobile_optimized:
                img = optimize_for_mobile(img)
            
            # Save image
            img.save(file_path, quality=85, optimize=True)
        
        logger.info(f"Image saved successfully: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Failed to save image: {e}")
        return None

def optimize_for_mobile(img: Image.Image) -> Image.Image:
    """
    Optimize image for mobile viewing.
    
    Args:
        img: PIL Image object
    
    Returns:
        Optimized PIL Image object
    """
    # Resize if too large (max 1920x1080 for mobile)
    max_width, max_height = 1920, 1080
    width, height = img.size
    
    if width > max_width or height > max_height:
        # Calculate new dimensions maintaining aspect ratio
        ratio = min(max_width / width, max_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    return img

def extract_gps_from_image(file: UploadFile) -> Optional[str]:
    """
    Extract GPS coordinates from image EXIF data.
    
    Args:
        file: Uploaded image file
    
    Returns:
        GPS coordinates as "latitude,longitude" string or None
    """
    try:
        # Reset file pointer
        file.file.seek(0)
        
        with Image.open(file.file) as img:
            # Check if image has EXIF data
            exif_data = getattr(img, '_getexif', lambda: None)()
            if not exif_data:
                return None
            
            # Extract GPS data
            gps_data = exif_data.get(34853)  # GPS IFD tag
            if not gps_data:
                return None
            
            # Extract latitude and longitude
            lat = extract_gps_coordinate(gps_data, 2, 1)  # GPSLatitude, GPSLatitudeRef
            lon = extract_gps_coordinate(gps_data, 4, 3)  # GPSLongitude, GPSLongitudeRef
            
            if lat is not None and lon is not None:
                return f"{lat},{lon}"
        
        return None
        
    except Exception as e:
        logger.warning(f"Failed to extract GPS from image: {e}")
        return None

def extract_gps_coordinate(gps_data: dict, coord_tag: int, ref_tag: int) -> Optional[float]:
    """
    Extract GPS coordinate from EXIF data.
    
    Args:
        gps_data: GPS EXIF data dictionary
        coord_tag: Coordinate tag (2 for latitude, 4 for longitude)
        ref_tag: Reference tag (1 for latitude ref, 3 for longitude ref)
    
    Returns:
        Coordinate as float or None
    """
    try:
        coord = gps_data.get(coord_tag)
        ref = gps_data.get(ref_tag)
        
        if not coord or not ref:
            return None
        
        # Convert DMS (degrees, minutes, seconds) to decimal
        degrees = float(coord[0])
        minutes = float(coord[1])
        seconds = float(coord[2])
        
        decimal_coord = degrees + (minutes / 60.0) + (seconds / 3600.0)
        
        # Apply reference (N/S for latitude, E/W for longitude)
        if ref in ['S', 'W']:
            decimal_coord = -decimal_coord
        
        return round(decimal_coord, 6)
        
    except Exception as e:
        logger.warning(f"Failed to extract GPS coordinate: {e}")
        return None

def get_image_info(file_path: str) -> dict:
    """
    Get image information including metadata.
    
    Args:
        file_path: Path to image file
    
    Returns:
        Dictionary with image information
    """
    try:
        with Image.open(file_path) as img:
            info = {
                "size": img.size,
                "mode": img.mode,
                "format": img.format,
                "file_size": os.path.getsize(file_path)
            }
            
            # Try to get EXIF data
            try:
                exif_data = getattr(img, '_getexif', lambda: None)()
                if exif_data:
                    info["has_exif"] = True
                    info["exif_keys"] = list(exif_data.keys())
                else:
                    info["has_exif"] = False
            except:
                info["has_exif"] = False
            
            return info
            
    except Exception as e:
        logger.error(f"Failed to get image info: {e}")
        return {}

