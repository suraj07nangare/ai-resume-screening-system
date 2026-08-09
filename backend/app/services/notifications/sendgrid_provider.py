import logging

import httpx

from app.services.notifications.base import EmailProvider

logger = logging.getLogger(__name__)


class SendGridProvider(EmailProvider):
    def __init__(self, api_key: str, from_email: str) -> None:
        self._api_key = api_key
        self._from_email = from_email

    def send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        try:
            response = httpx.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "personalizations": [{"to": [{"email": to_email}]}],
                    "from": {"email": self._from_email},
                    "subject": subject,
                    "content": [{"type": "text/html", "value": html_body}],
                },
                timeout=15.0,
            )
            response.raise_for_status()
            return True
        except httpx.HTTPError as exc:
            logger.error("SendGrid email send failed for %s: %s", to_email, exc)
            return False