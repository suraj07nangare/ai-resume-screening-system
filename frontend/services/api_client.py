import os

import requests

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


class ApiError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def _handle(response: requests.Response):
    if response.status_code >= 400:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        raise ApiError(response.status_code, detail)
    if response.status_code == 204:
        return None
    return response.json()


def get_health():
    return _handle(requests.get(f"{API_BASE_URL}/api/health", timeout=10))


def upload_resume(filename: str, file_bytes: bytes, content_type: str):
    files = {"file": (filename, file_bytes, content_type)}
    return _handle(requests.post(f"{API_BASE_URL}/api/resumes/upload", files=files, timeout=60))


def create_job(title: str, raw_description: str):
    payload = {"title": title, "raw_description": raw_description}
    return _handle(requests.post(f"{API_BASE_URL}/api/jobs", json=payload, timeout=60))


def list_jobs(limit: int = 100):
    return _handle(requests.get(f"{API_BASE_URL}/api/jobs", params={"limit": limit}, timeout=30))


def get_job(job_id: str):
    return _handle(requests.get(f"{API_BASE_URL}/api/jobs/{job_id}", timeout=30))


def list_candidates(limit: int = 50, offset: int = 0):
    params = {"limit": limit, "offset": offset}
    return _handle(requests.get(f"{API_BASE_URL}/api/candidates", params=params, timeout=30))


def search_candidates(**filters):
    params = {k: v for k, v in filters.items() if v not in (None, "")}
    return _handle(requests.get(f"{API_BASE_URL}/api/candidates/search", params=params, timeout=30))


def update_candidate_status(candidate_id: str, status: str):
    return _handle(
        requests.patch(
            f"{API_BASE_URL}/api/candidates/{candidate_id}/status", json={"status": status}, timeout=30
        )
    )


def get_candidate(candidate_id: str):
    return _handle(requests.get(f"{API_BASE_URL}/api/candidates/{candidate_id}", timeout=30))


def create_screening(candidate_id: str, job_id: str):
    payload = {"candidate_id": candidate_id, "job_id": job_id}
    return _handle(requests.post(f"{API_BASE_URL}/api/screenings", json=payload, timeout=60))


def get_job_rankings(job_id: str):
    return _handle(requests.get(f"{API_BASE_URL}/api/jobs/{job_id}/rankings", timeout=30))
