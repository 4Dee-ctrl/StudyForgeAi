from __future__ import annotations

import asyncio
import os

from fastapi import APIRouter, File, UploadFile

from ..config import settings
from ..exceptions import EmptyFileError, FileTooLargeError, UnsupportedFileTypeError
from ..schemas.models import ExtractMetadata, ExtractResponse
from ..services.file_parser import FileParser

router = APIRouter(tags=["Extract"])

_extract_semaphore = asyncio.Semaphore(3)
_parser = FileParser(max_text_length=settings.max_text_length)


@router.post(
	"/extract",
	response_model=ExtractResponse,
	summary="Extract text from a PDF or PPTX",
)
async def extract(file: UploadFile = File(...)) -> ExtractResponse:
	"""Accepts an uploaded PDF/PPTX and returns extracted text.
	"""

	filename = file.filename or ""
	ext = os.path.splitext(filename)[1].lower()

	if ext not in {".pdf", ".pptx"}:
		raise UnsupportedFileTypeError(
			f"Only PDF and PPTX files are supported. Received: {ext or 'unknown'}"
		)

	expected_mime = {
		".pdf": "application/pdf",
		".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
	}[ext]
	actual_mime = (file.content_type or "").lower()
	if actual_mime != expected_mime:
		raise UnsupportedFileTypeError(
			f"MIME type does not match extension. Expected: {expected_mime}. Received: {actual_mime or 'unknown'}"
		)

	file_bytes = await file.read()
	size_bytes = len(file_bytes)
	if size_bytes == 0:
		raise EmptyFileError("The uploaded file is empty.")

	max_bytes = settings.max_file_size_mb * 1024 * 1024
	if size_bytes > max_bytes:
		size_mb = size_bytes / (1024 * 1024)
		raise FileTooLargeError(
			f"File size ({size_mb:.1f} MB) exceeds the maximum allowed size ({settings.max_file_size_mb} MB)."
		)

	async with _extract_semaphore:
		result = await asyncio.to_thread(_parser.parse, file_bytes=file_bytes, filename=filename)

	metadata = ExtractMetadata(
		filename=result.filename,
		file_type=result.file_type,
		page_count=result.page_count,
		char_count=result.char_count,
		word_count=result.word_count,
		truncated=result.truncated,
	)

	return ExtractResponse(text=result.text, metadata=metadata, warning=result.warning)
