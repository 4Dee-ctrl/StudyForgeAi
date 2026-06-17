from __future__ import annotations

from .common import BASE_PROMPT_CONTRACT, source_block


def build_prompt(source_text: str) -> str:
	return f"""{BASE_PROMPT_CONTRACT}
[TASK]
Extract important vocabulary, concepts, people, events, formulas, acronyms, and named processes from the source material.

[EXACT OUTPUT TEMPLATE]
# Key Terms

## Terms Table
| Term | Type | Definition | Why It Matters |
|---|---|---|---|
| **Term** | concept/process/person/event/formula/acronym | 1 sentence definition from the source. | 1 sentence explaining its study value from the source. |

## Quick Review
- Write 3-5 bullets connecting the most important terms.

[SELECTION RULES]
- Include 8-20 terms, depending on source length.
- List terms in order of first appearance in the source.
- Use a specific Type value from this set only: concept, process, person, event, formula, acronym, place, date, other.
- If fewer than 8 supported terms exist, include only the supported terms and add "_Limited by available source material._" under Quick Review.
- Do not include generic words unless the source clearly defines them as important.

[QUALITY CHECK BEFORE RESPONDING]
- Does the response start with "# Key Terms"?
- Is the table header exactly as requested?
- Does every definition come from the source?
- Are terms listed by order of appearance?

{source_block(source_text)}"""
