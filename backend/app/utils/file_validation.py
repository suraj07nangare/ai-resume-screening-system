from app.core.config import get_settings
from app.core.exceptions import FileTooLargeError, UnsupportedFileError

ALLOWED_EXTENSIONS = {"pdf", "docx"}


def validate_upload(filename: str, size_bytes: int) -> str:
    if "." not in filename:
        raise UnsupportedFileError("File must have an extension of .pdf or .docx")

    extension = filename.rsplit(".", 1)[-1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise UnsupportedFileError(f"Unsupported file type: .{extension}. Allowed types: pdf, docx")

    settings = get_settings()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if size_bytes > max_bytes:
        raise FileTooLargeError(f"File exceeds maximum size of {settings.max_upload_size_mb}MB")

    if size_bytes == 0:
        raise UnsupportedFileError("Uploaded file is empty")

    return extension
