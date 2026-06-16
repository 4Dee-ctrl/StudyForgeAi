# 01 — Project Setup & Development Environment

> **Phase:** 1 of 9
> **Goal:** Scaffold both frontend and backend projects, install all dependencies, and establish development tooling so that both servers run locally and can communicate.
> **Estimated Time:** 1–2 hours

---

## 1. Prerequisites Checklist

Before writing any code, ensure the following are installed on your machine:

| Tool | Purpose | Verify Command |
|---|---|---|
| **Node.js** (v18+) | Runs Vue.js dev server and build tools | `node --version` |
| **npm** (v9+) | JavaScript package manager | `npm --version` |
| **Python** (v3.10+) | Runs the FastAPI backend | `python --version` |
| **pip** | Python package manager | `pip --version` |
| **Git** | Version control | `git --version` |
| **VS Code** | Recommended IDE | — |

### Recommended VS Code Extensions

- **Vue - Official** (Vue.volar) — Vue.js language support
- **Python** (ms-python.python) — Python IntelliSense and debugging
- **Pylance** — Advanced Python type checking
- **REST Client** or **Thunder Client** — Test API endpoints without Postman
- **GitLens** — Enhanced Git integration

---

## 2. Repository Structure

We'll use a **monorepo** approach — one GitHub repository with two top-level directories:

```
ai-proj-main/
├── plans/          # Planning documentation (this folder)
├── frontend/       # Vue.js application
├── backend/        # Python FastAPI application
├── .gitignore      # Root gitignore
└── README.md       # Project overview
```

### Why Monorepo?

- Simpler for a solo developer — one repo to manage
- Easy to reference backend schemas from frontend docs
- Single PR for full-stack features
- Both Vercel and Render support monorepo deployments (set root directory)

---

## 3. Frontend Scaffolding (Vue.js + Vite)

### 3.1 Create the Vue Project

Use Vite's official Vue template. Run from the `ai-proj-main/` root:

```bash
npm create vite@latest frontend -- --template vue
```

This creates a `frontend/` directory with a minimal Vue 3 + Vite setup.

### 3.2 Install Frontend Dependencies

Navigate into `frontend/` and install:

```bash
cd frontend
npm install
```

**Additional dependencies to install:**

| Package | Purpose | Install Command |
|---|---|---|
| `vue-router` | Client-side routing (if multi-page) | `npm install vue-router` |
| `pinia` | State management | `npm install pinia` |
| `axios` | HTTP client for API calls | `npm install axios` |
| `marked` | Render Markdown responses from Gemini | `npm install marked` |
| `dompurify` | Sanitize HTML from Markdown rendering | `npm install dompurify` |

Combined:
```bash
npm install vue-router pinia axios marked dompurify
```

### 3.3 Verify Frontend Runs

```bash
npm run dev
```

You should see the Vite dev server at `http://localhost:5173`. Confirm the default Vue page loads.

### 3.4 Frontend Environment Variables

Create a `frontend/.env.development` file:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Create a `frontend/.env.production` file:

```env
VITE_API_BASE_URL=https://your-backend-name.onrender.com
```

> **Note:** In Vite, environment variables must be prefixed with `VITE_` to be exposed to client-side code. Access them via `import.meta.env.VITE_API_BASE_URL`.

---

## 4. Backend Scaffolding (Python + FastAPI)

### 4.1 Create the Backend Directory

```bash
mkdir backend
cd backend
```

### 4.2 Create a Virtual Environment

Always use a virtual environment to isolate Python dependencies:

```bash
python -m venv venv
```

Activate it:
- **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
- **Windows (CMD):** `.\venv\Scripts\activate.bat`
- **Mac/Linux:** `source venv/bin/activate`

You should see `(venv)` in your terminal prompt.

### 4.3 Install Backend Dependencies

Create a `backend/requirements.txt`:

```
fastapi==0.115.*
uvicorn[standard]==0.34.*
python-multipart==0.0.*
google-generativeai==0.8.*
PyPDF2==3.0.*
python-pptx==1.0.*
fpdf2==2.8.*
python-docx==1.1.*
pydantic-settings==2.7.*
python-dotenv==1.1.*
```

Install:
```bash
pip install -r requirements.txt
```

### Dependency Breakdown

