import io

from tests.conftest import SAMPLE_RESUME_TEXT


def _make_docx_bytes(text: str) -> bytes:
    import docx

    buffer = io.BytesIO()
    document = docx.Document()
    for line in text.split("\n"):
        document.add_paragraph(line)
    document.save(buffer)
    buffer.seek(0)
    return buffer.read()


def test_upload_valid_docx_resume(client):
    content = _make_docx_bytes(SAMPLE_RESUME_TEXT)
    response = client.post(
        "/api/resumes/upload",
        files={"file": ("resume.docx", content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["resume_file"]["extraction_status"] == "completed"
    assert body["candidate"] is not None
    assert body["candidate"]["email"] == "john.doe@example.com"


def test_upload_invalid_file_type(client):
    response = client.post(
        "/api/resumes/upload",
        files={"file": ("resume.txt", b"hello world", "text/plain")},
    )
    assert response.status_code == 415


def test_upload_empty_file(client):
    response = client.post(
        "/api/resumes/upload",
        files={"file": ("resume.pdf", b"", "application/pdf")},
    )
    assert response.status_code == 415


def test_get_resume_not_found(client):
    import uuid

    response = client.get(f"/api/resumes/{uuid.uuid4()}")
    assert response.status_code == 404


def test_upload_malformed_docx_fails_gracefully(client):
    response = client.post(
        "/api/resumes/upload",
        files={"file": ("resume.docx", b"not a real docx file", "application/octet-stream")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["resume_file"]["extraction_status"] == "failed"


def test_upload_valid_text_pdf_uses_pdfplumber(client):
    from tests.pdf_fixtures import make_text_pdf_bytes

    content = make_text_pdf_bytes(SAMPLE_RESUME_TEXT)
    response = client.post(
        "/api/resumes/upload",
        files={"file": ("resume.pdf", content, "application/pdf")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["resume_file"]["extraction_method"] == "pdfplumber"
    assert body["resume_file"]["extraction_status"] == "completed"


def test_upload_scanned_pdf_triggers_ocr_fallback(client):
    from tests.pdf_fixtures import make_scanned_pdf_bytes

    content = make_scanned_pdf_bytes("John Doe\nPython Developer\nSkills: Python FastAPI SQL\n5 years experience")
    response = client.post(
        "/api/resumes/upload",
        files={"file": ("scanned.pdf", content, "application/pdf")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["resume_file"]["extraction_method"] == "ocr"
    assert body["resume_file"]["extraction_status"] == "completed"
