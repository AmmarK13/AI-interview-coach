import os
import uuid
from fastapi import UploadFile, File, HTTPException

def save_upload(file: UploadFile, subfolder: str = "audio/answers") -> str:
    # 1) Build absolute folder path from project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    target_dir = os.path.join(project_root, subfolder)

    # 2) Ensure folder exists
    os.makedirs(target_dir, exist_ok=True)

    # 3) Create safe unique filename and write file
    original_name = os.path.basename(file.filename or "upload.bin")
    ext = os.path.splitext(original_name)[1].lower()
    safe_name = f"{uuid.uuid4().hex}{ext}"
    full_path = os.path.join(target_dir, safe_name)

    try:
        with open(full_path, "wb") as f:
            f.write(file.file.read())  # for large files, use chunked copy
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
    finally:
        file.file.close()

    return full_path