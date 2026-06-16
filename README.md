# StudyForgeAi

AI-powered study companion MVP for turning notes, PDFs, and PPTX files into summaries, key terms, quizzes, and study guides.

## Demo MVP scope

- Paste text or upload a PDF/PPTX.
- Extract readable document text.
- Generate study aids with Gemini.
- View generated Markdown in tabs.
- Export a result as PDF or Word.

This is intentionally stateless: no accounts, no database, and no saved history.

## Local development

### Backend (FastAPI)

Create `backend/.env` (copy from `backend/.env.example`) and set `GEMINI_API_KEY` to enable `/api/generate`.

```powershell
cd backend
python -m venv venv
./venv/Scripts/python -m pip install --upgrade pip
./venv/Scripts/python -m pip install -r requirements.txt
./venv/Scripts/python -m uvicorn app.main:app --reload --port 8000
```

Verify:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

### Frontend (Vue + Vite)

```powershell
cd frontend
npm install
npm run dev
```

If PowerShell blocks `npm.ps1`, use `npm.cmd` instead (e.g., `npm.cmd install`).

Open `http://localhost:5173`.

## Render deployment

The repo includes `render.yaml` for a two-service Render Blueprint:

- `studyforge-api`: FastAPI backend.
- `studyforge-web`: Vue static frontend.

### Deploy with Blueprint

1. Push this repository to GitHub.
2. In Render, create a new Blueprint from the repo.
3. When Render prompts for `GEMINI_API_KEY`, paste your Gemini API key.
4. Deploy both services.
5. Open `https://studyforge-web.onrender.com`.

### If the service names are already taken

Render service names become part of the public URLs. If `studyforge-api` or `studyforge-web` is unavailable, update these values before deploying:

- `render.yaml`: service names.
- `render.yaml`: `VITE_API_BASE_URL`.
- `render.yaml`: backend `ALLOWED_ORIGINS`.
- `frontend/.env.production`: `VITE_API_BASE_URL`.

### Render notes

- Free instances may sleep after inactivity, so the first request can be slow.
- Do not commit `backend/.env`; set production secrets in Render.
- The backend health check is `/api/health`.
