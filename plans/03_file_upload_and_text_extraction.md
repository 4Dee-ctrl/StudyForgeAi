# 03 — File Upload & Text Extraction

> **Phase:** 3 of 9
> **Goal:** Implement the complete file processing pipeline — accept PDF and PPTX uploads, extract text content, clean and normalize the output, and return it to the frontend for review.
> **Estimated Time:** 3–4 hours
> **Depends On:** Phase 2 (Backend API Foundation)

---

## 1. Phase Objectives

By the end of this phase, the `/api/extract` endpoint will:

- Accept PDF and PPTX file uploads via multipart/form-data
- Validate file type and size server-side
- Extract all readable text from the document
- Clean and normalize extracted text (remove artifacts, fix whitespace)
- Return structured JSON with the extracted text and metadata

---

## 2. File Upload Endpoint — Detailed Specification

### `POST /api/extract`

**Request:**
- Content-Type: `multipart/form-data`
- Body: Single file field named `file`
- Max file size: 10 MB (configurable via `MAX_FILE_SIZE_MB`)

**Response (Success — 200):**
```json
{
  "text": "Extracted and cleaned text content...",
  "metadata": {
    "filename": "chapter5.pdf",
    "file_type": "pdf",
    "page_count": 12,
    "char_count": 15432,
    "word_count": 2847
  }
}
```

**Response (Error — 415):**
```json
{
  "error": "UnsupportedFileType",
  "detail": "Only PDF and PPTX files are supported. Received: .docx"
}
```

**Response (Error — 413):**
```json
{
  "error": "FileTooLarge",
  "detail": "File size (15.2 MB) exceeds the maximum allowed size (10 MB)."
}
```

---

## 3. File Validation Logic

### Step 1: Extension Check

Check the file extension (case-insensitive):
- `.pdf` → route to PDF parser
- `.pptx` → route to PPTX parser
- Anything else → return 415 error

### Step 2: MIME Type Check (Defense in Depth)

Don't trust the extension alone. Verify the MIME type from the upload:

| Extension | Expected MIME Type |
|---|---|
| `.pdf` | `application/pdf` |
| `.pptx` | `application/vnd.openxmlformats-officedocument.presentationml.presentation` |

If the MIME type doesn't match the extension, reject with a 415 error. This prevents users from renaming a `.exe` to `.pdf`.

### Step 3: File Size Check

- Read the file into memory (or use a temporary file for large files)
- Check size in bytes against `MAX_FILE_SIZE_MB * 1024 * 1024`
- If exceeded, return 413 error with the actual file size in the message

### Step 4: Content Validation

- After extraction, check if the extracted text is empty or near-empty
- If fewer than 50 characters were extracted, return a warning:
  ```json
  {
    "text": "",
    "metadata": { ... },
    "warning": "Very little text was extracted. The file may contain mostly images or scanned content."
  }
  ```

---

## 4. PDF Text Extraction

### Library: PyPDF2

PyPDF2 is the recommended library for text extraction from PDFs.

### Extraction Strategy

```
For each page in the PDF:
    1. Extract text using page.extract_text()
    2. If text is empty/whitespace, skip (likely an image-only page)
    3. Append extracted text with a page separator
    4. Track page numbers for metadata
```

### Key Considerations

| Scenario | Handling |
|---|---|
| **Normal text PDF** | Direct extraction works well |
| **Scanned PDF (images)** | PyPDF2 cannot OCR — extraction returns empty text. Return a warning to the user |
| **PDF with tables** | Text extraction may jumble table data. Accept this limitation for MVP |
| **PDF with columns** | Two-column layouts may interleave text. Accept for MVP |
| **Encrypted/password-protected PDF** | PyPDF2 will raise an exception. Catch and return a clear error |
| **Corrupted PDF** | Catch `PdfReadError` and return error |

### Page Separator Format

Use a consistent separator between pages to help Gemini understand document structure:

```
--- Page 1 ---
[text content]

--- Page 2 ---
[text content]
```

### Error Handling

| Exception | User-Facing Message |
|---|---|
| `PdfReadError` | "The PDF file appears to be corrupted or invalid." |
| `FileDecryptionError` | "This PDF is password-protected. Please upload an unprotected version." |
| `Exception` (generic) | "An error occurred while processing the PDF. Please try a different file." |

---

## 5. PPTX Text Extraction

### Library: python-pptx

### Extraction Strategy

```
For each slide in the presentation:
    1. Iterate over all shapes on the slide
    2. For each shape that has a text_frame:
        a. Extract all text from all paragraphs
        b. Preserve paragraph breaks
    3. Also check for text in tables (cells)
    4. Also check for text in group shapes (recursive)
    5. Append with slide separator
    6. Track slide numbers for metadata
```

### Shape Types to Extract Text From

| Shape Type | How to Access Text |
|---|---|
| **Text boxes** | `shape.text_frame.paragraphs` |
| **Titles** | `slide.shapes.title.text` |
| **Tables** | `shape.table.cell(row, col).text` |
| **Group shapes** | Recursively iterate `shape.shapes` |
| **Notes** | `slide.notes_slide.notes_text_frame` (consider including as supplementary) |

### Slide Separator Format

```
--- Slide 1 ---
[Title]
[Body text]

--- Slide 2 ---
[Title]
[Body text]
```

### What to Ignore

