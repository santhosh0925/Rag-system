from __future__ import annotations

from pathlib import Path
import shutil
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .config import ALLOWED_ORIGINS, DATA_DIR

app = FastAPI(title="Chat With Your Documents")

origins = ALLOWED_ORIGINS or ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


@app.get("/")
def index():
    index_file = FRONTEND_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend not found.")
    return FileResponse(str(index_file))


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/upload")
async def upload(files: List[UploadFile] = File(...)):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    saved = []
    for uploaded in files:
        if not uploaded.filename:
            continue
        if not uploaded.filename.lower().endswith(".txt"):
            raise HTTPException(status_code=400, detail="Only .txt files are supported.")
        dest = DATA_DIR / Path(uploaded.filename).name
        with dest.open("wb") as f:
            shutil.copyfileobj(uploaded.file, f)
        saved.append(dest.name)
    if not saved:
        raise HTTPException(status_code=400, detail="No files uploaded.")
    return {"saved": saved}


@app.post("/api/ingest")
def ingest():
    from .ingest import ingest_documents
    ingest_documents()
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    question = (payload.question or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is required.")
    try:
        from .rag_pipeline import query_rag
        answer = query_rag(question)
        return ChatResponse(answer=answer)
    except RuntimeError as e:
        msg = str(e)
        status = 502
        if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
            status = 429
        raise HTTPException(status_code=status, detail=msg) from e
