from __future__ import annotations

import asyncio
from functools import lru_cache

from fastapi import APIRouter

from ..config import settings
from ..exceptions import ServerConfigurationError
from ..schemas.models import GenerateMeta, GenerateRequest, GenerateResponse
from ..services.gemini import GeminiService

router = APIRouter(tags=["Generate"])


@lru_cache(maxsize=1)
def _get_gemini() -> GeminiService:
	api_key = (settings.gemini_api_key or "").strip()
	if not api_key:
		raise ServerConfigurationError("Server configuration error.")
	return GeminiService(api_key=api_key, model_names=settings.gemini_model_chain)


@router.post(
	"/generate",
	response_model=GenerateResponse,
	summary="Generate a study aid from text",
)
async def generate(payload: GenerateRequest) -> GenerateResponse:
	"""Generates a study aid from text.

	Phase 4 integrates Gemini and returns Markdown content.
	"""

	gemini = _get_gemini()
	result = await asyncio.to_thread(
		gemini.generate,
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
