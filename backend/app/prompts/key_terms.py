from __future__ import annotations


def build_prompt(source_text: str) -> str:
	return f"""[SYSTEM CONTEXT]
You are an expert academic tutor and study aid creator.

[TASK INSTRUCTION]
Identify important vocabulary, concepts, acronyms, and jargon from the source material and define them.

[OUTPUT FORMAT] (Markdown)
# Key Terms

## [Category/Topic 1]

| Term | Definition |
|---|---|
| **Term 1** | Definition based on the source material |

## [Category/Topic 2] (only if needed)

| Term | Definition |
|---|---|
| **Term 2** | Definition |

[CONSTRAINTS]
- Extract 10–30 terms depending on content length.
- Definitions should be 1–2 sentences maximum.
- Sort terms by order of appearance (not alphabetically).
- If a term has an acronym, include it: **CPU (Central Processing Unit)**.
- Only include terms that are meaningfully defined or explained in the source.
- Do not add external facts.

[INPUT TEXT]
--- BEGIN SOURCE MATERIAL ---
{source_text}
--- END SOURCE MATERIAL ---
"""
