from __future__ import annotations

import re
import time
from collections import Counter
from dataclasses import dataclass

from ..schemas.models import StudyAidType


@dataclass(slots=True)
class LocalGenerateResult:
	content: str
	model: str
	input_tokens: int | None
	output_tokens: int | None
	total_tokens: int | None
	generation_time_ms: int


class LocalStudyAidGenerator:
	"""Deterministic fallback generator for local development without an AI key."""

	def generate(self, *, text: str, study_aid_type: StudyAidType) -> LocalGenerateResult:
		started = time.perf_counter()
		cleaned_text = _normalize_text(text)
		sentences = _sentences(cleaned_text)
		key_terms = _key_terms(cleaned_text)

		builders = {
			StudyAidType.summary: self._summary,
			StudyAidType.key_terms: self._key_terms,
			StudyAidType.quiz: self._quiz,
			StudyAidType.study_guide: self._study_guide,
		}
		content = builders[study_aid_type](cleaned_text, sentences, key_terms)
		input_tokens = _estimate_tokens(cleaned_text)
		output_tokens = _estimate_tokens(content)

		return LocalGenerateResult(
			content=content,
			model="local-studyforge-fallback",
			input_tokens=input_tokens,
			output_tokens=output_tokens,
			total_tokens=input_tokens + output_tokens,
			generation_time_ms=int((time.perf_counter() - started) * 1000),
		)

	def _summary(self, text: str, sentences: list[str], terms: list[str]) -> str:
		title = _title_from_terms(terms)
		selected = _select_representative_sentences(sentences, limit=8)
		takeaways = selected[:5] or [text[:220].strip()]

		lines = [f"# Summary: {title}", "", "## Overview"]
		overview = selected[:5] or takeaways
		lines.extend(f"- {sentence}" for sentence in overview)

		lines.extend(["", "## Core Concepts"])
		if terms:
			for term in terms[:8]:
				lines.append(f"- **{term}:** {_definition_for(term, sentences)}")
		else:
			lines.append("- **Source Material:** The submitted text is the basis for this study aid.")

		lines.extend(["", "## Process or Structure"])
		process_items = selected[5:8]
		if process_items:
			lines.extend(f"- {sentence}" for sentence in process_items)
		else:
			lines.append("- No clear process or structure was provided in the source.")

		lines.extend(["", "## Key Takeaways"])
		lines.extend(f"- {item}" for item in takeaways)
		lines.extend(["", "_Generated locally. Add a Gemini API key for richer AI output._"])
		return "\n".join(lines)

	def _key_terms(self, text: str, sentences: list[str], terms: list[str]) -> str:
		lines = [
			"# Key Terms",
			"",
			"## Terms Table",
			"| Term | Type | Definition | Why It Matters |",
			"|---|---|---|---|",
		]
		for term in terms[:20]:
			definition = _definition_for(term, sentences)
			lines.append(
				f"| **{term}** | concept | {definition} | This is useful for reviewing the source material. |"
			)
		if len(lines) == 5:
			lines.append(
				"| **Source Material** | other | The submitted study content. | This is the basis for the study aid. |"
			)
		lines.extend(["", "## Quick Review"])
		if terms:
			lines.extend(f"- {term} connects to the main ideas in the source material." for term in terms[:5])
		else:
			lines.append("- _Limited by available source material._")
		lines.extend(["", "_Generated locally. Add a Gemini API key for richer AI output._"])
		return "\n".join(lines)

	def _quiz(self, text: str, sentences: list[str], terms: list[str]) -> str:
		selected_terms = terms[:6] or ["source material"]
		selected_sentences = _select_representative_sentences(sentences, limit=6)

		lines = ["# Quiz: StudyForge Practice Check", "", "## Multiple Choice"]
		answer_lines = ["", "---", "", "# Answer Key"]

		for index, term in enumerate(selected_terms[:4], start=1):
			definition = _definition_for(term, sentences)
			lines.extend(
				[
					"",
					f"**{index}. Which statement best matches {term}?**",
					f"- A) {definition}",
					"- B) It is unrelated to the submitted material.",
					"- C) It is only a formatting label.",
					"- D) It is a source citation.",
				]
			)
			answer_lines.append(f"**{index}.** A) {definition}")

		lines.extend(["", "## Short Answer"])
		offset = 5
		for idx, sentence in enumerate(selected_sentences[:3], start=offset):
			lines.extend(["", f"**{idx}. Briefly explain this idea:** {sentence}"])
			answer_lines.append(f"**{idx}.** A good answer should mention: {sentence}")

		lines.extend(["", "## True or False"])
		tf_number = offset + min(3, len(selected_sentences))
		for idx, sentence in enumerate(selected_sentences[3:6], start=tf_number):
			lines.extend(["", f"**{idx}.** {sentence}"])
			answer_lines.append(f"**{idx}.** True.")

		lines.extend(answer_lines)
		lines.extend(["", "_Generated locally. Add a Gemini API key for richer AI output._"])
		return "\n".join(lines)

	def _study_guide(self, text: str, sentences: list[str], terms: list[str]) -> str:
		title = _title_from_terms(terms)
		selected = _select_representative_sentences(sentences, limit=8)
		display_terms = terms[:8]

		lines = [
			f"# Study Guide: {title}",
			"",
			"## Overview",
			"- This guide organizes the submitted material into review points, practice prompts, and a quick checklist.",
			"- Each item is based on the submitted source material.",
			"",
			"## Learning Objectives",
		]
		if display_terms:
			lines.extend(f"- I can explain {term}." for term in display_terms[:6])
		else:
			lines.append("- I can explain the main idea of the submitted source material.")

		lines.extend(["", "## Main Topics"])
		if display_terms:
			for term in display_terms[:5]:
				lines.extend(
					[
						f"### {term}",
						f"- **What it means:** {_definition_for(term, sentences)}",
						"- **Details to remember:**",
						f"- {term} appears as an important idea in the source material.",
						"- **Common confusion:** Do not add outside facts beyond what the source supports.",
					]
				)
		else:
			lines.extend(
				[
					"### Submitted Study Material",
					"- **What it means:** The submitted text is the source for this study guide.",
					"- **Details to remember:**",
					"- Review the source carefully before relying on generated material.",
					"- **Common confusion:** Do not add outside facts beyond what the source supports.",
				]
			)

		lines.extend(["", "## Review Questions"])
		if display_terms:
			lines.extend(f"- How would you explain {term} using the source material?" for term in display_terms[:5])
		else:
			lines.append("- What is the main idea of the submitted source material?")

		lines.extend(["", "## Quick Review Checklist"])
		if display_terms:
			lines.extend(f"- [ ] I can explain {term}." for term in display_terms[:6])
		else:
			lines.append("- [ ] I can explain the main idea of the source.")

		lines.extend(["", "## Summary Table", "", "| Concept | Key Point | Source Detail |", "|---|---|---|"])
		for term in display_terms[:6]:
			lines.append(f"| {term} | Review this concept. | {_definition_for(term, sentences)} |")
		if not display_terms:
			lines.append("| Source Material | Review the submitted text. | _Limited by available source material._ |")

		lines.extend(["", "_Generated locally. Add a Gemini API key for richer AI output._"])
		return "\n".join(lines)


