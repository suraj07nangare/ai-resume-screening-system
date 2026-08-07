import pdfplumber

from app.core.exceptions import ExtractionError


def extract_text_from_pdf(file_path: str) -> str:
    try:
        chunks: list[str] = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if page_text:
                    chunks.append(page_text)
        return "\n".join(chunks).strip()
    except Exception as exc:
        raise ExtractionError(f"Failed to read PDF file: {exc}") from exc
