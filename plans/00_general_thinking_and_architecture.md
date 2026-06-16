# 00 — General Thinking & System Architecture

> **Project:** AI-Powered Micro-SaaS Study Companion
> **Status:** Planning Phase
> **Last Updated:** 2026-05-19

---

## 1. Executive Summary

The **StudyForge** (working title) is an AI-powered web application that helps students transform raw study materials into structured, actionable study aids. Users can paste text or upload documents (PDF/PPTX), and the system leverages Google's Gemini API to generate four distinct outputs:

| Study Aid | Description |
|---|---|
| **Reviewer Summary** | A concise, structured summary of the source material organized by topic |
| **Key Terms** | Extracted vocabulary/concepts with AI-generated definitions |
| **Quiz** | Auto-generated multiple-choice and identification questions with answer keys |
| **Study Guide** | A comprehensive, exam-prep-style guide with headings, bullet points, and mnemonics |

The app is designed as a **stateless MVP** — no user accounts, no database. This dramatically reduces complexity and cost, making it ideal for a solo beginner developer to ship quickly.

---

## 2. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER'S BROWSER                           │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                  Vue.js Frontend (Vercel)                 │  │
│  │                                                           │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐  │  │
│  │  │ Text Input   │  │ File Upload  │  │ Study Aid View  │  │  │
│  │  │ (Paste Area) │  │ (PDF/PPTX)   │  │ (Tabs/Cards)    │  │  │
│  │  └──────┬───────┘  └──────┬───────┘  └────────▲────────┘  │  │
│  │         │                 │                    │            │  │
│  │         └────────┬────────┘                    │            │  │
│  │                  │                             │            │  │
│  │                  ▼                             │            │  │
│  │         ┌────────────────┐            ┌────────┴────────┐  │  │
│  │         │  API Service   │◄──────────►│  State Manager  │  │  │
│  │         │  (Axios/Fetch) │            │  (Pinia Store)  │  │  │
│  │         └────────┬───────┘            └─────────────────┘  │  │
│  │                  │                                         │  │
│  └──────────────────┼─────────────────────────────────────────┘  │
│                     │                                            │
└─────────────────────┼────────────────────────────────────────────┘
                      │  HTTPS (JSON)
                      │  CORS-Protected
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Python Backend (Render)                          │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    FastAPI Application                     │  │
│  │                                                           │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │  │
│  │  │ /api/extract │  │ /api/generate│  │ /api/export    │  │  │
│  │  │ (Upload +    │  │ (AI Study    │  │ (PDF/Word      │  │  │
│  │  │  Parse)      │  │  Aid Gen)    │  │  Download)     │  │  │
│  │  └──────┬───────┘  └──────┬───────┘  └────────────────┘  │  │
│  │         │                 │                                │  │
│  │         ▼                 ▼                                │  │
│  │  ┌──────────────┐  ┌──────────────┐                       │  │
│  │  │ File Parser  │  │ Gemini       │                       │  │
│  │  │ (PyPDF2,     │  │ Prompt       │                       │  │
│  │  │  python-pptx)│  │ Engine       │                       │  │
│  │  └──────────────┘  └──────┬───────┘                       │  │
│  │                           │                                │  │
│  └───────────────────────────┼────────────────────────────────┘  │
│                              │                                   │
└──────────────────────────────┼───────────────────────────────────┘
                               │  HTTPS
                               ▼
                    ┌──────────────────────┐
                    │  Google AI Studio    │
                    │  (Gemini API)        │
                    │  Free Tier           │
                    └──────────────────────┘
```

---

## 3. Backend Language Decision: Python (FastAPI)

Both Laravel (PHP) and Python were considered. **Python with FastAPI is the recommended choice** for this project. Here's why:

| Factor | Python (FastAPI) | Laravel (PHP) |
|---|---|---|
| **Gemini SDK** | First-class `google-generativeai` Python SDK | No official SDK; must use raw HTTP |
| **PDF Parsing** | `PyPDF2`, `pdfplumber` — mature, well-documented | Fewer native options, heavier dependencies |
| **PPTX Parsing** | `python-pptx` — industry standard | No comparable library |
| **Learning Curve** | Minimal boilerplate, beginner-friendly | Full MVC framework — overkill for a stateless API |
| **Render Deployment** | Native Python support, simple `requirements.txt` | Requires PHP buildpack, more config |
| **Performance** | Async-native, excellent for I/O-bound AI calls | Synchronous by default |
| **Export Libraries** | `fpdf2` (PDF), `python-docx` (Word) | Available but less ergonomic |

> **Verdict:** Python + FastAPI is the clear winner for an AI-focused, file-processing, stateless micro-service.

---

## 4. Data Flow — End-to-End Request Lifecycle

### Flow A: Text Paste → Study Aid

```
1. User pastes text into the Vue.js textarea
2. User selects desired study aid type (summary/terms/quiz/guide)
3. Frontend sends POST /api/generate with JSON body:
   { "text": "...", "type": "summary" }
