from urllib.parse import quote

from app.core.config import Settings


def build_scheduling_link(settings: Settings, candidate_name: str, candidate_email: str) -> str | None:
    if not settings.calcom_scheduling_url:
        return None

    base_url = settings.calcom_scheduling_url.rstrip("/")
    name_param = quote(candidate_name)
    email_param = quote(candidate_email)
    return f"{base_url}?name={name_param}&email={email_param}"