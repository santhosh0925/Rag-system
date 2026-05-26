# Chat With Your Documents

Minimal RAG app:
- Upload `.txt` documents
- Ingest into a local Chroma vector DB
- Chat against the ingested content using Gemini

## Backend setup (Windows / PowerShell)

From repo root:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `backend/.env`:

```env
GEMINI_API_KEY=YOUR_KEY_HERE
```

Run the server:

```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open the UI:
- `http://127.0.0.1:8000/`

If you want to run from the repo root (without `cd backend`), use `--app-dir`:

```powershell
.\backend\venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

## Notes
- Documents are saved to `backend/data/`
- Chroma persistence lives in `backend/chroma_db/`
- Only `.txt` is supported in the UI endpoints (`/api/upload`)
