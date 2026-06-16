from __future__ import annotations


class StudyForgeError(Exception):
    status_code: int = 400
    error: str = "StudyForgeError"

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class FileTooLargeError(StudyForgeError):
    status_code = 413
    error = "FileTooLarge"


class UnsupportedFileTypeError(StudyForgeError):
    status_code = 415
    error = "UnsupportedFileType"


class GeminiAPIError(StudyForgeError):
    status_code = 502
    error = "GeminiAPIError"


class ServerConfigurationError(StudyForgeError):
    status_code = 500
    error = "ServerConfigurationError"


class ContentBlockedError(StudyForgeError):
    status_code = 422
    error = "ContentBlocked"


class AITimeoutError(StudyForgeError):
    status_code = 504
    error = "AITimeout"


class RateLimitError(StudyForgeError):
    status_code = 429
    error = "RateLimitError"


class TextExtractionError(StudyForgeError):
    status_code = 400
    error = "TextExtractionError"


class EmptyFileError(StudyForgeError):
    status_code = 400
    error = "EmptyFile"
