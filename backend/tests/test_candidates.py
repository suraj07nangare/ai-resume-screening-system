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


def _upload_candidate(client, text: str = SAMPLE_RESUME_TEXT):
    content = _make_docx_bytes(text)
    response = client.post(
        "/api/resumes/upload",
        files={"file": ("resume.docx", content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    return response.json()["candidate"]


def test_candidate_search_by_skill(client):
    _upload_candidate(client)
    response = client.get("/api/candidates/search", params={"skill": "python"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert any("python" in [s.lower() for s in item["skills"]] for item in body["items"])


def test_candidate_search_by_min_experience(client):
    _upload_candidate(client)
    response = client.get("/api/candidates/search", params={"min_experience": 10})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 0


def test_get_candidate_detail(client):
    candidate = _upload_candidate(client)
    response = client.get(f"/api/candidates/{candidate['id']}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == candidate["id"]
    assert len(body["skills"]) > 0


def test_get_candidate_not_found(client):
    import uuid

    response = client.get(f"/api/candidates/{uuid.uuid4()}")
    assert response.status_code == 404


def test_update_candidate_status(client):
    candidate = _upload_candidate(client)
    response = client.patch(f"/api/candidates/{candidate['id']}/status", json={"status": "shortlisted"})
    assert response.status_code == 200
    assert response.json()["status"] == "shortlisted"

    response = client.get(f"/api/candidates/{candidate['id']}")
    assert response.json()["status"] == "shortlisted"


def test_update_candidate_status_not_found(client):
    import uuid

    response = client.patch(f"/api/candidates/{uuid.uuid4()}/status", json={"status": "rejected"})
    assert response.status_code == 404


def test_update_candidate_status_invalid_value(client):
    candidate = _upload_candidate(client)
    response = client.patch(f"/api/candidates/{candidate['id']}/status", json={"status": "not_a_status"})
    assert response.status_code == 422


def test_candidate_search_by_status(client):
    candidate = _upload_candidate(client)
    client.patch(f"/api/candidates/{candidate['id']}/status", json={"status": "shortlisted"})

    response = client.get("/api/candidates/search", params={"status": "shortlisted"})
    assert response.status_code == 200
    assert response.json()["total"] == 1

    response = client.get("/api/candidates/search", params={"status": "rejected"})
    assert response.json()["total"] == 0
