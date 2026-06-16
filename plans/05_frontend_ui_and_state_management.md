# 05 — Frontend UI & State Management

> **Phase:** 5 of 9
> **Goal:** Build the complete Vue.js user interface — input forms, navigation, state management with Pinia, API integration with Axios, and the overall application shell.
> **Estimated Time:** 6–8 hours
> **Depends On:** Phase 2 (Backend API), Phase 4 (Generate endpoint working)

---

## 1. Phase Objectives

By the end of this phase:

- The Vue.js app has a polished, professional UI
- Users can paste text or upload PDF/PPTX files
- The app communicates with the backend via Axios
- Pinia stores manage application state cleanly
- Loading states, error messages, and transitions are handled
- The UI is responsive (mobile + desktop)

---

## 2. Application Pages & Routing

### Page Structure

The app is simple enough for a single-page layout with sections, but we'll use Vue Router for clean URL management and potential future expansion.

| Route | Component | Purpose |
|---|---|---|
| `/` | `HomeView` | Landing / input page — paste text or upload file |
| `/results` | `ResultsView` | Display generated study aids with tabs |
| `/about` | `AboutView` | Simple about page (optional, low priority) |

### Navigation Flow

```
HomeView (Input)
    │
    │  User pastes text or uploads file
    │  User clicks "Generate Study Aids"
    │
    ▼
ResultsView (Output)
    │
    │  Tabs: Summary | Key Terms | Quiz | Study Guide
    │  Each tab triggers a separate API call (or all at once)
    │  Export buttons on each tab
    │
    │  "Start Over" button → back to HomeView
    ▼
HomeView (Input) — fresh state
```

---

## 3. Component Architecture

### Component Tree

```
App.vue
├── AppHeader.vue          # Logo, navigation, branding
├── <router-view>
│   ├── HomeView.vue       # Input page
│   │   ├── TextInput.vue      # Textarea for pasting text
│   │   ├── FileUpload.vue     # Drag-and-drop file upload zone
│   │   └── GenerateButton.vue # Submit button with loading state
│   │
│   └── ResultsView.vue   # Results page
│       ├── StudyAidTabs.vue   # Tab navigation (Summary, Key Terms, Quiz, Guide)
│       ├── StudyAidContent.vue # Rendered Markdown content
│       ├── ExportBar.vue      # Export as PDF/Word buttons
│       └── SourcePreview.vue  # Collapsible preview of original text
│
└── AppFooter.vue          # Credits, links
```

### Shared/Reusable Components

```
components/
├── ui/
│   ├── LoadingSpinner.vue    # Reusable loading indicator
│   ├── ErrorAlert.vue        # Error message display
│   ├── SuccessToast.vue      # Success notification
│   └── MarkdownRenderer.vue  # Renders Markdown strings as HTML
```

---

## 4. HomeView — Input Page Design

### Layout

```
┌──────────────────────────────────────────────┐
│                  AppHeader                    │
│           StudyForge ✦ AI Study Companion     │
├──────────────────────────────────────────────┤
│                                              │
│     ┌────────────────────────────────┐       │
│     │     Hero Section               │       │
│     │  "Transform your notes into    │       │
│     │   powerful study aids"         │       │
│     └────────────────────────────────┘       │
│                                              │
│     ┌─────────────┐  ┌──────────────┐       │
│     │  📝 Paste   │  │  📁 Upload   │       │
│     │   Text      │  │   File       │       │
│     │  (Tab)      │  │  (Tab)       │       │
│     ├─────────────┴──┴──────────────┤       │
│     │                                │       │
│     │  [Textarea / Upload Zone]      │       │
│     │                                │       │
│     │  Character count: 0 / 50,000   │       │
│     │                                │       │
│     └────────────────────────────────┘       │
│                                              │
│     ┌────────────────────────────────┐       │
│     │  Select Study Aid Types:       │       │
│     │  ☑ Summary  ☑ Key Terms       │       │
│     │  ☑ Quiz     ☑ Study Guide     │       │
│     └────────────────────────────────┘       │
│                                              │
│     ┌────────────────────────────────┐       │
│     │   ✨ Generate Study Aids       │       │
│     │   (Primary CTA Button)        │       │
│     └────────────────────────────────┘       │
│                                              │
├──────────────────────────────────────────────┤
│                 AppFooter                     │
└──────────────────────────────────────────────┘
```

### TextInput Component Requirements

- Large, resizable textarea
- Placeholder text with usage instructions
- Live character counter: `{current} / 50,000`
- Visual warning when approaching limit (counter turns orange/red)
- Minimum 50 characters required to enable Generate button
- Clear button to reset textarea

### FileUpload Component Requirements

- Drag-and-drop zone with visual feedback
- Click to browse files
- Accept only `.pdf` and `.pptx` files (set `accept` attribute)
- Show selected filename after selection
- Show file size
- Upload progress indicator
- After upload, display extracted text in the textarea (switches to text tab)
- Error display for rejected files (wrong type, too large)

### Study Aid Type Selection

- Checkboxes for each type: Summary, Key Terms, Quiz, Study Guide
- All checked by default
- At least one must be checked to enable Generate button
- Visual indication of selected types

