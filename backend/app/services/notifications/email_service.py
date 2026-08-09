import logging

from app.core.config import Settings, get_settings
from app.services.notifications.base import EmailProvider

logger = logging.getLogger(__name__)


def build_email_provider(settings: Settings) -> EmailProvider | None:
    provider = settings.email_provider.lower()

    if provider == "smtp":
        if not settings.smtp_host or not settings.smtp_from_email:
            logger.warning("EMAIL_PROVIDER=smtp but SMTP_HOST/SMTP_FROM_EMAIL not configured")
            return None
        from app.services.notifications.smtp_provider import SMTPProvider

        return SMTPProvider(
            host=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password,
            from_email=settings.smtp_from_email,
            use_tls=settings.smtp_use_tls,
        )

    if provider == "sendgrid":
        if not settings.sendgrid_api_key or not settings.sendgrid_from_email:
            logger.warning("EMAIL_PROVIDER=sendgrid but SENDGRID_API_KEY/SENDGRID_FROM_EMAIL not configured")
            return None
        from app.services.notifications.sendgrid_provider import SendGridProvider

        return SendGridProvider(api_key=settings.sendgrid_api_key, from_email=settings.sendgrid_from_email)

    return None


class EmailService:
    def __init__(self, provider: EmailProvider | None = None) -> None:
        self._provider = provider if provider is not None else build_email_provider(get_settings())

    @property
    def is_configured(self) -> bool:
        return self._provider is not None

    def send(self, to_email: str, subject: str, html_body: str) -> bool:
        if not self._provider:
            logger.info("Email not sent to %s (no email provider configured): %s", to_email, subject)
            return False
        return self._provider.send_email(to_email, subject, html_body)