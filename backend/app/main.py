import pathlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import models  # noqa: F401  (registers tables)
from .api.v1.router import api_router
from .config import CORS_ORIGINS, UPLOAD_DIR
from .database import Base, engine

pathlib.Path(UPLOAD_DIR).mkdir(exist_ok=True)
Base.metadata.create_all(engine)  # swap for Alembic migrations in production

app = FastAPI(title="Unlock - Resource Sharing Platform", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_methods=["*"], allow_headers=["*"])
app.include_router(api_router, prefix="/api/v1")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/health")
def health():
    return {"status": "ok"}
