from __future__ import annotations


def build_prompt(source_text: str) -> str:
	return f"""[SYSTEM CONTEXT]
You are an expert academic tutor and study aid creator.

[TASK INSTRUCTION]
Create a comprehensive, exam-prep-style study guide based on the source material.

[OUTPUT FORMAT] (Markdown)
# Study Guide: [Auto-generated title]

## Overview
Brief description of what this study guide covers and how to use it.

## Topic 1: [Topic Name]

### What You Need to Know
- Key concepts in student-friendly language

### Memory Aids
- 💡 **Mnemonic:** ...
- 🔗 **Connection:** ...

### Common Mistakes to Avoid
- ❌ ...
- ✅ ...

## Quick Review Checklist
- [ ] I can explain ...

## Summary Table

| Concept | Key Point | Example |
|---|---|---|
| ... | ... | ... |

[CONSTRAINTS]
- Use student-friendly language.
- Explain jargon when it appears.
- Include at least one memory aid per major topic.
- Include a Quick Review Checklist.
- Include a summary table.
- Use emojis sparingly (💡🔗❌✅📌).
- Do not add information not present in the source.

[INPUT TEXT]
--- BEGIN SOURCE MATERIAL ---
{source_text}
--- END SOURCE MATERIAL ---
"""
