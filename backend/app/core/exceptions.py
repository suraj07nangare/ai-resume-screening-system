class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=404)


class ValidationAppError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=422)


class UnsupportedFileError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=415)


class FileTooLargeError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=413)


class ExtractionError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=422)


class LLMProviderError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=502)
