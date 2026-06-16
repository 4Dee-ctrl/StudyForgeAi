# 04 — Gemini Integration & Prompt Engineering

> **Phase:** 4 of 9
> **Goal:** Integrate the Google Gemini API, design and test prompt templates for all four study aid types, implement response parsing, and handle AI-specific error scenarios.
> **Estimated Time:** 4–6 hours (prompt engineering is iterative)
> **Depends On:** Phase 2 (Backend API Foundation)

---

## 1. Phase Objectives

By the end of this phase:

- The Gemini API client is fully integrated and tested
- Four prompt templates produce high-quality, structured study aids
- AI responses are parsed into clean, consistent formats
- Error handling covers API failures, rate limits, and malformed responses
- The `/api/generate` endpoint is fully functional (not a stub)

---

## 2. Gemini API Client Service

### `services/gemini.py`

Create a dedicated service class to encapsulate all Gemini interactions.

### Client Initialization

```
GeminiService:
    __init__(api_key, model_name):
        - Configure the google-generativeai SDK
        - Set the model (default: gemini-2.0-flash)
        - Configure generation settings (temperature, max_tokens, etc.)
        - Configure safety settings

    generate(text, study_aid_type) → StudyAidResult:
        - Select the appropriate prompt template
        - Construct the full prompt
        - Call the Gemini API
        - Parse and validate the response
        - Return structured result
```

### Generation Configuration

| Parameter | Value | Rationale |
|---|---|---|
| `temperature` | `0.3` | Low temperature for factual, consistent outputs. Summaries and key terms should not be creative. |
| `top_p` | `0.95` | Slight diversity while maintaining accuracy |
| `top_k` | `40` | Standard value |
| `max_output_tokens` | `8192` | Generous limit for comprehensive study guides |

> **Why low temperature?** Study aids must be accurate and factual. High temperature introduces creative but potentially incorrect content. For quizzes, we might bump to `0.5` to get varied question phrasing.

### Safety Settings

Configure safety settings to be permissive for educational content:

```
HARASSMENT: BLOCK_ONLY_HIGH
HATE_SPEECH: BLOCK_ONLY_HIGH
SEXUALLY_EXPLICIT: BLOCK_ONLY_HIGH
DANGEROUS_CONTENT: BLOCK_ONLY_HIGH
```

> **Why permissive?** Academic texts may discuss sensitive historical events, medical topics, or social issues. Aggressive safety filters would block legitimate educational content. `BLOCK_ONLY_HIGH` only blocks clearly harmful content.

---

## 3. Prompt Engineering — General Principles

### The Prompt Formula

Every prompt follows this structure:

```
[SYSTEM CONTEXT]
You are an expert academic tutor and study aid creator.

[TASK INSTRUCTION]
Specific instruction for the study aid type.

[OUTPUT FORMAT]
Exact format specification with examples.

[CONSTRAINTS]
Rules and boundaries for the output.

[INPUT TEXT]
--- BEGIN SOURCE MATERIAL ---
{user's text}
--- END SOURCE MATERIAL ---
```

### Key Prompt Engineering Rules

1. **Be explicit about format.** Gemini follows formatting instructions well when they're specific.
2. **Use delimiters.** Wrap the source text in clear delimiters (`--- BEGIN ---` / `--- END ---`) so the model distinguishes instructions from content.
3. **Request Markdown output.** Markdown is easy to render in the frontend and looks professional.
4. **Include negative instructions.** Tell the model what NOT to do (e.g., "Do not include information not found in the source material").
5. **Give examples.** Few-shot examples dramatically improve output quality.

---

## 4. Prompt Template: Reviewer Summary

### Purpose

Generate a structured, hierarchical summary of the source material organized by topic/section.

### Prompt Specification

**System context:**
- Expert academic tutor specializing in creating concise, comprehensive study summaries

**Task:**
- Analyze the source material and create a well-organized summary
- Identify the main topics, subtopics, and key points
- Preserve the logical flow and hierarchy of the original material
- Highlight critical concepts, definitions, and relationships

**Output format (Markdown):**
```markdown
# Summary: [Auto-generated title based on content]

## [Main Topic 1]
- Key point with explanation
- Key point with explanation
  - Supporting detail
  - Supporting detail

## [Main Topic 2]
- Key point with explanation
...

## Key Takeaways
- Most important point 1
- Most important point 2
- Most important point 3
```

**Constraints:**
- Summary should be 20–30% the length of the original text
- Use bullet points, not paragraphs (easier to scan)
- Do not add information not present in the source material
- Bold important terms on first mention
- Include a "Key Takeaways" section at the end (max 5 points)

---

## 5. Prompt Template: Key Terms

### Purpose

Extract important vocabulary, concepts, and terminology with clear definitions.

### Prompt Specification

**Task:**
- Identify all significant terms, concepts, acronyms, and jargon
- Provide a clear, concise definition for each term
- Categorize terms by topic if there are multiple subjects

