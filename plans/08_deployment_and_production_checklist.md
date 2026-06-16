# 08 — Deployment & Production Checklist

> **Phase:** 8 of 9
> **Goal:** Deploy the frontend to Vercel and the backend to Render, configure environment variables, set up CORS for production, and verify the full application works end-to-end in production.
> **Estimated Time:** 2–4 hours
> **Depends On:** All previous phases (app must be complete and working locally)

---

## 1. Phase Objectives

By the end of this phase:

- Frontend is live on Vercel at a public URL
- Backend is live on Render at a public URL
- CORS is configured to allow only the Vercel domain
- API key is securely stored as a Render environment variable
- The full app works end-to-end in production
- Basic monitoring and error awareness is in place

---

## 2. Pre-Deployment Checklist

Before deploying, verify everything works locally:

- [ ] Frontend runs without errors (`npm run dev`)
- [ ] Backend runs without errors (`uvicorn app.main:app --reload`)
- [ ] All four study aid types generate correctly
- [ ] File upload works (PDF and PPTX)
- [ ] Export to PDF and Word works
- [ ] No console errors in the browser
- [ ] No hardcoded `localhost` URLs (use environment variables)
- [ ] `.env` is in `.gitignore`
- [ ] `.env.example` exists with placeholder values
- [ ] `requirements.txt` is up to date
- [ ] `package.json` has all dependencies
- [ ] Code is committed and pushed to GitHub

---

## 3. Backend Deployment — Render

### 3.1 Prepare the Backend for Render

#### Dockerfile (Recommended Approach)

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

> **Note:** Render will automatically detect the Dockerfile. Alternatively, you can use a native Python environment (no Docker) by specifying the build and start commands directly.

#### Alternative: No Docker

If you prefer not to use Docker:
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Render injects `$PORT` automatically

### 3.2 Step-by-Step Render Deployment

