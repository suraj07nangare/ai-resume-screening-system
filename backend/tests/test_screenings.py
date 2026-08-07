import io

from tests.conftest import SAMPLE_JD_TEXT, SAMPLE_RESUME_TEXT


def _make_docx_bytes(text: str) -> bytes:
    import docx

    buffer = io.BytesIO()
    document = docx.Document()
    for line in text.split("\n"):
        document.add_paragraph(line)
    document.save(buffer)
    buffer.seek(0)
    return buffer.read()


def _setup_candidate_and_job(client):
    content = _make_docx_bytes(SAMPLE_RESUME_TEXT)
    candidate_resp = client.post(
        "/api/resumes/upload",
        files={"file": ("resume.docx", content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    candidate = candidate_resp.json()["candidate"]

    job_resp = client.post("/api/jobs", json={"title": "Backend Engineer", "raw_description": SAMPLE_JD_TEXT})
    job = job_resp.json()

    return candidate, job


def test_create_screening_returns_score_in_range(client):
    candidate, job = _setup_candidate_and_job(client)
    response = client.post("/api/screenings", json={"candidate_id": candidate["id"], "job_id": job["id"]})
    assert response.status_code == 201
    body = response.json()
    assert 0 <= body["overall_score"] <= 100
    assert "python" in [s.lower() for s in body["matched_skills"]]
    assert body["explanation"]


def test_get_screening(client):
    candidate, job = _setup_candidate_and_job(client)
    create_resp = client.post("/api/screenings", json={"candidate_id": candidate["id"], "job_id": job["id"]})
    screening_id = create_resp.json()["id"]

    response = client.get(f"/api/screenings/{screening_id}")
    assert response.status_code == 200
    assert response.json()["id"] == screening_id


def test_screening_missing_candidate(client):
    import uuid

    _, job = _setup_candidate_and_job(client)
    response = client.post("/api/screenings", json={"candidate_id": str(uuid.uuid4()), "job_id": job["id"]})
    assert response.status_code == 404


def test_screening_missing_job(client):
    import uuid

    candidate, _ = _setup_candidate_and_job(client)
    response = client.post("/api/screenings", json={"candidate_id": candidate["id"], "job_id": str(uuid.uuid4())})
    assert response.status_code == 404


def test_job_rankings(client):
    candidate, job = _setup_candidate_and_job(client)
    client.post("/api/screenings", json={"candidate_id": candidate["id"], "job_id": job["id"]})

    response = client.get(f"/api/jobs/{job['id']}/rankings")
    assert response.status_code == 200
    body = response.json()
    assert len(body["rankings"]) == 1
    assert body["rankings"][0]["rank"] == 1
