import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

UPLOAD_DIR = Path(__file__).resolve().parent / "static" / "uploads"
ALLOWED = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
DOC_ALLOWED = ALLOWED | {".pdf"}


def save_upload(file: UploadFile, prefix: str = "file", *, documents: bool = False) -> str:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "image.jpg").suffix.lower()
    allowed = DOC_ALLOWED if documents else ALLOWED
    if suffix not in allowed:
        raise HTTPException(status_code=400, detail="Можно загрузить jpg, png, webp, gif или pdf")
    name = f"{prefix}-{uuid.uuid4().hex}{suffix}"
    path = UPLOAD_DIR / name
    content = file.file.read()
    limit = 16 * 1024 * 1024 if documents else 8 * 1024 * 1024
    if len(content) > limit:
        raise HTTPException(status_code=400, detail="Файл слишком большой")
    path.write_bytes(content)
    return f"/assets/uploads/{name}"
