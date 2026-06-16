# 06 — Study Aids Display & Interaction

> **Phase:** 6 of 9
> **Goal:** Build rich, polished rendering for all four study aid types with type-specific formatting, interactive elements, and a seamless user experience in the results view.
> **Estimated Time:** 4–5 hours
> **Depends On:** Phase 5 (Frontend UI), Phase 4 (Generate endpoint)

---

## 1. Phase Objectives

By the end of this phase:

- All four study aid types render beautifully with type-specific styling
- Markdown content is safely rendered as interactive HTML
- Quiz answers can be hidden/revealed interactively
- Users can copy individual sections to clipboard
- Print-friendly layout for browser printing
- Smooth transitions between tabs

---

## 2. Markdown Rendering Pipeline

### The Pipeline

```
Raw Markdown (from API)
    │
    ▼
marked.parse()        → Raw HTML string
    │
    ▼
DOMPurify.sanitize()  → Sanitized HTML (no XSS risk)
    │
    ▼
v-html directive      → Rendered in the DOM
    │
    ▼
Scoped CSS            → Styled with study-aid-specific rules
```

### MarkdownRenderer Component

Create a reusable `MarkdownRenderer.vue` component:

**Props:**
- `content` (String, required) — Raw Markdown string
- `type` (String, optional) — Study aid type for type-specific styling classes

**Behavior:**
1. Parse Markdown to HTML using `marked`
2. Sanitize with DOMPurify
3. Apply the HTML via `v-html`
4. Add a CSS class based on `type` for targeted styling

### Marked Configuration

Configure `marked` for optimal study aid rendering:

- Enable GitHub Flavored Markdown (GFM) for tables and task lists
- Enable `breaks: true` (treat single newlines as `<br>`)
- Custom renderer overrides:
  - Tables: add `class="study-table"` for styling
  - Links: add `target="_blank"` and `rel="noopener"`
  - Headings: add `id` attributes for anchor linking

### DOMPurify Configuration

Allow specific HTML elements and attributes:

```
Allowed tags: p, h1-h6, ul, ol, li, table, thead, tbody, tr, th, td,
              strong, em, code, pre, blockquote, a, br, hr, input, span
Allowed attributes: class, id, href, target, rel, type, checked, disabled
```

Block: `<script>`, `<iframe>`, `<form>`, `<style>`, event handlers (`onclick`, etc.)

---

## 3. Type-Specific Rendering — Summary

### Expected Structure

```markdown
# Summary: [Title]

## [Topic 1]
- Point
- Point
  - Sub-point

## [Topic 2]
- Point

## Key Takeaways
- Takeaway 1
- Takeaway 2
```

### Styling Goals

- Clean hierarchy with distinct heading styles
- Bullet points with custom icons or indentation markers
- Bold terms highlighted with a subtle background color
- "Key Takeaways" section visually distinct (colored background card, icon)
- Print-friendly: headings and bullets survive print layout

### Special Rendering Rules

- Detect the `## Key Takeaways` section and wrap it in a styled card
- Add a subtle left border to each `## Section` for visual separation
- Auto-generate a mini table of contents at the top (list of H2 headings with anchor links)

---

## 4. Type-Specific Rendering — Key Terms

### Expected Structure

```markdown
# Key Terms

## [Category 1]

| Term | Definition |
|---|---|
| **Term** | Definition text |

## [Category 2]

| Term | Definition |
|---|---|
| **Term** | Definition text |
```

### Styling Goals

- Tables should be full-width with alternating row colors
- Term column should be narrower (30%) and definitions wider (70%)
- Bold terms in the first column should stand out
- Category headings should be visually distinct
- Mobile: tables should scroll horizontally OR reflow into card layout

### Interactive Features

- **Search/filter:** Add a search input above the terms table that filters rows as the user types
- **Copy term:** Hover on a term to show a "copy" icon that copies "Term: Definition" to clipboard
- **Term count badge:** Show "23 terms extracted" badge

### Mobile Responsiveness

Tables are problematic on mobile. Two options:

**Option A: Horizontal Scroll**
- Wrap table in `overflow-x: auto` container
- Show scroll hint on mobile