**Output format (Markdown):**
```markdown
# Key Terms

## [Category/Topic 1]

| Term | Definition |
|---|---|
| **Term 1** | Clear, concise definition based on the source material |
| **Term 2** | Clear, concise definition based on the source material |

## [Category/Topic 2]

| Term | Definition |
|---|---|
| **Term 3** | Definition |
```

**Constraints:**
- Extract 10–30 terms depending on content length
- Definitions should be 1–2 sentences maximum
- Terms should be sorted by order of appearance (not alphabetically)
- If a term has an acronym, include it: e.g., **CPU (Central Processing Unit)**
- Only extract terms that are meaningfully defined or explained in the source material

---

## 6. Prompt Template: Quiz

### Purpose

Generate a practice quiz with varied question types to test comprehension.

### Prompt Specification

**Task:**
- Create a balanced quiz covering all major topics in the source material
- Generate a mix of question types
- Include an answer key with brief explanations

**Output format (Markdown):**
```markdown
# Quiz: [Auto-generated title]

## Multiple Choice

**1. [Question text]**
- A) Option A
- B) Option B
- C) Option C
- D) Option D

**2. [Question text]**
- A) Option A
...

## Identification / Short Answer

**6. [Question or prompt]**

**7. [Question or prompt]**

## True or False

**9. [Statement]**

**10. [Statement]**

---

# Answer Key

**1.** C) Option C — [Brief explanation of why this is correct]
**2.** A) Option A — [Brief explanation]
...
**6.** [Expected answer — brief explanation]
...
**9.** True — [Explanation]
**10.** False — [Explanation and correction]
```

**Constraints:**
- Generate 10–20 questions depending on content length
- Distribution: ~50% multiple choice, ~30% identification, ~20% true/false
- Questions should range from recall (easy) to application (hard)
- Every question must be answerable from the source material alone
- Multiple choice distractors should be plausible (not obviously wrong)
- Answer key must be separated from questions (users may want to hide it)
- Mark difficulty: Easy / Medium / Hard (optional, nice-to-have)

### Quiz-Specific Generation Settings

- Bump temperature to `0.5` for more varied question phrasing
- This prevents generating repetitive questions when the same material is submitted multiple times

---

## 7. Prompt Template: Study Guide

### Purpose

Generate a comprehensive, exam-prep-style study guide with structured sections, mnemonics, and study tips.

### Prompt Specification

**Task:**
- Create a comprehensive study guide that a student could use to prepare for an exam
- Organize by topic with clear headings
- Include memory aids, mnemonics, and conceptual connections
- Add practice scenarios or application examples where relevant

**Output format (Markdown):**
```markdown
# Study Guide: [Auto-generated title]

## Overview
Brief description of what this study guide covers and how to use it.

## Topic 1: [Topic Name]

### What You Need to Know
- Concept explanation in clear, student-friendly language
- Key relationships and connections

### Memory Aids
- 💡 **Mnemonic:** [Memory aid for remembering key points]
- 🔗 **Connection:** [How this relates to other topics]

### Common Mistakes to Avoid
- ❌ [Common misconception and why it's wrong]
- ✅ [Correct understanding]

## Topic 2: [Topic Name]
...

## Quick Review Checklist
- [ ] I can explain [concept 1]
- [ ] I can differentiate between [A] and [B]
- [ ] I understand why [concept] matters
...

## Summary Table

| Concept | Key Point | Example |
|---|---|---|
| [Concept] | [One-line summary] | [Brief example] |
```

**Constraints:**
- Most comprehensive of all study aids — can be longer than the original text
- Use student-friendly language (explain jargon when used)
- Include at least one mnemonic or memory aid per major topic
- Include a "Quick Review Checklist" at the end
- Include a summary table for quick reference
- Use emojis sparingly for visual scanning (💡🔗❌✅📌)

---

## 8. Response Parsing & Validation

### What Could Go Wrong

| Issue | Detection | Handling |
|---|---|---|
| Empty response | `len(response.text) == 0` | Retry once, then return error |
| Response is not Markdown | Check for basic Markdown markers (`#`, `-`, `|`) | Accept as-is (Gemini almost always returns Markdown) |
| Response is truncated | Check if max_output_tokens was hit | Add note: "Output may be incomplete due to length limits" |
| Response contains hallucinated content | Cannot detect automatically | Warn user in UI: "AI-generated content should be verified" |
| Safety filter triggered | `response.prompt_feedback.block_reason` is set | Return specific error about content filtering |
| API returns error | Exception from SDK | Catch and return appropriate HTTP error |

### Response Processing Pipeline

```
1. Call Gemini API
2. Check for safety blocks → if blocked, return error with reason
3. Check for empty response → if empty, retry once
4. Extract response.text
5. Validate basic structure (contains expected Markdown elements)
6. Add metadata (token usage, model used)
7. Return to client
```

### Token Usage Tracking

Include token usage in the response (for debugging and monitoring):

```json
{
  "type": "summary",
  "content": "# Summary: ...",
  "meta": {
    "model": "gemini-2.0-flash",
    "input_tokens": 3245,
    "output_tokens": 1023,
    "total_tokens": 4268,
    "generation_time_ms": 2340
  }
}
```