def _normalize_text(text: str) -> str:
	return re.sub(r"\s+", " ", (text or "").strip())


def _sentences(text: str) -> list[str]:
	parts = re.split(r"(?<=[.!?])\s+", text)
	return [part.strip() for part in parts if len(part.strip()) > 20]


def _words(text: str) -> list[str]:
	return re.findall(r"[A-Za-z][A-Za-z'-]{2,}", text)


def _key_terms(text: str) -> list[str]:
	stop_words = {
		"about",
		"after",
		"also",
		"because",
		"before",
		"between",
		"could",
		"first",
		"from",
		"have",
		"into",
		"more",
		"only",
		"other",
		"should",
		"their",
		"there",
		"these",
		"this",
		"through",
		"using",
		"were",
		"when",
		"where",
		"which",
		"while",
		"with",
		"would",
	}
	words = [word.strip("'").lower() for word in _words(text)]
	counts = Counter(word for word in words if word not in stop_words and len(word) > 3)
	ordered: list[str] = []
	for word in words:
		if word in counts and counts[word] >= 2 and word not in ordered:
			ordered.append(word)
		if len(ordered) >= 20:
			break
	if not ordered:
		ordered = [word for word, _ in counts.most_common(10)]
	return [word.replace("-", " ").title() for word in ordered]


def _select_representative_sentences(sentences: list[str], *, limit: int) -> list[str]:
	if not sentences:
		return []
	candidates = [sentence for sentence in sentences if len(sentence) <= 260]
	if not candidates:
		candidates = sentences
	step = max(1, len(candidates) // limit)
	selected = candidates[::step][:limit]
	return selected or candidates[:limit]


def _definition_for(term: str, sentences: list[str]) -> str:
	lowered = term.lower()
	for sentence in sentences:
		if lowered in sentence.lower():
			return sentence[:260].strip()
	return "An important concept found in the submitted source material."


def _title_from_terms(terms: list[str]) -> str:
	if not terms:
		return "Submitted Study Material"
	return ", ".join(terms[:3])


def _estimate_tokens(text: str) -> int:
	return max(1, len(text.split()))