4. Backend validates input (length limits, sanitization)
5. Backend constructs a Gemini prompt using a template for the selected type
6. Backend calls Gemini API with the prompt
7. Gemini returns structured output (Markdown or JSON)
8. Backend parses/validates the AI response
9. Backend returns the study aid as JSON to the frontend
10. Frontend renders the study aid in a formatted card/tab view
```

### Flow B: File Upload → Study Aid

```
1. User uploads a PDF or PPTX file via the file input
2. Frontend sends POST /api/extract as multipart/form-data
3. Backend validates file (type, size ≤ 10MB)
4. Backend extracts text:
   - PDF: PyPDF2 or pdfplumber (page-by-page extraction)
   - PPTX: python-pptx (slide-by-slide text extraction)
5. Backend cleans and normalizes extracted text
6. Backend returns extracted text to frontend as JSON
7. Frontend displays extracted text for user review/editing
8. User confirms and selects study aid type
9. Flow continues as Flow A, Step 3
```

### Flow C: Export Study Aid

```
1. User views a generated study aid
2. User clicks "Export as PDF" or "Export as Word"
3. Frontend sends POST /api/export with:
   { "content": "...", "format": "pdf", "title": "Chapter 5 Summary" }
4. Backend generates the document using fpdf2 or python-docx
5. Backend returns the file as a binary download (Content-Disposition: attachment)
6. Browser triggers file download
```

---

## 5. API Endpoint Summary

| Method | Endpoint | Purpose | Input | Output |
|---|---|---|---|---|
| `GET` | `/api/health` | Health check | None | `{ "status": "ok" }` |
| `POST` | `/api/extract` | Extract text from uploaded file | `multipart/form-data` (file) | `{ "text": "..." }` |
| `POST` | `/api/generate` | Generate a study aid from text | `{ "text", "type" }` | `{ "type", "content" }` |
| `POST` | `/api/export` | Export study aid as PDF/Word | `{ "content", "format", "title" }` | Binary file download |

---

## 6. Gemini API — Free Tier Constraints

Understanding the free tier is **critical** to avoid unexpected costs.

### Current Free Tier Limits (Google AI Studio — as of 2026)

| Parameter | Limit |
|---|---|
| **Model** | `gemini-2.0-flash` (recommended for free tier) |
| **Requests per Minute (RPM)** | 15 RPM |
| **Tokens per Minute (TPM)** | 1,000,000 TPM |
| **Requests per Day (RPD)** | 1,500 RPD |
| **Max Input Tokens** | ~1,048,576 tokens (1M context window) |

### Implications for Our App

- **Rate Limiting:** We must implement client-side and server-side rate limiting. If 15+ users hit "Generate" simultaneously, requests will fail. We'll add retry logic with exponential backoff.
- **Token Budget:** A typical college textbook chapter is ~5,000–15,000 tokens. The free tier can handle this easily per-request, but we should still truncate excessively long inputs (~50,000 char limit).
- **Model Selection:** Use `gemini-2.0-flash` — it's fast, free, and capable enough for summarization/quiz generation. Avoid `gemini-2.0-pro` unless the user explicitly upgrades.
- **No Streaming (MVP):** For simplicity, we'll use synchronous (non-streaming) requests in the MVP. Streaming can be added later for better UX.

---

## 7. Project Structure (Monorepo)

```
ai-proj-main/
├── plans/                    # This planning documentation
│   ├── 00_general_thinking_and_architecture.md
│   ├── 01_project_setup_and_dev_environment.md
│   ├── ...
│
├── frontend/                 # Vue.js application
│   ├── public/
│   ├── src/
│   │   ├── assets/           # Images, fonts, global CSS
│   │   ├── components/       # Reusable UI components
│   │   ├── views/            # Page-level components
│   │   ├── stores/           # Pinia state management
│   │   ├── services/         # API client (Axios wrapper)
│   │   ├── router/           # Vue Router config
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
│
├── backend/                  # Python FastAPI application
│   ├── app/
│   │   ├── main.py           # FastAPI app entry point
│   │   ├── routers/          # Route handlers (extract, generate, export)
│   │   ├── services/         # Business logic (parser, gemini, exporter)
│   │   ├── prompts/          # Prompt templates (Jinja2 or string templates)
│   │   ├── schemas/          # Pydantic models for request/response validation
│   │   └── config.py         # Environment variable management
│   ├── requirements.txt
│   ├── Dockerfile            # For Render deployment
│   └── .env.example
│
└── README.md
```

---

## 8. Deployment Roadmap (Beginner-Friendly)

### 8.1 Understanding the Architecture

Your app has **two separate deployments**:

```
┌──────────────────┐         ┌──────────────────┐
│    VERCEL         │  HTTPS  │    RENDER         │
│    (Frontend)     │────────►│    (Backend)      │
│                   │         │                   │
│  Your Vue.js app  │         │  Your Python API  │
│  Static files     │         │  Running server   │
│  (HTML/CSS/JS)    │         │  (FastAPI + Uvicorn)│
└──────────────────┘         └────────┬──────────┘
                                      │ HTTPS
                                      ▼
                             ┌──────────────────┐
                             │ Google AI Studio  │
                             │ (Gemini API)      │
                             └──────────────────┘