### Generate Button

- Disabled until valid input exists (50+ chars, at least 1 type selected)
- Loading state with spinner and "Generating..." text
- Animated transition when generating
- On success: navigate to `/results`
- On error: show ErrorAlert with message

---

## 5. ResultsView — Output Page Design

### Layout

```
┌──────────────────────────────────────────────┐
│                  AppHeader                    │
├──────────────────────────────────────────────┤
│                                              │
│  ← Back to Input    [Source Preview ▼]       │
│                                              │
│  ┌──────────────────────────────────────┐    │
│  │ Summary │ Key Terms │ Quiz │ Guide   │    │
│  ├──────────────────────────────────────┤    │
│  │                                      │    │
│  │   [Rendered Markdown Content]        │    │
│  │                                      │    │
│  │   # Summary: Introduction to ML      │    │
│  │                                      │    │
│  │   ## What is Machine Learning?       │    │
│  │   - A subset of AI that...           │    │
│  │   - Enables systems to learn from... │    │
│  │                                      │    │
│  │                                      │    │
│  └──────────────────────────────────────┘    │
│                                              │
│  ┌──────────────────────────────────────┐    │
│  │  📥 Export as PDF  │ 📥 Export Word  │    │
│  └──────────────────────────────────────┘    │
│                                              │
├──────────────────────────────────────────────┤
│                 AppFooter                     │
└──────────────────────────────────────────────┘
```

### Tab Behavior

Two strategies to consider:

**Strategy A: Generate All at Once (Recommended for MVP)**
- When user clicks Generate on the HomeView, fire all selected study aid types in parallel
- Show a multi-step progress indicator: "Generating Summary... ✓ Generating Quiz..."
- All tabs are populated when the user arrives at ResultsView
- **Pro:** Simpler UX, user doesn't wait per-tab
- **Con:** Longer initial wait, more API calls at once (rate limit risk)

**Strategy B: Generate On-Tab-Click (Lazy)**
- Only generate a study aid when the user clicks its tab
- Show loading spinner in the tab content area
- Cache results so re-clicking a tab doesn't regenerate
- **Pro:** Faster initial load, fewer API calls upfront
- **Con:** User waits each time they click a new tab

> **Recommendation:** Start with **Strategy A** for MVP. If rate limits become an issue, switch to Strategy B.

### Source Preview

- Collapsible section showing the original text
- Collapsed by default (focus on study aids)
- Shows first 500 characters with "Show more" expansion
- Useful for users to verify the correct text was processed

### Markdown Rendering

- Use `marked` library to convert Markdown to HTML
- Use `DOMPurify` to sanitize the HTML (prevent XSS)
- Apply custom CSS for rendered content:
  - Styled headers, tables, lists
  - Code blocks with background color
  - Bold terms highlighted
  - Checkbox styling for study guide checklists

---

## 6. State Management (Pinia)

### Store: `useStudyStore`

**State:**

```javascript
{
  // Input
  sourceText: '',          // The text to generate from (pasted or extracted)
  sourceFile: null,        // File metadata if uploaded
  selectedTypes: ['summary', 'key_terms', 'quiz', 'study_guide'],

  // Generation
  isGenerating: false,     // Global loading state
  generationProgress: {},  // Per-type progress: { summary: 'loading', key_terms: 'done', ... }

  // Results
  results: {
    summary: null,         // Generated content (Markdown string) or null
    key_terms: null,
    quiz: null,
    study_guide: null,
  },

  // Errors
  error: null,             // Global error message
  typeErrors: {},          // Per-type errors: { quiz: "Rate limit exceeded" }

  // UI
  activeTab: 'summary',   // Currently selected result tab
}
```

**Getters:**

```javascript
{
  hasSourceText: (state) => state.sourceText.length >= 50,
  hasResults: (state) => Object.values(state.results).some(r => r !== null),
  charCount: (state) => state.sourceText.length,
  isOverLimit: (state) => state.sourceText.length > 50000,
  canGenerate: (state) => state.hasSourceText && state.selectedTypes.length > 0 && !state.isGenerating,
}
```

**Actions:**

```javascript
{
  setSourceText(text): // Set source text from paste or extraction
  setSourceFile(file): // Set file metadata after upload
  toggleType(type):    // Toggle a study aid type selection
  selectAllTypes():    // Check all types
  setActiveTab(tab):   // Switch active result tab

  async extractFile(file):  // Upload file → call /api/extract → set sourceText
  async generateAll():      // Generate all selected types → call /api/generate for each
  async generateOne(type):  // Generate a single type
  async exportResult(type, format): // Call /api/export for a specific result

  clearResults():     // Clear all generated results
  clearAll():         // Full reset (back to initial state)
}
```

---

## 7. API Service Layer

### `services/api.js`

Create an Axios instance with preconfigured settings:

### Base Configuration

```javascript
{
  baseURL: import.meta.env.VITE_API_BASE_URL,  // From .env
  timeout: 120000,                              // 2 minutes (AI generation can be slow)
  headers: {
    'Content-Type': 'application/json',
  }
}
```

### Interceptors