| Package | Purpose |
|---|---|
| `fastapi` | Web framework for building the API |
| `uvicorn` | ASGI server to run FastAPI |
| `python-multipart` | Required for file upload handling in FastAPI |
| `google-generativeai` | Official Google Gemini SDK |
| `PyPDF2` | Extract text from PDF files |
| `python-pptx` | Extract text from PPTX files |
| `fpdf2` | Generate PDF exports |
| `python-docx` | Generate Word (.docx) exports |
| `pydantic-settings` | Type-safe environment variable management |
| `python-dotenv` | Load `.env` files locally |

### 4.4 Create the Backend Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings / env var management
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── extract.py       # POST /api/extract
│   │   ├── generate.py      # POST /api/generate
│   │   └── export.py        # POST /api/export
│   ├── services/
│   │   ├── __init__.py
│   │   ├── file_parser.py   # PDF/PPTX text extraction logic
│   │   ├── gemini.py        # Gemini API client wrapper
│   │   └── exporter.py      # PDF/Word document generation
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── summary.py       # Prompt template for summaries
│   │   ├── key_terms.py     # Prompt template for key terms
│   │   ├── quiz.py          # Prompt template for quizzes
│   │   └── study_guide.py   # Prompt template for study guides
│   └── schemas/
│       ├── __init__.py
│       └── models.py        # Pydantic request/response models
├── requirements.txt
├── .env.example
├── .env                     # LOCAL ONLY — never commit
└── Dockerfile
```

Create all `__init__.py` files — they can be empty but are required for Python to treat directories as packages.

### 4.5 Create the .env File

Create `backend/.env.example` (committed to Git):
```env
GEMINI_API_KEY=your_api_key_here
ALLOWED_ORIGINS=http://localhost:5173
```

Create `backend/.env` (NOT committed — add to `.gitignore`):
```env
GEMINI_API_KEY=AIzaSy...your_actual_key
ALLOWED_ORIGINS=http://localhost:5173
```

### 4.6 Get Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click **"Get API Key"** in the left sidebar
4. Click **"Create API Key"**
5. Copy the key and paste it into your `backend/.env` file

> **⚠️ Important:** This key is free but has rate limits. Never share it publicly or commit it to Git.

### 4.7 Verify Backend Runs

Create a minimal `backend/app/main.py`:

```python
# Minimal test — replace with full implementation in Phase 2
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
```

Run:
```bash
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/api/health` — you should see `{"status": "ok"}`.

Visit `http://localhost:8000/docs` — you should see FastAPI's auto-generated Swagger UI.

---

## 5. Root .gitignore

Create a `.gitignore` at the project root (`ai-proj-main/.gitignore`):

```gitignore
# Python
backend/venv/
backend/.env
__pycache__/
*.pyc
*.pyo

# Node
frontend/node_modules/
frontend/dist/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local
.env.*.local
```

---

## 6. Development Workflow

### Running Both Servers Locally

You'll need **two terminal windows** running simultaneously:

**Terminal 1 — Backend:**
```bash
cd backend
.\venv\Scripts\Activate.ps1    # Activate virtual environment
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Your setup is working when:
- Frontend is live at `http://localhost:5173`
- Backend is live at `http://localhost:8000`
- Frontend can reach `http://localhost:8000/api/health`

### Testing the Connection

Open your browser's developer console (F12) on the frontend page and run:

```javascript
fetch('http://localhost:8000/api/health')
  .then(r => r.json())
  .then(console.log)
```

If you see `{status: "ok"}`, the connection works. If you get a CORS error, that's expected — we'll fix it in Phase 2.

---

## 7. Phase 1 Completion Checklist

- [ ] Node.js and Python installed and verified
- [ ] Vue.js project scaffolded in `frontend/`
- [ ] All frontend dependencies installed
- [ ] Python virtual environment created in `backend/`
- [ ] All backend dependencies installed
- [ ] Backend project structure created with all directories
- [ ] `.env` file created with Gemini API key
- [ ] `.gitignore` configured
- [ ] Frontend dev server runs at `localhost:5173`
- [ ] Backend dev server runs at `localhost:8000`
- [ ] Health check endpoint returns `{"status": "ok"}`
- [ ] Initial commit pushed to GitHub

---

## 8. Common Issues & Troubleshooting

| Problem | Solution |
|---|---|
| `python` not found | Try `python3` instead; ensure Python is in your PATH |
| `venv` activation fails on Windows | Run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` in PowerShell |
| Port already in use | Kill the process using the port or use a different port (`--port 8001`) |
| `ModuleNotFoundError` | Ensure your virtual environment is activated before installing/running |
| Frontend can't reach backend | CORS not configured yet — that's Phase 2. For now, test backend directly |
