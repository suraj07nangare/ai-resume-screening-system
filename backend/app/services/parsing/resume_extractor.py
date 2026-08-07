from app.core.config import get_settings
from app.core.exceptions import ExtractionError
from app.services.ocr.ocr_service import extract_text_via_ocr
from app.services.parsing.docx_parser import extract_text_from_docx
from app.services.parsing.pdf_parser import extract_text_from_pdf
from app.services.parsing.text_cleaner import clean_extracted_text


def extract_resume_text(file_path: str, extension: str) -> tuple[str, str]:
    settings = get_settings()

    if extension == "docx":
        raw_text = extract_text_from_docx(file_path)
        return clean_extracted_text(raw_text), "docx"

    if extension == "pdf":
        raw_text = extract_text_from_pdf(file_path)
        if len(raw_text.strip()) >= settings.ocr_min_text_chars:
            return clean_extracted_text(raw_text), "pdfplumber"

        ocr_text = extract_text_via_ocr(file_path)
        if len(ocr_text.strip()) < settings.ocr_min_text_chars:
            raise ExtractionError("No meaningful text could be extracted from this document, even with OCR")
        return clean_extracted_text(ocr_text), "ocr"

    raise ExtractionError(f"Unsupported file extension: {extension}")