**Option B: Card Layout (Recommended)**
- On mobile (< 640px), transform the table into stacked cards:
  ```
  ┌────────────────────┐
  │ Term               │
  │ Definition text    │
  │ that wraps nicely  │
  └────────────────────┘
  ```
- Use CSS media queries or a responsive table library

---

## 5. Type-Specific Rendering — Quiz

### Expected Structure

```markdown
# Quiz: [Title]

## Multiple Choice

**1. Question text**
- A) Option A
- B) Option B
- C) Option C
- D) Option D

## Identification

**6. Question text**

## True or False

**9. Statement**

---

# Answer Key

**1.** C) — Explanation
**6.** Expected answer — Explanation
**9.** True — Explanation
```

### Styling Goals

- Questions numbered with clear visual hierarchy
- Multiple choice options styled as selectable cards (not plain list)
- Clear visual separation between question sections
- Answer key hidden by default (reveal mechanism)

### Interactive Features — Quiz-Specific

This is the most interactive study aid type.

#### Answer Hiding/Revealing

The answer key should be separated from the questions and hidden behind a toggle:

```
┌─────────────────────────────────────┐
│  Quiz: Introduction to Biology      │
│                                     │
│  1. What is photosynthesis?         │
│     ○ A) Cell division              │
│     ○ B) Light to energy conversion │
│     ○ C) DNA replication            │
│     ○ D) Protein synthesis          │
│                                     │
│  2. True or False: Cells are...     │
│                                     │
│  ┌─────────────────────────────┐    │
│  │  🔒 Show Answer Key         │    │
│  │  (Click to reveal answers)  │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

**Implementation approach:**
1. Parse the Markdown to find the `# Answer Key` section
2. Split the content into two parts: questions and answers
3. Render questions normally
4. Wrap answers in a collapsible component
5. Animate the reveal (slide down or fade in)

#### Self-Check Mode (Nice-to-Have)

Allow users to select answers before revealing:
- Multiple choice: clickable option buttons
- True/False: toggle buttons
- After selecting, show checkmark (correct) or X (incorrect) with explanation
- Track score: "You got 7/10 correct!"

> **Note:** This requires post-processing the Markdown to extract structured quiz data. Consider having Gemini return JSON instead of Markdown for quizzes. This can be a v2 enhancement.

---

## 6. Type-Specific Rendering — Study Guide

### Expected Structure

```markdown
# Study Guide: [Title]

## Overview
Brief description.

## Topic 1: [Name]

### What You Need to Know
- Concepts...

### Memory Aids
- 💡 **Mnemonic:** ...
- 🔗 **Connection:** ...

### Common Mistakes
- ❌ Mistake
- ✅ Correct understanding

## Quick Review Checklist
- [ ] I can explain...
- [ ] I understand...

## Summary Table
| Concept | Key Point | Example |
|---|---|---|
```

### Styling Goals

- Most visually rich of all study aid types
- Emoji icons rendered natively (not stripped)
- "Memory Aids" sections highlighted with colored background cards
- "Common Mistakes" formatted as red (wrong) / green (correct) pairs
- Checklist items rendered as actual checkboxes (interactive)
- Summary table well-formatted and scannable

### Interactive Features

#### Interactive Checklist

The `- [ ]` Markdown task list items should render as functional checkboxes:
- Users can check/uncheck items as they study
- Visual feedback (strikethrough or green highlight on checked items)
- Counter: "4 of 12 completed"
- State persisted in Pinia store (but NOT persisted across sessions in MVP — no database)

#### Memory Aid Cards

Detect lines starting with 💡, 🔗, or 📌 and wrap them in styled cards:

```
┌─────────────────────────────────────┐
│ 💡 Mnemonic                         │
│ "ROY G. BIV" — The colors of       │
│ the visible light spectrum:         │
│ Red, Orange, Yellow, Green, Blue,   │
│ Indigo, Violet                      │
└─────────────────────────────────────┘
```

#### Common Mistakes Highlighting

Detect ❌ and ✅ patterns and style them:
- ❌ lines: red left border, light red background
- ✅ lines: green left border, light green background

---

## 7. Shared Interactive Features (All Types)

