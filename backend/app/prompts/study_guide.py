from __future__ import annotations

from .common import BASE_PROMPT_CONTRACT, source_block


def build_prompt(source_text: str) -> str:
	return f"""{BASE_PROMPT_CONTRACT}
[TASK]
Create a comprehensive exam-prep study guide from the source material.

[EXACT OUTPUT TEMPLATE]
# Study Guide: [Specific title from the source]

## Overview
- Write 3-4 bullets explaining what the material covers.

## Learning Objectives
- Write 4-6 "I can..." statements.

## Main Topics
### [Topic Name]
- **What it means:** 1-2 sentences.
- **Details to remember:** 2-4 bullets.
- **Common confusion:** 1 bullet naming a likely misunderstanding based only on the source.

## Review Questions
- Write 5 open-ended questions a student should be able to answer after studying.

## Quick Review Checklist
- [ ] Write 5-8 checklist items.

## Summary Table
| Concept | Key Point | Source Detail |
|---|---|---|
| [Concept] | [Main idea] | [Specific supporting detail from source] |

[CONTENT RULES]
- Create 2-5 Main Topics depending on source length.
- Use H3 headings only inside Main Topics.
- Do not add memory aids unless the source itself supports them.
- Keep each table cell under 25 words.
- If the source is too short, create fewer topics and add "_Limited by available source material._" after the Overview.

[QUALITY CHECK BEFORE RESPONDING]
- Does the response start with "# Study Guide:"?
- Are all six H2 sections present in the exact order?
- Does every topic include "What it means", "Details to remember", and "Common confusion"?
- Are all claims grounded in the source?

{source_block(source_text)}"""
