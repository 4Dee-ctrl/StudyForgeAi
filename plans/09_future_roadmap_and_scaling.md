# 09 — Future Roadmap & Scaling

> **Phase:** 9 of 9
> **Goal:** Document the future evolution of StudyForge beyond the MVP — user accounts, persistent storage, premium features, and scaling strategies.
> **Priority:** Low (plan only, implement after MVP is live and validated)

---

## 1. The MVP → Product Evolution Path

```
MVP (Phases 1–8)                    v1.0 — What We Built
├── Stateless (no database)
├── No user accounts
├── No history/saved sessions
├── Single AI model (Gemini Flash)
├── In-memory rate limiting
└── Free hosting (Vercel + Render)

        │
        ▼

Post-MVP Tier 1 (Quick Wins)       v1.1 — Low-Effort Improvements
├── Local storage for history
├── Dark mode / theme toggle
├── Streaming AI responses
├── Better error messages
└── Performance optimizations

        │
        ▼

Post-MVP Tier 2 (User Accounts)    v2.0 — Real Product
├── Authentication (Google OAuth)
├── Database (Supabase / PostgreSQL)
├── Saved study sessions
├── User dashboard
└── Usage quotas per user

        │
        ▼

Post-MVP Tier 3 (Monetization)     v3.0 — Business
├── Freemium model
├── Stripe payments
├── Premium features (longer docs, better model)
├── Team/classroom features
└── API access for other developers
```

---

## 2. Tier 1 — Quick Wins (Post-MVP)

These can be implemented in 1–2 days each and significantly improve the user experience.

### 2.1 Local Storage History

**What:** Save generated study aids in the browser's localStorage so users can revisit them without regenerating.

**How:**
- After generation, save to localStorage: `{ id, timestamp, sourcePreview, type, content }`
- Add a "History" section to the HomeView showing recent sessions (last 10)
- Click to reload a previous session
- "Clear History" button

**Limitations:**
- Limited to ~5 MB of storage
- Lost if user clears browser data
- Not synced across devices

### 2.2 Dark Mode

**What:** Toggle between light and dark color schemes.

**How:**
- CSS custom properties for all colors
- Toggle button in AppHeader
- Respect `prefers-color-scheme` media query for initial default
- Save preference in localStorage

### 2.3 Streaming AI Responses

**What:** Show AI-generated content as it's being produced, word by word.

**How:**
- Use Gemini's streaming API (`generate_content_stream`)
- Backend uses Server-Sent Events (SSE) to stream chunks to frontend
- Frontend progressively renders Markdown as chunks arrive
- UX feels much faster (first tokens appear in < 1 second)

**Complexity:** Medium — requires SSE setup and incremental Markdown rendering.

### 2.4 Copy-to-Clipboard Improvements

- Copy button on every section heading
- "Copy as Markdown" and "Copy as Plain Text" options
- Toast notification on copy

### 2.5 Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl + Enter` | Generate study aids |
| `Ctrl + 1/2/3/4` | Switch to tab 1/2/3/4 |
| `Ctrl + E` | Export current tab as PDF |
| `Ctrl + Shift + E` | Export current tab as DOCX |
| `Escape` | Close modals / exit focus mode |

---

## 3. Tier 2 — User Accounts & Persistence

### 3.1 Authentication

**Recommended: Supabase Auth or Firebase Auth**

- Google OAuth is the simplest for students (everyone has a Google account)
- Supabase Auth is free, open-source, and works well with PostgreSQL
- Firebase Auth is Google's solution — great docs, free tier

**Flow:**
```
1. User clicks "Sign in with Google"
2. OAuth flow redirects to Google
3. Google returns auth token
4. Frontend stores token in memory/cookie
5. All API requests include token in Authorization header
6. Backend validates token on each request
7. User's study sessions are linked to their user ID
```

### 3.2 Database

**Recommended: Supabase (PostgreSQL)**

Supabase offers:
- Free tier with 500 MB storage
- Built-in auth
- PostgreSQL (industry standard)
- Real-time subscriptions (optional)
- REST API auto-generated from schema
- Works well with the GitHub Student Developer Pack

**Schema Design:**

```sql
-- Users (managed by Supabase Auth)
-- id, email, created_at, etc. are automatic

-- Study Sessions
CREATE TABLE study_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    title VARCHAR(200),
    source_text TEXT,
    source_filename VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Study Aids
CREATE TABLE study_aids (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES study_sessions(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL,  -- summary, key_terms, quiz, study_guide
    content TEXT NOT NULL,
    token_usage JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Usage Tracking
CREATE TABLE usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    action VARCHAR(50),  -- generate, export, extract
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 3.3 User Dashboard

**Features:**
- View all past study sessions
- Search and filter by title, date, type
- Delete sessions
- Re-export past study aids
- Usage statistics (sessions this month, total words processed)

### 3.4 Usage Quotas

Implement per-user limits to manage Gemini API costs:

| Tier | Sessions/Day | Exports/Day | Max Text Length |
|---|---|---|---|
| Free | 10 | 20 | 30,000 chars |
| Premium | Unlimited | Unlimited | 100,000 chars |

---

## 4. Tier 3 — Monetization

### 4.1 Freemium Model

```
Free Tier:
├── 10 generations per day
├── Gemini Flash model
├── Export as PDF only
├── 30,000 char input limit
└── No saved history (or limited to 5)