### Copy to Clipboard

- "Copy" button on each study aid tab
- Copies the raw Markdown (not HTML) to clipboard
- Toast notification: "Copied to clipboard!"
- Also allow copying individual sections (hover to reveal copy icon on headings)

### Print View

- "Print" button that opens browser print dialog
- Apply `@media print` CSS:
  - Remove navigation, header, footer, buttons
  - Use serif font for readability
  - Ensure page breaks don't split tables or sections
  - Black and white friendly (reduce color dependency)

### Full Screen / Focus Mode

- Toggle button to expand the study aid content to full viewport
- Hides header, tabs, and export bar
- Escape key or close button to exit
- Useful for focused studying

### Text Size Adjustment

- Small / Medium / Large buttons to adjust font size
- Stored in Pinia (per session) or localStorage (persistent)
- Affects only the rendered content, not the app UI

---

## 8. Tab Navigation — Detailed Behavior

### Tab States

| State | Visual |
|---|---|
| **Active** | Highlighted background, bold text, underline/indicator |
| **Loaded** | Normal text, subtle checkmark icon |
| **Loading** | Spinner icon replacing the checkmark |
| **Error** | Red text, warning icon |
| **Disabled** | Grayed out, not clickable (type was not selected) |

### Tab Transition Animation

When switching tabs, animate the content:
- Use Vue's `<Transition>` component
- Fade out → fade in (simple and clean)
- Or slide left/right based on tab position (more dynamic)
- Duration: 200–300ms

### Tab Keyboard Navigation

- Arrow keys to move between tabs
- Enter/Space to activate a tab
- Tab key to move into the content area

---

## 9. Empty & Error States for Results

### No Results Yet

If user navigates to `/results` without generating:
```
┌─────────────────────────────────┐
│                                 │
│   📚  No study aids yet        │
│                                 │
│   Go back to the input page    │
│   and paste your study material │
│                                 │
│   [← Go to Input Page]         │
│                                 │
└─────────────────────────────────┘
```

### Generation Failed (Single Type)

Show in the specific tab:
```
┌─────────────────────────────────┐
│                                 │
│   ⚠️  Could not generate quiz  │
│                                 │
│   Error: Rate limit exceeded.   │
│   Please try again in 1 minute. │
│                                 │
│   [🔄 Retry]                   │
│                                 │
└─────────────────────────────────┘
```

### Generation Failed (All Types)

Show a full-page error:
```
┌─────────────────────────────────┐
│                                 │
│   ❌  Generation Failed         │
│                                 │
│   We couldn't connect to the   │
│   AI service. This may be due  │
│   to high demand.              │
│                                 │
│   [🔄 Try Again]  [← Go Back] │
│                                 │
└─────────────────────────────────┘
```

---

## 10. Performance Considerations

### Markdown Rendering

- Markdown parsing is synchronous and can block the main thread for very large documents
- For content > 50,000 characters, consider:
  - Using a Web Worker for parsing
  - Lazy rendering (render visible portion first, then rest)
  - Virtual scrolling for very long content

### Image Handling

- Gemini responses should not contain images, but if they do, DOMPurify will strip them
- No image rendering needed in MVP

### Memory

- Store raw Markdown strings, not parsed HTML, in Pinia
- Parse HTML only when rendering (computed property)
- This avoids doubling memory usage

---

## 11. Phase 6 Completion Checklist

- [ ] MarkdownRenderer component created and tested
- [ ] Summary rendering with styled sections and key takeaways card
- [ ] Key Terms rendering with searchable, styled tables
- [ ] Quiz rendering with hidden/reveal answer key
- [ ] Study Guide rendering with interactive checklists and memory aid cards
- [ ] Tab navigation with all states (active, loaded, loading, error, disabled)
- [ ] Tab transition animations working
- [ ] Copy to clipboard functionality
- [ ] Print-friendly CSS
- [ ] Empty states and error states designed and implemented
- [ ] Responsive: all study aids readable on mobile
- [ ] Tables scroll or reflow on mobile
- [ ] Font size adjustment working
- [ ] End-to-end test: paste text → generate → view all 4 types → verify formatting
