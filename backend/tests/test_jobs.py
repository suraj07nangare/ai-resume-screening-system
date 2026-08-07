from tests.conftest import SAMPLE_JD_TEXT


def test_create_job(client):
    response = client.post(
        "/api/jobs",
        json={"title": "Backend Engineer", "raw_description": SAMPLE_JD_TEXT},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Backend Engineer"
    assert "python" in [s.lower() for s in body["required_skills"]]


def test_get_job_not_found(client):
    import uuid

    response = client.get(f"/api/jobs/{uuid.uuid4()}")
    assert response.status_code == 404