Premium Tier ($5/month or $40/year):
├── Unlimited generations
├── Gemini Pro model (higher quality)
├── Export as PDF and DOCX
├── 100,000 char input limit
├── Unlimited saved history
├── Priority processing
└── Custom branding on exports (remove "StudyForge" watermark)
```

### 4.2 Stripe Integration

Use Stripe for payment processing:
- Stripe Checkout for the payment page (no custom payment form needed)
- Stripe Webhooks to update user tier on payment
- Stripe Customer Portal for subscription management

### 4.3 Revenue Projections

| Users | Free (80%) | Premium (20%) | MRR |
|---|---|---|---|
| 100 | 80 | 20 | $100 |
| 500 | 400 | 100 | $500 |
| 1,000 | 800 | 200 | $1,000 |
| 5,000 | 4,000 | 1,000 | $5,000 |

At $5,000 MRR, you'd likely need to move off the free tiers:
- Render paid tier: ~$7/month
- Supabase paid tier: ~$25/month
- Gemini paid tier: Variable (but still cheap for text)
- Vercel paid tier: ~$20/month

---

## 5. Feature Ideas — Backlog

### High Impact, Low Effort

| Feature | Effort | Impact |
|---|---|---|
| Flashcard mode (from key terms) | 2 days | High |
| Share study aids via link | 1 day | High |
| Multiple language support | 1 day | Medium (Gemini already supports this) |
| Spaced repetition reminders | 3 days | High |
| Import from Google Docs URL | 2 days | Medium |

### High Impact, High Effort

| Feature | Effort | Impact |
|---|---|---|
| OCR for scanned PDFs (Tesseract) | 1 week | High |
| Collaborative study rooms | 2 weeks | High |
| Mobile app (PWA) | 3 days | Medium |
| Custom prompt templates | 1 week | Medium |
| LMS integration (Canvas, Moodle) | 2 weeks | High (for institutions) |
| Handwriting recognition (photo upload) | 2 weeks | High |

### Low Priority / Nice-to-Have

| Feature | Notes |
|---|---|
| Gamification (XP, streaks) | Increases engagement but non-essential |
| AI chat about the material | "Ask me anything about this chapter" |
| Audio study guides (TTS) | Use browser Web Speech API |
| Mind map generation | Visual learning aid (use a diagram library) |
| Plagiarism-safe paraphrasing | Ensure study aids are original language |

---

## 6. Scaling Considerations

### When to Scale

Scale when you observe:
- Response times > 5 seconds consistently
- Gemini rate limits hit frequently (daily)
- Render server crashes due to memory
- More than ~100 concurrent users

### Backend Scaling

| Level | Solution |
|---|---|
| Level 1 | Upgrade Render to paid tier ($7/month) — more RAM, no cold starts |
| Level 2 | Add Redis for caching and rate limiting |
| Level 3 | Add a task queue (Celery + Redis) for async AI generation |
| Level 4 | Multiple backend instances behind a load balancer |
| Level 5 | Move to a dedicated cloud provider (Railway, Fly.io, or AWS) |

### Caching Strategy

```
Request → Check cache (Redis)
    │
    ├── Cache HIT → Return cached result (instant)
    │
    └── Cache MISS → Call Gemini API → Store in cache → Return result
```

Cache key: `hash(source_text + study_aid_type)`
Cache TTL: 24 hours (study aids don't change for the same input)

### Cost Optimization

- Cache aggressively to reduce Gemini API calls
- Use Gemini Flash (cheapest) for free tier, Gemini Pro for premium
- Implement request deduplication (same user, same text, within 60s)
- Monitor token usage daily

---

## 7. Technical Debt to Address

| Debt | Priority | When to Address |
|---|---|---|
| In-memory rate limiter → Redis | High | Before 50+ users |
| No automated tests | High | Before adding features |
| No CI/CD pipeline | Medium | Before team collaboration |
| Hardcoded prompt templates → DB/config | Medium | Before customization feature |
| No logging aggregation | Medium | Before debugging production issues |
| Markdown parser is basic | Low | When export quality complaints arise |
| No API versioning | Low | Before breaking changes |

---

## 8. Competitive Landscape

Understand where StudyForge fits in the market:

| Competitor | Differentiator |
|---|---|
| Quizlet | Established, but quiz-focused. StudyForge generates multiple aid types |
| Notion AI | General purpose. StudyForge is specialized for study materials |
| ChatGPT | Requires crafting prompts. StudyForge is one-click |
| Scholarcy | Research-focused summarizer. StudyForge targets students |
| StudyForge | Free, specialized, one-click, multiple output types, exportable |

### Our Unique Value Proposition

"Paste your notes, get a complete study kit in 30 seconds — for free."

---

## 9. Success Metrics

### MVP Success Criteria

| Metric | Target | How to Measure |
|---|---|---|
| App is live | Yes | Vercel + Render URLs work |
| End-to-end flow works | Yes | Text → Study Aid → Export |
| Time to first result | < 30s | Manual testing |
| Works on mobile | Yes | Manual testing |
| Zero critical bugs | Yes | Manual testing + user feedback |

### Growth Metrics (Post-MVP)

| Metric | Target (Month 1) | How to Measure |
|---|---|---|
| Daily Active Users | 10 | Analytics |
| Generations per day | 50 | Server logs |
| Retention (7-day) | 30% | Analytics |
| User satisfaction | 4/5 stars | Feedback form |
| Time on site | > 3 min | Analytics |

---

## 10. Launch Strategy

### Soft Launch

1. Share with 5–10 classmates for feedback
2. Fix critical bugs and UX issues
3. Iterate on prompt quality based on real usage

### Public Launch

1. Post on social media (Twitter/X, Reddit r/college, r/studying)
2. Submit to Product Hunt
3. Share in student Discord servers / Facebook groups
4. Write a blog post about building it (great for portfolio)

### Portfolio Value

This project demonstrates:
- Full-stack development (Vue.js + Python)
- AI/API integration
- Cloud deployment
- File processing
- Document generation
- System architecture

> **Tip:** Create a detailed README with screenshots, architecture diagrams, and a demo video. This significantly improves portfolio impact.
