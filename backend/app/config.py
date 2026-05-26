from __future__ import annotations

from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

BACKEND_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BACKEND_DIR / "data"
CHROMA_DIR = BACKEND_DIR / "chroma_db"


def env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is None:
        return default
    value = value.strip()
    return value if value else default


GEMINI_API_KEY = env("GEMINI_API_KEY")

# Comma-separated list, e.g. "http://localhost:5173,http://127.0.0.1:5173"
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in (env("ALLOWED_ORIGINS", "") or "").split(",")
    if origin.strip()
]