---

## 9. Error Handling — Gemini-Specific

### Rate Limiting (429 from Gemini)

```
Strategy: Exponential backoff with retry
- First retry: wait 2 seconds
- Second retry: wait 4 seconds
- Third retry: wait 8 seconds
- After 3 retries: return 429 to the client with message:
  "The AI service is currently busy. Please try again in a few minutes."
```

### Quota Exceeded (Daily Limit)

```
If daily RPD limit (1,500) is hit:
- Return 429 with message:
  "Daily usage limit reached. The service will reset at midnight (Pacific Time)."
- Log a warning so you can monitor usage
```

### Content Blocked by Safety Filter

```
Return 422 with message:
"The submitted content was flagged by the AI safety filter.
 This may happen with certain academic topics.
 Try submitting a shorter excerpt or rephrasing the content."
```

### Network/API Errors

```
- Timeout (>60s): Return 504 "AI request timed out. Please try again."
- Connection error: Return 502 "Unable to reach AI service. Please try again later."
- Invalid API key: Return 500 "Server configuration error." (don't leak details)
```

---

## 10. Gemini API Usage Optimization

### Token Efficiency

- **Trim whitespace** before sending to Gemini (saves tokens on excessive blank lines)
- **Don't send page/slide separators** if they're not useful for context
- **Consider chunking** for very long texts: if input > 30,000 tokens, summarize in chunks then combine (future optimization)

### Caching Considerations (Future)

For the MVP, no caching. But note for the future:
- Hash the input text + study aid type to create a cache key
- Store responses in Redis or even an in-memory dict with TTL
- This saves API calls when users regenerate the same content

### Cost Monitoring

Even though the free tier has no monetary cost, track usage to avoid hitting limits:
- Log every API call with token counts
- Track daily request count
- Add an internal endpoint `/api/admin/usage` (protected) that shows current usage stats

---

## 11. The Generate Endpoint — Full Implementation Spec

### `POST /api/generate`

**Request:**
```json
{
  "text": "The source material text...",
  "type": "summary"
}
```

**Processing Flow:**
```
1. Validate request (Pydantic schema)
2. Check rate limit
3. Trim and validate text length
4. Select prompt template based on type
5. Construct full prompt (template + source text)
6. Call GeminiService.generate()
7. Handle errors (retry on 429, error on safety block)
8. Parse response
9. Return formatted result
```

**Response (Success):**
```json
{
  "type": "summary",
  "content": "# Summary: Introduction to Machine Learning\n\n## What is Machine Learning?\n...",
  "meta": {
    "model": "gemini-2.0-flash",
    "input_tokens": 5432,
    "output_tokens": 2100,
    "generation_time_ms": 3200
  }
}
```

---

## 12. Testing Strategy

### Test with Real Content

Prepare 3–5 diverse test inputs:

1. **Short text** (~500 words) — a Wikipedia paragraph
2. **Medium text** (~2,000 words) — a textbook chapter section
3. **Long text** (~10,000 words) — a full chapter
4. **Technical content** — content with jargon, formulas, acronyms
5. **Non-English** — test behavior with non-English text (Gemini handles many languages)

### Quality Checklist for Each Study Aid Type

**Summary:**
- [ ] Has clear hierarchical structure (H1, H2, bullets)
- [ ] Length is 20–30% of original
- [ ] No hallucinated content
- [ ] Key takeaways section present

**Key Terms:**
- [ ] Terms are relevant and correctly defined
- [ ] Definitions match the source material
- [ ] Table format is correct Markdown
- [ ] 10–30 terms extracted

**Quiz:**
- [ ] Mix of question types present
- [ ] All questions answerable from source material
- [ ] Answer key is separated and complete
- [ ] Distractors are plausible

**Study Guide:**
- [ ] Comprehensive and well-organized
- [ ] Memory aids/mnemonics present
- [ ] Quick review checklist present
- [ ] Student-friendly language

### Prompt Iteration

Prompt engineering is iterative. Expect to:
1. Write the initial prompt
2. Test with diverse inputs
3. Identify weaknesses (too verbose, missing sections, wrong format)
4. Refine the prompt
5. Repeat 3–5 times per prompt template

---

## 13. Phase 4 Completion Checklist

- [ ] Gemini SDK configured and authenticated
- [ ] GeminiService class created with clean interface
- [ ] Generation config set (temperature, max_tokens, safety settings)
- [ ] Summary prompt template written and tested
- [ ] Key Terms prompt template written and tested
- [ ] Quiz prompt template written and tested
- [ ] Study Guide prompt template written and tested
- [ ] Response parsing validates and cleans AI output
- [ ] Retry logic with exponential backoff for rate limits
- [ ] Error handling covers all Gemini-specific failure modes
- [ ] Token usage logged for each request
- [ ] `/api/generate` endpoint fully functional (replaces stub)
- [ ] Tested with 3+ diverse real-world text inputs
- [ ] All four study aid types produce quality output
