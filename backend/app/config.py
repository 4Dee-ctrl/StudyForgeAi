from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	gemini_api_key: str = Field(default="", validation_alias="GEMINI_API_KEY")
	allowed_origins: str = Field(
		default="http://localhost:5173",
		validation_alias="ALLOWED_ORIGINS",
	)
	max_file_size_mb: int = Field(default=10, validation_alias="MAX_FILE_SIZE_MB")
	max_text_length: int = Field(default=50000, validation_alias="MAX_TEXT_LENGTH")
	rate_limit_per_minute: int = Field(default=60, validation_alias="RATE_LIMIT_PER_MINUTE")
	gemini_model: str = Field(default="gemini-3.1-flash-lite", validation_alias="GEMINI_MODEL")
	gemini_fallback_models: str = Field(
		default="gemini-2.5-flash-lite",
		validation_alias="GEMINI_FALLBACK_MODELS",
	)

	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		extra="ignore",
	)

	@property
	def allowed_origins_list(self) -> list[str]:
		return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

	@property
	def gemini_model_chain(self) -> list[str]:
		models = [self.gemini_model]
		models.extend(
			model.strip()
			for model in self.gemini_fallback_models.split(",")
			if model.strip()
		)

		deduped: list[str] = []
		for model in models:
			if model not in deduped:
				deduped.append(model)
		return deduped


settings = Settings()