- **Images:** Cannot extract text from embedded images (no OCR)
- **Charts:** Chart data is complex to extract; skip for MVP
- **SmartArt:** Usually extractable as text shapes
- **Animations/transitions:** Not relevant to text content

### Error Handling

| Exception | User-Facing Message |
|---|---|
| `PackageNotFoundError` | "The PPTX file appears to be corrupted or invalid." |
| `ValueError` | "Could not parse the presentation file." |
| `Exception` (generic) | "An error occurred while processing the PPTX. Please try a different file." |

---

## 6. Text Cleaning & Normalization

After extraction, the raw text needs cleaning. Create a `clean_text()` utility function.

### Cleaning Steps (In Order)

```
1. Replace multiple consecutive newlines with double newline (paragraph break)
2. Replace multiple consecutive spaces with single space
3. Remove null bytes and control characters (except \n and \t)
4. Strip leading/trailing whitespace from each line
5. Remove lines that are purely page numbers (e.g., "12", "- 12 -", "Page 12")
6. Remove lines that are purely header/footer artifacts (repeated short strings)
7. Normalize unicode characters (NFKC normalization)
8. Collapse excessive whitespace between words
9. Ensure final text doesn't exceed MAX_TEXT_LENGTH (truncate with warning)
```

### Truncation Behavior

If extracted text exceeds `MAX_TEXT_LENGTH` (default 50,000 chars):
- Truncate at the nearest paragraph break before the limit
- Add a note: `"\n\n[Note: Text was truncated due to length. Only the first ~50,000 characters were included.]"`
- Include `truncated: true` in the response metadata

---

## 7. File Parser Service Architecture

### `services/file_parser.py`

Design the file parser as a service with a clean interface:

```
FileParser
├── parse(file_bytes, filename) → ExtractResult
│   ├── _detect_file_type(filename) → "pdf" | "pptx"
│   ├── _parse_pdf(file_bytes) → RawText
│   ├── _parse_pptx(file_bytes) → RawText
│   └── _clean_text(raw_text) → CleanText
```

### `ExtractResult` Data Structure

```
ExtractResult:
    text: str              # Cleaned, normalized text
    filename: str          # Original filename
    file_type: str         # "pdf" or "pptx"
    page_count: int        # Number of pages/slides
    char_count: int        # Length of cleaned text
    word_count: int        # Approximate word count
    truncated: bool        # Whether text was truncated
    warning: str | None    # Any warnings (e.g., low text content)
```

---

## 8. Memory Management

### The Problem

File uploads can consume significant memory. A 10 MB PDF might expand to 50+ MB of text in memory during processing.

### Solutions

1. **Don't store files permanently.** Process in memory, extract text, then discard the file bytes immediately.
2. **Use `BytesIO` streams** instead of writing to disk. This avoids filesystem permissions issues on Render.
3. **Limit concurrent uploads.** The basic rate limiter from Phase 2 helps, but consider adding a semaphore for the extract endpoint specifically (max 3 concurrent extractions).
4. **Clean up aggressively.** After extraction, explicitly `del` large byte arrays and call the garbage collector if needed.

### File Processing Flow

```
1. Receive UploadFile from FastAPI
2. Read file.read() into bytes (in memory)
3. Validate size
4. Pass bytes to parser
5. Parser creates BytesIO stream
6. Extract text
7. Close BytesIO stream
8. Clean text
9. Return result (only the text string, not the file bytes)
10. File bytes are garbage collected
```

---

## 9. Edge Cases & Error Scenarios

| Scenario | Expected Behavior |
|---|---|
| Empty PDF (0 pages) | Return error: "The PDF file contains no pages." |
| PDF with only images | Return extracted text (empty or near-empty) + warning |
| PPTX with no text slides | Return warning about minimal content |
| File is 0 bytes | Return error: "The uploaded file is empty." |
| File name has special characters | Sanitize filename before logging; don't use it for file paths |
| User uploads PPTX with `.ppt` extension | Reject — `.ppt` is the legacy format and not supported |
| Concurrent uploads from same user | Rate limiter handles this (Phase 2) |
| Server runs out of memory | The 10 MB limit prevents catastrophic OOM, but monitor |

---

## 10. Alternative Approach: Client-Side Text Paste

In addition to file upload, users can paste text directly. This path is simpler:

```
1. User pastes text into frontend textarea
2. Frontend sends POST /api/generate directly (skip /api/extract)
3. Text validation happens via Pydantic schema (min/max length)
4. No file parsing needed
```

This means the `/api/generate` endpoint must accept raw text regardless of whether it came from a file upload or a paste. The frontend decides which flow to use.

---

## 11. Phase 3 Completion Checklist

- [ ] PDF text extraction working with PyPDF2
- [ ] PPTX text extraction working with python-pptx
- [ ] File type validation (extension + MIME type)
- [ ] File size validation with clear error messages
- [ ] Text cleaning and normalization pipeline
- [ ] Page/slide separators in extracted text
- [ ] Truncation logic for long documents
- [ ] Warning for low-text-content files (scanned PDFs, image-heavy PPTX)
- [ ] Proper error handling for corrupted/encrypted files
- [ ] Memory cleanup after extraction
- [ ] Metadata included in response (page count, word count, etc.)
- [ ] Tested with at least 3 different PDFs and 3 different PPTX files
- [ ] Edge cases tested (empty file, wrong extension, oversized file)
