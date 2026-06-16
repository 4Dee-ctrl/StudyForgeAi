# 02 — Backend API Foundation

> **Phase:** 2 of 9
> **Goal:** Build the FastAPI application skeleton with proper CORS configuration, error handling, request validation, and a clean project structure that all future phases will build upon.
> **Estimated Time:** 2–3 hours
> **Depends On:** Phase 1 (Project Setup)

---

## 1. Phase Objectives

By the end of this phase, you will have:

- A running FastAPI application with a modular router structure
- CORS middleware configured for local development and production
- Centralized configuration management using environment variables
- Pydantic schemas for request/response validation
- Global error handling with consistent error response format
- API documentation auto-generated at `/docs`

---

## 2. Configuration Management (`config.py`)

### Requirements

- Load environment variables from `.env` in development
- Use `pydantic-settings` for type-safe configuration
- Fail fast if required variables (like `GEMINI_API_KEY`) are missing

### Settings to Manage

| Variable | Type | Default | Required |
|---|---|---|---|
| `GEMINI_API_KEY` | `str` | — | ✅ Yes |
| `ALLOWED_ORIGINS` | `str` | `http://localhost:5173` | No |
| `MAX_FILE_SIZE_MB` | `int` | `10` | No |
| `MAX_TEXT_LENGTH` | `int` | `50000` | No |
| `GEMINI_MODEL` | `str` | `gemini-2.0-flash` | No |

### Design Notes

- `ALLOWED_ORIGINS` should be a comma-separated string (e.g., `http://localhost:5173,https://myapp.vercel.app`) that gets split into a list
- Create a singleton `Settings` instance that can be imported anywhere
- Use `pydantic-settings`'s `BaseSettings` class with `env_file = ".env"` for automatic `.env` loading

---

## 3. Main Application Entry Point (`main.py`)

### Requirements

- Create the FastAPI app instance with metadata (title, description, version)
- Mount CORS middleware
- Include all routers with `/api` prefix
- Add a root health check endpoint

### FastAPI App Metadata

```
Title: "StudyForge API"
Description: "AI-powered study aid generation API"
Version: "1.0.0"
```

### CORS Middleware Configuration

The CORS middleware must:
- Allow origins from the `ALLOWED_ORIGINS` config
- Allow methods: `GET`, `POST`, `OPTIONS`
- Allow headers: `Content-Type`, `Authorization`
- Allow credentials: `false` (no cookies needed for stateless API)

### Router Mounting

```
/api/health    → health check (defined in main.py)
/api/extract   → extract router
/api/generate  → generate router
/api/export    → export router
```

---

## 4. Pydantic Schemas (`schemas/models.py`)

Define all request and response models using Pydantic v2 for automatic validation.

### Request Models

#### `ExtractRequest` (implicit via file upload)
- No explicit Pydantic model needed — FastAPI handles `UploadFile` directly
- Validation happens in the router (file type, file size)

#### `GenerateRequest`
| Field | Type | Validation |
|---|---|---|
| `text` | `str` | Required, min length 50, max length 50,000 |
| `type` | `str` (enum) | Must be one of: `summary`, `key_terms`, `quiz`, `study_guide` |

#### `ExportRequest`
| Field | Type | Validation |
|---|---|---|
| `content` | `str` | Required, min length 1 |
| `format` | `str` (enum) | Must be one of: `pdf`, `docx` |
| `title` | `str` | Optional, default: "Study Aid", max length 200 |

### Response Models

#### `ExtractResponse`
| Field | Type |
|---|---|
| `text` | `str` |
| `page_count` | `int` (for PDFs) or `slide_count` (for PPTX) |
| `char_count` | `int` |

#### `GenerateResponse`
| Field | Type |
|---|---|
| `type` | `str` |
| `content` | `str` (Markdown-formatted study aid) |
| `token_usage` | `dict` (optional, for debugging) |

#### `ErrorResponse`
| Field | Type |
|---|---|
| `error` | `str` |
| `detail` | `str` |
| `status_code` | `int` |

### Enum Definition

Create a `StudyAidType` string enum:
```
summary
key_terms
quiz
study_guide
```

Create an `ExportFormat` string enum:
```
pdf
docx
```

---

## 5. Router Stubs

In this phase, create the router files with stub implementations that return mock data. The actual logic will be implemented in later phases.

### `routers/extract.py`

- **Endpoint:** `POST /api/extract`
- **Accepts:** `UploadFile` (multipart/form-data)
- **Stub Response:** Return mock extracted text
- **Validation to implement now:**
  - Check file extension is `.pdf` or `.pptx`
  - Check file size ≤ `MAX_FILE_SIZE_MB`
  - Return 400 error for invalid files

### `routers/generate.py`

- **Endpoint:** `POST /api/generate`
- **Accepts:** `GenerateRequest` JSON body
- **Stub Response:** Return a placeholder study aid string
- **Validation:** Handled automatically by Pydantic schema