1. **Go to [render.com](https://render.com)** and sign in (use your GitHub account)
2. **Click "New +"** → **"Web Service"**
3. **Connect your GitHub repository**
   - Grant Render access to your repo
   - Select the repository
4. **Configure the service:**

| Setting | Value |
|---|---|
| **Name** | `studyforge-api` (or your choice) |
| **Region** | Choose closest to your users (e.g., Oregon for US) |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` (or `Docker` if using Dockerfile) |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | **Free** |

5. **Add Environment Variables:**

| Key | Value |
|---|---|
| `GEMINI_API_KEY` | `AIzaSy...` (your actual key) |
| `ALLOWED_ORIGINS` | `https://your-app.vercel.app` (set after Vercel deploy) |
| `PYTHON_VERSION` | `3.11.0` |

6. **Click "Create Web Service"**
7. **Wait for build** (2–5 minutes)
8. **Verify:** Visit `https://studyforge-api.onrender.com/api/health`

### 3.3 Render Free Tier Limitations

| Limitation | Impact | Mitigation |
|---|---|---|
| **Spins down after 15 min idle** | First request after idle takes 30–60s | Add loading screen in frontend; consider a keep-alive ping |
| **750 free hours/month** | Enough for a single service 24/7 | No action needed |
| **512 MB RAM** | May struggle with very large PDFs | Enforce 10 MB file size limit |
| **0.1 CPU** | Slower processing | Acceptable for MVP traffic levels |

### 3.4 Cold Start Mitigation

The free tier's cold start is the biggest UX issue. Mitigation strategies:

**Option A: Loading Screen (Required)**
- When the frontend first loads, ping `/api/health`
- If it takes > 5 seconds, show a message: "Waking up the server... This takes about 30 seconds on the first visit."
- Retry the health check every 5 seconds until it succeeds
- Once healthy, enable the UI

**Option B: Keep-Alive Cron (Optional)**
- Use a free cron service (like cron-job.org) to ping `/api/health` every 14 minutes
- This prevents the server from spinning down
- ⚠️ Uses some of your 750 free hours — still enough for the month

---

## 4. Frontend Deployment — Vercel

### 4.1 Prepare the Frontend for Vercel

Ensure `frontend/package.json` has a build script:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

Ensure `vite.config.js` doesn't have hardcoded paths.

### 4.2 Step-by-Step Vercel Deployment

1. **Go to [vercel.com](https://vercel.com)** and sign in with GitHub
2. **Click "Add New..."** → **"Project"**
3. **Import your GitHub repository**
4. **Configure the project:**

| Setting | Value |
|---|---|
| **Project Name** | `studyforge` (or your choice) |
| **Framework Preset** | Vite (auto-detected) |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |

5. **Add Environment Variables:**

| Key | Value |
|---|---|
| `VITE_API_BASE_URL` | `https://studyforge-api.onrender.com` |

6. **Click "Deploy"**
7. **Wait for build** (1–2 minutes)
8. **Verify:** Visit your Vercel URL (e.g., `https://studyforge.vercel.app`)

### 4.3 Update CORS on Render

Now that you have the Vercel URL, go back to Render:

1. Go to your web service → Environment
2. Update `ALLOWED_ORIGINS` to: `https://studyforge.vercel.app`
3. If you want to allow both production and local development:
   `ALLOWED_ORIGINS=https://studyforge.vercel.app,http://localhost:5173`
4. Render will auto-redeploy

### 4.4 Vercel Configuration (Optional)

Create `frontend/vercel.json` for any special configuration:

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

This catch-all rewrite ensures Vue Router works correctly (prevents 404 on direct URL access to routes like `/results`).

---

## 5. Production Environment Variables — Complete List

### Render (Backend)

| Variable | Value | Notes |
|---|---|---|
| `GEMINI_API_KEY` | `AIzaSy...` | Never expose this |
| `ALLOWED_ORIGINS` | `https://studyforge.vercel.app` | Comma-separated if multiple |
| `PYTHON_VERSION` | `3.11.0` | Tells Render which Python to use |
| `MAX_FILE_SIZE_MB` | `10` | Optional override |
| `MAX_TEXT_LENGTH` | `50000` | Optional override |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Optional override |

### Vercel (Frontend)

| Variable | Value | Notes |
|---|---|---|
| `VITE_API_BASE_URL` | `https://studyforge-api.onrender.com` | Must include `VITE_` prefix |

---

## 6. Production CORS Configuration

### What to Allow

```python
# In production
allowed_origins = [
    "https://studyforge.vercel.app",    # Your Vercel domain
    "https://studyforge-*.vercel.app",  # Preview deployments (optional)
]

# In development
allowed_origins = [
    "http://localhost:5173",            # Vite dev server
    "http://localhost:4173",            # Vite preview server
]
```

### What to Block

- `*` (wildcard) — Never use in production
- HTTP origins (non-HTTPS) in production
- Unknown domains

### CORS Headers to Set

```
Access-Control-Allow-Origin: https://studyforge.vercel.app
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
Access-Control-Max-Age: 3600
```

---

## 7. Security Hardening for Production

### 7.1 API Key Security

- [x] API key stored as environment variable on Render
- [ ] API key not in any committed file
- [ ] `.env.example` has placeholder, not real key
- [ ] Git history doesn't contain the key (if it was ever committed, rotate the key)

### 7.2 Input Validation

- [ ] All inputs validated with Pydantic schemas
- [ ] File size limit enforced server-side
- [ ] Text length limit enforced server-side
- [ ] File type validated by extension AND MIME type

### 7.3 Rate Limiting

- [ ] In-memory rate limiter active (10 req/min per IP)
- [ ] Consider adding Render's IP allowlisting if available

### 7.4 Headers

Add security headers to FastAPI responses:

| Header | Value | Purpose |
|---|---|---|
| `X-Content-Type-Options` | `nosniff` | Prevent MIME type sniffing |
| `X-Frame-Options` | `DENY` | Prevent clickjacking |
| `Strict-Transport-Security` | `max-age=31536000` | Enforce HTTPS |
| `X-Request-ID` | UUID | Request tracing |

### 7.5 Error Messages

- Never expose stack traces in production
- Never expose internal paths or config values
- Use generic messages for 500 errors
- Log detailed errors server-side only

---

## 8. Post-Deployment Verification

### Smoke Test Checklist

Run through these tests on the live production URLs:

| # | Test | Expected Result |
|---|---|---|
| 1 | Visit Vercel URL | Frontend loads without errors |
| 2 | Visit Render URL `/api/health` | `{"status": "ok"}` |
| 3 | Paste text and generate summary | Study aid appears |
| 4 | Generate all four types | All tabs populate |
| 5 | Upload a small PDF | Text extracted, study aids generated |
| 6 | Upload a PPTX | Text extracted, study aids generated |
| 7 | Export as PDF | PDF downloads and opens correctly |
| 8 | Export as DOCX | Word doc downloads and opens correctly |
| 9 | Upload oversized file | Error message displayed |
| 10 | Upload wrong file type | Error message displayed |
| 11 | Check mobile layout | Responsive, usable on phone |
| 12 | Check CORS | No CORS errors in console |
| 13 | Wait 20 min, then visit | Cold start recovers gracefully |

---

## 9. Continuous Deployment

### Automatic Deploys

Both Vercel and Render support automatic deployment on `git push`:

```
git push origin main
    │
    ├──► Vercel: Auto-builds and deploys frontend (< 1 min)
    │
    └──► Render: Auto-builds and deploys backend (2–5 min)
```

### Preview Deployments (Vercel)

Vercel creates a unique preview URL for every pull request:
- Useful for testing frontend changes before merging
- Each PR gets `https://studyforge-<hash>.vercel.app`

### Manual Deploys (Render)

If auto-deploy is disabled, trigger manually:
- Render dashboard → Manual Deploy → "Deploy latest commit"

---

## 10. Monitoring & Logging

### Render Logs

- View live logs: Render dashboard → your service → Logs
- Filter by time, search for errors
- Logs are retained for 7 days on the free tier

### What to Monitor

| Metric | How | Alert Threshold |
|---|---|---|
| Server uptime | Render health checks | Down > 5 min |
| API errors (5xx) | Log monitoring | > 5 per hour |
| Gemini rate limits | Log `429` responses | > 10 per day |
| Response times | Log request duration | > 30s average |
| Daily API usage | Internal counter | > 1,000 requests |

### Free Monitoring Tools

- **UptimeRobot** (free tier): Ping your health endpoint every 5 minutes, email alerts on downtime
- **Render built-in**: Basic metrics in the dashboard
- **Vercel Analytics**: Basic traffic analytics (free tier)

---

## 11. Custom Domain (Optional)

If you have a custom domain:

### Vercel Custom Domain
1. Vercel dashboard → Settings → Domains
2. Add your domain (e.g., `studyforge.com`)
3. Add DNS records as instructed by Vercel

### Render Custom Domain
1. Render dashboard → your service → Settings → Custom Domains
2. Add your domain (e.g., `api.studyforge.com`)
3. Add DNS records as instructed by Render

### Update CORS
If using custom domains, update `ALLOWED_ORIGINS` to include the custom domain.

---

## 12. Phase 8 Completion Checklist

- [ ] Backend deployed to Render and accessible
- [ ] Frontend deployed to Vercel and accessible
- [ ] `VITE_API_BASE_URL` points to Render URL
- [ ] `ALLOWED_ORIGINS` includes Vercel URL
- [ ] CORS working correctly (no browser errors)
- [ ] Gemini API key secure in Render env vars
- [ ] Health check returns 200
- [ ] Full smoke test passed (all 13 tests)
- [ ] Cold start handled gracefully in frontend
- [ ] Security headers present in responses
- [ ] Error messages are user-friendly (no stack traces)
- [ ] Auto-deploy working on git push
- [ ] Uptime monitoring configured (optional but recommended)
- [ ] Vue Router works on direct URL access (vercel.json rewrite)
- [ ] README.md updated with live URLs
