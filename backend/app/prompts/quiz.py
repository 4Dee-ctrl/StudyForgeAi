from __future__ import annotations

from .common import BASE_PROMPT_CONTRACT, source_block


def build_prompt(source_text: str) -> str:
	return f"""{BASE_PROMPT_CONTRACT}
[TASK]
Create a practice quiz that tests recall, comprehension, and application of the source material.

[EXACT OUTPUT TEMPLATE]
# Quiz: [Specific title from the source]

## Multiple Choice
**1. [Question text]**
- A) [Option]
- B) [Option]
- C) [Option]
- D) [Option]

## Short Answer
**6. [Question text]**

## True or False
**9. [Statement from the source]**

---

# Answer Key
**1.** [Letter]) [Correct option] - [One-sentence explanation grounded in the source.]

[QUESTION RULES]
- Create exactly 10 questions when enough source material is available.
- Questions 1-5 must be Multiple Choice.
- Questions 6-8 must be Short Answer.
- Questions 9-10 must be True or False.
- Number questions consecutively from 1 to 10.
- Multiple-choice questions must have exactly four options: A, B, C, D.
- Use a balanced answer distribution for multiple choice. Do not make every answer A.
- Every answer-key item must include a short explanation.
- Do not reveal answers before the Answer Key.

[QUALITY CHECK BEFORE RESPONDING]
- Does the response start with "# Quiz:"?
- Are the four main sections present in this order: Multiple Choice, Short Answer, True or False, Answer Key?
- Are there exactly 10 numbered questions if the source supports it?
- Is every question answerable from the source alone?

{source_block(source_text)}"""
