from __future__ import annotations

from ..schemas.models import StudyAidType


EXPECTED_SECTIONS: dict[StudyAidType, list[str]] = {
	StudyAidType.summary: [
		"# Summary:",
		"## Overview",
		"## Core Concepts",
		"## Process or Structure",
		"## Key Takeaways",
	],
	StudyAidType.key_terms: [
		"# Key Terms",
		"## Terms Table",
		"| Term | Type | Definition | Why It Matters |",
		"## Quick Review",
	],
	StudyAidType.quiz: [
		"# Quiz:",
		"## Multiple Choice",
		"## Short Answer",
		"## True or False",
		"# Answer Key",
	],
	StudyAidType.study_guide: [
		"# Study Guide:",
		"## Overview",
		"## Learning Objectives",
		"## Main Topics",
		"## Review Questions",
		"## Quick Review Checklist",
		"## Summary Table",
	],
}


def missing_expected_sections(*, content: str, study_aid_type: StudyAidType) -> list[str]:
	return [section for section in EXPECTED_SECTIONS[study_aid_type] if section not in content]
