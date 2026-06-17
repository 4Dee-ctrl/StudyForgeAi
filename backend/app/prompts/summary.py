from __future__ import annotations

from .common import BASE_PROMPT_CONTRACT, source_block


def build_prompt(source_text: str) -> str:
	return f"""{BASE_PROMPT_CONTRACT}
[TASK]
Create a structured study summary from the source material.

[EXACT OUTPUT TEMPLATE]
# Summary: [Specific title from the source]

## Overview
- Write 3-5 bullets that explain the overall subject and purpose of the material.
- Each bullet must be one complete sentence.

## Core Concepts
- Create 5-8 bullets.
- Bold the main term or idea at the start of each bullet, then explain it.
- Format: - **Concept:** explanation from the source.

## Process or Structure
- If the source describes steps, stages, causes, categories, or relationships, summarize them here in 3-6 bullets.
- If the source has no process or structure, write exactly: - No clear process or structure was provided in the source.

## Key Takeaways
- Provide exactly 5 bullets unless the source is too short.
- Each takeaway must be directly useful for review.

[QUALITY CHECK BEFORE RESPONDING]
- Does the response start with "# Summary:"?
- Are all four H2 sections present in the exact order?
- Are all claims grounded in the source?
- Is the wording concise and consistent?

{source_block(source_text)}"""
