from __future__ import annotations


def build_prompt(source_text: str) -> str:
	return f"""[SYSTEM CONTEXT]
You are an expert academic tutor and study aid creator.

[TASK INSTRUCTION]
Create a practice quiz that tests comprehension of the source material.

[OUTPUT FORMAT] (Markdown)
# Quiz: [Auto-generated title]

## Multiple Choice

**1. [Question text]**
- A) Option A
- B) Option B
- C) Option C
- D) Option D

## Identification / Short Answer

**6. [Question or prompt]**

## True or False

**9. [Statement]**

---

# Answer Key

**1.** C) Option C — Brief explanation

[CONSTRAINTS]
- Generate 10–20 questions depending on content length.
- Mix: ~50% multiple choice, ~30% identification, ~20% true/false.
- Every question must be answerable from the source material alone.
- Multiple choice distractors should be plausible.
- Keep the Answer Key separated from the questions.
- Do not add facts not present in the source.

[INPUT TEXT]
--- BEGIN SOURCE MATERIAL ---
{source_text}
--- END SOURCE MATERIAL ---
"""
