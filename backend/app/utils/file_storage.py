import pathlib
import uuid

from fastapi import UploadFile

from ..config import UPLOAD_DIR
from ..core.exceptions import err

ALLOWED = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "application/pdf": ".pdf"}


async def save_upload(f: UploadFile) -> str:
    ext = ALLOWED.get(f.content_type or "")
    if not ext:
        raise err(415, "Only JPEG, PNG, WebP or PDF files are allowed")
    data = await f.read()
    if len(data) > 5 * 1024 * 1024:
        raise err(413, "File is larger than 5 MB")
    pathlib.Path(UPLOAD_DIR).mkdir(exist_ok=True)
    name = uuid.uuid4().hex + ext
    (pathlib.Path(UPLOAD_DIR) / name).write_bytes(data)
    return f"/uploads/{name}"
