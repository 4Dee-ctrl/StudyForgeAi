# Local Run Baseline (Monorepo)

This is a quick sanity-check guide for the current `frontend/` + `backend/` layout.
The canonical implementation plan is in `01_project_setup_and_dev_environment.md`.

## Success criteria

- Backend starts with no errors.
- `GET http://127.0.0.1:8000/api/health` returns HTTP 200 and JSON `{ "status": "ok" }`.
- Frontend dev server starts and serves `http://localhost:5173`.

## Backend (FastAPI)

```powershell
cd backend
python -m venv venv
./venv/Scripts/python -m pip install --upgrade pip
./venv/Scripts/python -m pip install -r requirements.txt

# Optional but recommended:
# Copy backend/.env.example -> backend/.env and set GEMINI_API_KEY to enable /api/generate

./venv/Scripts/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Verify:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

## Frontend (Vue + Vite)

```powershell
cd frontend

# If PowerShell blocks npm.ps1, use npm.cmd instead.
npm.cmd install
npm.cmd run dev
```

## Troubleshooting

- Port 8000 already in use:
  - Run with a different port: `./venv/Scripts/python -m uvicorn app.main:app --reload --port 8001`
- Dependency install failures:
  - Paste the full error output and we’ll fix it before proceeding.
