from __future__ import annotations

import asyncio
import logging
from functools import lru_cache

from fastapi import APIRouter

from ..config import settings
from ..exceptions import GeminiAPIError, ServerConfigurationError
from ..schemas.models import GenerateMeta, GenerateRequest, GenerateResponse
from ..services.gemini import GeminiResult, GeminiService
from ..services.local_generator import LocalGenerateResult, LocalStudyAidGenerator

logger = logging.getLogger("studyforge.generate")

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
	try:
		result = await asyncio.to_thread(
			generator.generate,
			text=payload.text,
			study_aid_type=payload.type,
		)
	except (GeminiAPIError, ServerConfigurationError) as exc:
		logger.warning(
			"Gemini unavailable; using local fallback generator (%s)",
			exc.__class__.__name__,
		)
		result = await asyncio.to_thread(
			LocalStudyAidGenerator().generate,
			text=payload.text,
			study_aid_type=payload.type,
		)

	return _response_from_result(payload=payload, result=result)


def _response_from_result(
	*,
	payload: GenerateRequest,
	result: GeminiResult | LocalGenerateResult,
) -> GenerateResponse:
	meta = GenerateMeta(
		model=result.model,
		input_tokens=result.input_tokens,
		output_tokens=result.output_tokens,
		total_tokens=result.total_tokens,
		generation_time_ms=result.generation_time_ms,
	)
	return GenerateResponse(type=payload.type, content=result.content, meta=meta)
