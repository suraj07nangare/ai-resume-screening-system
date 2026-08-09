import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.services.notifications.base import EmailProvider

logger = logging.getLogger(__name__)


class SMTPProvider(EmailProvider):
    def __init__(
        self,
        host: str,
        port: int,
        username: str | None,
        password: str | None,
        from_email: str,
        use_tls: bool = True,
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._from_email = from_email
        self._use_tls = use_tls

    def send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self._from_email
        message["To"] = to_email
        message.attach(MIMEText(html_body, "html"))

        try:
            with smtplib.SMTP(self._host, self._port, timeout=15) as server:
                if self._use_tls:
                    server.starttls()
                if self._username and self._password:
                    server.login(self._username, self._password)
                server.sendmail(self._from_email, [to_email], message.as_string())
            return True
        except Exception as exc:  # noqa: BLE001
            logger.error("SMTP email send failed for %s: %s", to_email, exc)
            return False