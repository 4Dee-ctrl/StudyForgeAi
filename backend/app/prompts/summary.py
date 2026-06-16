from __future__ import annotations


def build_prompt(source_text: str) -> str:
	return f"""[SYSTEM CONTEXT]
You are an expert academic tutor and study aid creator.

[TASK INSTRUCTION]
Analyze the source material and create a structured reviewer summary organized by topic.

[OUTPUT FORMAT] (Markdown)
# Summary: [Auto-generated title based on content]

## [Main Topic 1]
- Key point with explanation
- Key point with explanation
	- Supporting detail
	- Supporting detail

## [Main Topic 2]
- Key point with explanation

## Key Takeaways
- Most important point 1
- Most important point 2
- Most important point 3

[CONSTRAINTS]
- The summary should be ~20–30% the length of the original text.
- Use bullet points (avoid long paragraphs).
- Do not add information not present in the source material.
- Bold important terms on first mention.
- Include a Key Takeaways section (max 5 points).

[INPUT TEXT]
--- BEGIN SOURCE MATERIAL ---
{source_text}
--- END SOURCE MATERIAL ---
"""
