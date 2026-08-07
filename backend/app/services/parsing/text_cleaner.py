from app.utils.normalization import clean_text


def clean_extracted_text(text: str) -> str:
    return clean_text(text)
