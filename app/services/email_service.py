from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EmailService:
    async def send_password_reset(self, to_email: str, full_name: str, reset_link: str) -> None:
        subject = "Reset your password"
        body = (
            f"Hi {full_name},\n\n"
            "We received a request to reset your password.\n"
            f"Use the link below to set a new one (valid for {settings.RESET_TOKEN_EXPIRE_MINUTES} minutes):\n\n"
            f"{reset_link}\n\n"
            "If you didn't request this, you can safely ignore this email."
        )
        await self._send(to_email, subject, body)

    async def _send(self, to_email: str, subject: str, body: str) -> None:
        if not settings.EMAIL_ENABLED:
            logger.info(f"[email disabled] To: {to_email} | {subject}\n{body}")
            return

        message = EmailMessage()
        message["From"] = settings.SMTP_FROM
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)

        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER or None,
            password=settings.SMTP_PASSWORD or None,
            start_tls=True,
        )
        logger.info(f"Password reset email sent to {to_email}")