### `routers/export.py`

- **Endpoint:** `POST /api/export`
- **Accepts:** `ExportRequest` JSON body
- **Stub Response:** Return a dummy PDF/Word file
- **Note:** This endpoint returns a `StreamingResponse` or `FileResponse`, not JSON

---

## 6. Error Handling Strategy

### Global Exception Handler

Register a global exception handler that catches all unhandled exceptions and returns a consistent JSON error response:

```json
{
  "error": "InternalServerError",
  "detail": "An unexpected error occurred. Please try again.",
  "status_code": 500
}
```

### Specific Exception Handlers

| Exception | Status Code | When |
|---|---|---|
| `RequestValidationError` | 422 | Pydantic validation fails |
| `HTTPException` | varies | Explicitly raised in route handlers |
| `FileTooLargeError` (custom) | 413 | Uploaded file exceeds size limit |
| `UnsupportedFileTypeError` (custom) | 415 | File is not PDF/PPTX |
| `GeminiAPIError` (custom) | 502 | Gemini API call fails |
| `RateLimitError` (custom) | 429 | Rate limit exceeded |
| `Exception` (catch-all) | 500 | Unexpected errors |

### Custom Exception Classes

Create custom exception classes in `app/exceptions.py`:

- `FileTooLargeError(detail: str)`
- `UnsupportedFileTypeError(detail: str)`
- `GeminiAPIError(detail: str)`
- `RateLimitError(detail: str)`
- `TextExtractionError(detail: str)`

Each should inherit from a base `StudyForgeError` class.

---

## 7. Request Logging & Middleware

### Request ID Middleware

Add middleware that:
1. Generates a unique request ID (UUID) for each incoming request
2. Attaches it to the response headers as `X-Request-ID`
3. Logs the request method, path, status code, and duration

### Logging Configuration

- Use Python's built-in `logging` module
- Log format: `[timestamp] [level] [request_id] message`
- Log levels:
  - `INFO` — successful requests
  - `WARNING` — rate limits, large files
  - `ERROR` — failed API calls, unhandled exceptions

---

## 8. Rate Limiting (Basic)

For the MVP, implement a **simple in-memory rate limiter**:

- Track requests per IP address using a dictionary
- Limit: 10 requests per minute per IP
- Reset counter every 60 seconds
- Return 429 if limit exceeded

### Why In-Memory?

- No database needed (stateless MVP)
- Good enough for low traffic
- Will be replaced by Redis or a proper rate limiter if the app scales

### Edge Cases

- Rate limiter resets on server restart (acceptable for MVP)
- Behind a proxy (Render), use `X-Forwarded-For` header to get real client IP
- Don't rate-limit the health check endpoint

---

## 9. API Documentation

FastAPI auto-generates OpenAPI documentation. Enhance it by:

- Adding descriptions to all endpoints via docstrings
- Adding example values to Pydantic schemas
- Adding tags to group endpoints: `["Extract", "Generate", "Export", "Health"]`
- The Swagger UI at `/docs` should be a complete, usable reference

---

## 10. Testing the Foundation

### Manual Tests to Run

After completing this phase, verify:

| Test | Method | Expected Result |
|---|---|---|
| Health check | `GET /api/health` | `{"status": "ok"}` |
| Swagger UI loads | Visit `/docs` | Interactive API documentation |
| Valid generate request | `POST /api/generate` with valid body | Mock study aid response |
| Invalid type in generate | `POST /api/generate` with `type: "invalid"` | 422 validation error |
| Missing text field | `POST /api/generate` with no `text` | 422 validation error |
| Text too short | `POST /api/generate` with `text: "hi"` | 422 validation error |
| Upload wrong file type | `POST /api/extract` with `.txt` file | 415 error |
| CORS from localhost | Call from frontend at `:5173` | No CORS error |
| CORS from random origin | Call from different origin | CORS blocked |

### How to Test

Use any of these tools:
- **FastAPI Swagger UI** (`/docs`) — built-in, easiest for beginners
- **curl** — command-line HTTP client
- **Thunder Client** — VS Code extension
- **Browser console** — `fetch()` calls

---

## 11. Phase 2 Completion Checklist

- [ ] `config.py` loads all environment variables with validation
- [ ] `main.py` creates FastAPI app with CORS middleware
- [ ] All three routers created with stub endpoints
- [ ] Pydantic schemas validate all request/response models
- [ ] Custom exception classes created
- [ ] Global error handler returns consistent JSON errors
- [ ] Request logging middleware operational
- [ ] Basic rate limiting works (10 req/min per IP)
- [ ] Swagger UI at `/docs` is complete and accurate
- [ ] File upload validation rejects non-PDF/PPTX files
- [ ] CORS allows requests from `localhost:5173`
- [ ] All manual tests pass
