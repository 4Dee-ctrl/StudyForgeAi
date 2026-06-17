from __future__ import annotations

import asyncio
from functools import lru_cache

from fastapi import APIRouter

from ..config import settings
from ..schemas.models import GenerateMeta, GenerateRequest, GenerateResponse
from ..services.gemini import GeminiService
from ..services.local_generator import LocalStudyAidGenerator

router = APIRouter(tags=["Generate"])


@lru_cache(maxsize=1)
def _get_generator() -> GeminiService | LocalStudyAidGenerator:
	api_key = (settings.gemini_api_key or "").strip()
	if not api_key or api_key == "your_api_key_here":
		return LocalStudyAidGenerator()
	return GeminiService(api_key=api_key, model_names=settings.gemini_model_chain)


@router.post(
	"/generate",
	response_model=GenerateResponse,
	summary="Generate a study aid from text",
)
async def generate(payload: GenerateRequest) -> GenerateResponse:
	"""Generates a study aid from text.

	Uses Gemini when configured, or a deterministic local generator for development.
	"""

	generator = _get_generator()
	result = await asyncio.to_thread(
		generator.generate,
		text=payload.text,
		study_aid_type=payload.type,
	)

	meta = GenerateMeta(
		model=result.model,
		input_tokens=result.input_tokens,
		output_tokens=result.output_tokens,
		total_tokens=result.total_tokens,
		generation_time_ms=result.generation_time_ms,
	)
	return GenerateResponse(type=payload.type, content=result.content, meta=meta)
