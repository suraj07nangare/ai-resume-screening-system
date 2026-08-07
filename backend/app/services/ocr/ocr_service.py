import pytesseract
from pdf2image import convert_from_path

from app.core.exceptions import ExtractionError


def extract_text_via_ocr(file_path: str) -> str:
    try:
        images = convert_from_path(file_path)
        chunks: list[str] = []
        for image in images:
            page_text = pytesseract.image_to_string(image) or ""
            if page_text:
                chunks.append(page_text)
        return "\n".join(chunks).strip()
    except Exception as exc:
        raise ExtractionError(f"OCR extraction failed: {exc}") from exc