```

### 8.2 Vercel (Frontend)

**What it does:** Vercel hosts your compiled Vue.js app as static files. When users visit your URL, Vercel serves the HTML/CSS/JS.

**How to deploy:**
1. Push your `frontend/` code to a GitHub repository
2. Connect the repo to Vercel (vercel.com → Import Project)
3. Set the **Root Directory** to `frontend/`
4. Set the **Build Command** to `npm run build`
5. Set the **Output Directory** to `dist/`
6. Add environment variables:
   - `VITE_API_BASE_URL` = `https://your-backend.onrender.com`
7. Vercel auto-deploys on every `git push`

**GitHub Student Developer Pack:** Vercel's free Hobby tier is already generous. The Student Pack may offer additional benefits — check your dashboard.

### 8.3 Render (Backend)

**What it does:** Render runs your Python server 24/7. It listens for HTTP requests from your frontend.

**How to deploy:**
1. Push your `backend/` code to a GitHub repository (same repo, or separate)
2. Go to render.com → New Web Service
3. Connect your GitHub repo
4. Set the **Root Directory** to `backend/`
5. Set the **Build Command** to `pip install -r requirements.txt`
6. Set the **Start Command** to `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
7. Add environment variables:
   - `GEMINI_API_KEY` = your API key from Google AI Studio
   - `ALLOWED_ORIGINS` = `https://your-frontend.vercel.app`
8. Select the **Free** tier

**⚠️ Free Tier Caveat:** Render's free tier spins down after 15 minutes of inactivity. The first request after a cold start takes ~30–60 seconds. This is expected — add a loading state in your frontend to handle it gracefully.

### 8.4 CORS (Cross-Origin Resource Sharing)

**What is CORS?** When your frontend (on `vercel.app`) tries to call your backend (on `onrender.com`), the browser blocks it by default because they're on different domains. CORS headers tell the browser "it's okay, I trust this origin."

**How to configure (FastAPI):**
- Use FastAPI's `CORSMiddleware`
- Allow only your Vercel domain in production
- Allow `http://localhost:5173` during development
- Never use `allow_origins=["*"]` in production

### 8.5 Securing API Keys

**The #1 Rule: NEVER put API keys in frontend code.**

Your Gemini API key lives ONLY on the backend:
- Stored as an **environment variable** on Render (not in code)
- Loaded via Python's `os.environ` or a config library like `pydantic-settings`
- The `.env` file is in `.gitignore` — never committed to Git
- The frontend never sees or handles the API key

```
Frontend (public, visible to anyone)
    │
    │  "Hey backend, generate a summary for this text"
    │  (No API key in this request)
    ▼
Backend (private, server-side only)
    │
    │  "Hey Gemini, here's the text + my API key"
    │  (API key is server-side only)
    ▼
Gemini API
```

---

## 9. Development Phase Overview

| Phase | Document | Focus |
|---|---|---|
| **Phase 1** | `01_project_setup_and_dev_environment.md` | Scaffold both projects, install dependencies, configure dev tooling |
| **Phase 2** | `02_backend_api_foundation.md` | Build FastAPI skeleton with health check, CORS, error handling |
| **Phase 3** | `03_file_upload_and_text_extraction.md` | Implement file upload, PDF/PPTX parsing, text cleaning |
| **Phase 4** | `04_gemini_integration_and_prompt_engineering.md` | Connect to Gemini, design prompt templates, parse AI responses |
| **Phase 5** | `05_frontend_ui_and_state_management.md` | Build Vue.js interface: input, navigation, state management |
| **Phase 6** | `06_study_aids_display_and_interaction.md` | Render all four study aid types with rich formatting |
| **Phase 7** | `07_export_to_pdf_and_word.md` | Implement document export functionality |
| **Phase 8** | `08_deployment_and_production_checklist.md` | Deploy to Vercel + Render, final production hardening |
| **Phase 9** | `09_future_roadmap_and_scaling.md` | Auth, database, history, payments, and beyond |

---

## 10. Key Architectural Decisions Log

| Decision | Choice | Rationale |
|---|---|---|
| Backend framework | FastAPI (Python) | Native Gemini SDK, excellent file parsing libraries, async support |
| State management | Pinia | Official Vue.js recommendation, simpler than Vuex |
| HTTP client | Axios | Interceptors for error handling, request/response transforms |
| Styling approach | TBD (Phase 5) | Will decide between Vuetify, PrimeVue, or custom CSS |
| Database | None (MVP) | Stateless MVP reduces complexity; add Supabase/Postgres later |
| Authentication | None (MVP) | No user accounts in v1; add OAuth later |
| File size limit | 10 MB | Prevents abuse, stays within Render free tier memory |
| Text length limit | 50,000 characters | Keeps Gemini token usage reasonable on free tier |
| AI model | `gemini-2.0-flash` | Best balance of speed, capability, and free tier availability |