**Request Interceptor:**
- Log request method and URL (dev only)
- Could add auth token here in the future

**Response Interceptor:**
- On success: return `response.data` directly (unwrap Axios response)
- On error: extract error message from response body
- Handle specific status codes:
  - `429` → "Rate limit exceeded. Please wait a moment."
  - `413` → "File is too large. Maximum size is 10 MB."
  - `415` → "Unsupported file type. Please upload PDF or PPTX."
  - `422` → Display validation error details
  - `500` → "Server error. Please try again later."
  - Network error → "Unable to connect to server. Check your internet connection."

### API Methods

```javascript
api.healthCheck()           // GET /api/health
api.extractFile(file)       // POST /api/extract (multipart)
api.generateStudyAid(text, type)  // POST /api/generate
api.exportStudyAid(content, format, title)  // POST /api/export → returns blob
```

---

## 8. Loading & Error States

### Loading States to Implement

| State | Where | Visual |
|---|---|---|
| File uploading | FileUpload component | Progress bar + percentage |
| File extracting | FileUpload component | Spinner + "Extracting text..." |
| Generating study aids | ResultsView or HomeView | Multi-step progress indicator |
| Exporting document | ExportBar | Button spinner + "Exporting..." |

### Multi-Step Generation Progress

When generating all study aids, show progress:

```
✓ Summary — Generated
⟳ Key Terms — Generating...
○ Quiz — Waiting
○ Study Guide — Waiting
```

### Error Display Patterns

| Error Type | Display |
|---|---|
| Validation error (empty text) | Inline message near input field |
| File upload error | Alert below upload zone |
| API connection error | Full-width banner at top |
| Generation error (single type) | Error message in the specific tab |
| Generation error (all fail) | Full error page with retry button |
| Rate limit error | Toast notification with countdown |

---

## 9. Responsive Design Requirements

### Breakpoints

| Breakpoint | Width | Layout Changes |
|---|---|---|
| Mobile | < 640px | Single column, stacked tabs, full-width inputs |
| Tablet | 640px – 1024px | Slightly wider inputs, side-by-side tab labels |
| Desktop | > 1024px | Centered max-width container, spacious layout |

### Key Responsive Behaviors

- **Textarea:** Full width on all breakpoints, minimum height 200px on mobile
- **File upload zone:** Full width, shorter height on mobile
- **Result tabs:** Horizontal scroll on mobile if too many tabs, or switch to dropdown
- **Export buttons:** Stack vertically on mobile
- **Markdown content:** Ensure tables scroll horizontally on mobile (overflow-x: auto)

---

## 10. UX Polish Checklist

### Micro-Interactions

- [ ] Smooth tab transitions (fade or slide)
- [ ] Button hover effects with subtle scale/shadow
- [ ] Drag-and-drop visual feedback (border color change, icon animation)
- [ ] Character counter color transition as limit approaches
- [ ] Skeleton loading state while content loads
- [ ] Success animation when generation completes (subtle confetti or checkmark)
- [ ] Smooth scroll to results after generation

### Accessibility

- [ ] All form inputs have labels
- [ ] Keyboard navigation works for tabs
- [ ] Focus management after navigation
- [ ] Color contrast meets WCAG AA
- [ ] File upload zone is keyboard-accessible
- [ ] Error messages announced to screen readers (aria-live)

### Empty States

- [ ] Results page with no generated content → helpful message
- [ ] Upload zone → clear instructions with supported formats
- [ ] Tab with generation error → retry button

---

## 11. Styling Approach — Decision Point

Choose ONE approach before starting:

### Option A: Component Library (Faster Development)

Use **PrimeVue** or **Vuetify** for pre-built components:
- **Pro:** Faster development, consistent design, built-in responsive
- **Con:** Larger bundle, opinionated design, learning curve
- **Recommendation:** PrimeVue (lighter weight, works well with Vite)

### Option B: Custom CSS (Full Control)

Build all components with custom CSS:
- **Pro:** Smaller bundle, unique design, full control
- **Con:** Slower development, must build every component
- **Recommendation:** If you want a distinctive, portfolio-worthy design

### Option C: Utility Framework

Use **Tailwind CSS**:
- **Pro:** Rapid prototyping, responsive utilities
- **Con:** Verbose HTML, learning curve
- **Recommendation:** Good middle ground if you know Tailwind

> **For a beginner:** Start with **Option A (PrimeVue)** to ship faster, then customize the theme.

---

## 12. Phase 5 Completion Checklist

- [ ] Vue Router configured with all routes
- [ ] Pinia store created with all state, getters, and actions
- [ ] API service layer configured with Axios
- [ ] HomeView built with text input and file upload
- [ ] TextInput component with character counter and validation
- [ ] FileUpload component with drag-and-drop
- [ ] Study aid type checkboxes working
- [ ] Generate button with loading state and validation
- [ ] ResultsView built with tab navigation
- [ ] Markdown content renders correctly
- [ ] Loading states for all async operations
- [ ] Error states display correctly
- [ ] Navigation between pages works
- [ ] Responsive layout on mobile and desktop
- [ ] Backend integration tested end-to-end (paste text → see results)
