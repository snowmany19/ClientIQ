# backend/utils/image_uploader.py

import os
from fastapi import UploadFile
from uuid import uuid4

def save_image(upload: UploadFile, upload_dir="static/images") -> str:
    os.makedirs(upload_dir, exist_ok=True)

    file_extension = os.path.splitext(upload.filename)[-1]
    filename = f"{uuid4().hex}{file_extension}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(upload.file.read())

    return file_path

