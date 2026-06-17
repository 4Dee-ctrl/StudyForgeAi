from __future__ import annotations

import logging
import time
from dataclasses import dataclass

import google.generativeai as genai

from ..exceptions import (
	AITimeoutError,
	ContentBlockedError,
	GeminiAPIError,
	RateLimitError,
	ServerConfigurationError,
)
from ..prompts import key_terms, quiz, study_guide, summary
from ..schemas.models import StudyAidType

logger = logging.getLogger("studyforge.ai")


@dataclass(slots=True)
class GeminiResult:
	content: str
	model: str
	input_tokens: int | None
	output_tokens: int | None
	total_tokens: int | None
	generation_time_ms: int


class GeminiService:
	def __init__(
		self,
		*,
		api_key: str,
		model_name: str | None = None,
		model_names: list[str] | None = None,
	):
		genai.configure(api_key=api_key)
		chain = model_names or ([model_name] if model_name else [])
		self._model_names = [name.strip() for name in chain if name and name.strip()]
		if not self._model_names:
			raise ServerConfigurationError("Server configuration error.")

		self._base_generation_config = {
			"temperature": 0.2,
			"top_p": 0.9,
			"top_k": 40,
			"max_output_tokens": 8192,
		}

		self._quiz_generation_config = {
			**self._base_generation_config,
			"temperature": 0.25,
		}

		self._safety_settings = [
			{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
			{"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
			{"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
			{"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
		]

	def generate(self, *, text: str, study_aid_type: StudyAidType) -> GeminiResult:
		cleaned_text = (text or "").strip()

		prompt_builder = {
			StudyAidType.summary: summary.build_prompt,
			StudyAidType.key_terms: key_terms.build_prompt,
			StudyAidType.quiz: quiz.build_prompt,
			StudyAidType.study_guide: study_guide.build_prompt,
		}[study_aid_type]

		prompt = prompt_builder(cleaned_text)
		generation_config = (
			self._quiz_generation_config
			if study_aid_type == StudyAidType.quiz
			else self._base_generation_config
		)

		backoff_seconds = [2, 4, 8]
		last_exc: Exception | None = None

		started = time.perf_counter()
		for model_index, model_name in enumerate(self._model_names):
			model = genai.GenerativeModel(model_name)
			is_fallback_model = model_index > 0

			if is_fallback_model:
				logger.warning(
					"Trying Gemini fallback model after primary failure (model=%s)",
					model_name,
				)

			try:
				return self._generate_with_model(
					model=model,
					model_name=model_name,
					prompt=prompt,
					generation_config=generation_config,
					started=started,
					study_aid_type=study_aid_type,
					backoff_seconds=backoff_seconds,
				)
			except RateLimitError as exc:
				last_exc = exc
				if model_index < len(self._model_names) - 1:
					continue
				raise
			except GeminiAPIError as exc:
				last_exc = exc
				if model_index < len(self._model_names) - 1:
					continue
				raise

		raise GeminiAPIError("Unable to reach AI service. Please try again later.") from last_exc

	def _generate_with_model(
		self,
		*,
		model,
		model_name: str,
		prompt: str,
		generation_config: dict,
		started: float,
		study_aid_type: StudyAidType,
		backoff_seconds: list[int],
	) -> GeminiResult:
		last_exc: Exception | None = None

		for attempt in range(len(backoff_seconds) + 1):
			try:
				response = model.generate_content(
					prompt,
					generation_config=generation_config,
					safety_settings=self._safety_settings,
				)

				feedback = getattr(response, "prompt_feedback", None)
				block_reason = getattr(feedback, "block_reason", None) if feedback else None
				if block_reason:
					raise ContentBlockedError(
						"The submitted content was flagged by the AI safety filter. "
						"Try submitting a shorter excerpt or rephrasing the content."
					)

				content = (getattr(response, "text", None) or "").strip()
				if not content:
					# Retry once on empty response
					if attempt == 0:
						continue
					raise GeminiAPIError("Empty AI response")

				usage = getattr(response, "usage_metadata", None)
				input_tokens = getattr(usage, "prompt_token_count", None) if usage else None
				output_tokens = (
					getattr(usage, "candidates_token_count", None) if usage else None
				)
				total_tokens = getattr(usage, "total_token_count", None) if usage else None

				generation_time_ms = int((time.perf_counter() - started) * 1000)
				logger.info(
					"Gemini generate succeeded (type=%s, in=%s, out=%s, total=%s, ms=%s)",
					study_aid_type,
					input_tokens,
					output_tokens,
					total_tokens,
					generation_time_ms,
				)

				return GeminiResult(
					content=content,
					model=model_name,
					input_tokens=input_tokens,
					output_tokens=output_tokens,
					total_tokens=total_tokens,
					generation_time_ms=generation_time_ms,
				)

			except ContentBlockedError:
				raise
			except Exception as exc:  # noqa: BLE001
				last_exc = exc
				msg = str(exc).lower()

				if any(token in msg for token in ["429", "resource_exhausted", "too many requests"]):
					if attempt < len(backoff_seconds):
						time.sleep(backoff_seconds[attempt])
						continue
					if "quota" in msg or "daily" in msg:
						raise RateLimitError(
							"Daily usage limit reached. The service will reset at midnight (Pacific Time)."
						) from exc
					raise RateLimitError(
						"The AI service is currently busy. Please try again in a few minutes."
					) from exc

				if any(token in msg for token in ["deadline exceeded", "timeout"]):
					raise AITimeoutError("AI request timed out. Please try again.") from exc

				if any(token in msg for token in ["api key", "unauthorized", "unauthenticated", "permission"]):
					raise ServerConfigurationError("Server configuration error.") from exc

				raise GeminiAPIError("Unable to reach AI service. Please try again later.") from exc

		raise GeminiAPIError("Unable to reach AI service. Please try again later.") from last_exc
