from __future__ import annotations

from enum import StrEnum
from pydantic import BaseModel, Field


class StudyAidType(StrEnum):
	summary = "summary"
	key_terms = "key_terms"
	quiz = "quiz"
	study_guide = "study_guide"


class ExportFormat(StrEnum):
	pdf = "pdf"
	docx = "docx"


class GenerateRequest(BaseModel):
	"""Generate a study aid from input text."""

	text: str = Field(
		...,
		min_length=50,
		max_length=50000,
		examples=["Paste at least a few paragraphs of study material here..."],
	)
	type: StudyAidType = Field(..., examples=[StudyAidType.summary])


class ExportRequest(BaseModel):
	"""Export a generated study aid to PDF or Word."""

	content: str = Field(..., min_length=1, examples=["# Summary\n\n...markdown..."])
	format: ExportFormat = Field(..., examples=[ExportFormat.pdf])
	title: str = Field(default="Study Aid", max_length=200, examples=["Chapter 5 Summary"])


class ExtractMetadata(BaseModel):
	"""Extraction metadata returned alongside extracted text."""

	filename: str
	file_type: str
	page_count: int
	char_count: int
	word_count: int
	truncated: bool = False


class ExtractResponse(BaseModel):
	"""Extraction response payload."""

	text: str
	metadata: ExtractMetadata
	warning: str | None = None


class GenerateMeta(BaseModel):
	"""Generation metadata for debugging/monitoring."""

	model: str
	input_tokens: int | None = None
	output_tokens: int | None = None
	total_tokens: int | None = None
	generation_time_ms: int


class GenerateResponse(BaseModel):
	"""Study aid generation response."""

	type: StudyAidType
	content: str
	meta: GenerateMeta


class ErrorResponse(BaseModel):
	"""Consistent error response format."""

	error: str
	detail: str
	status_code: int
