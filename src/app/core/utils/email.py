import smtplib
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from jinja2 import Template

from app.core.config import settings
import structlog

@dataclass
class EmailData:
    html_content: str
    subject: str
    

logger = structlog.get_logger(__name__)

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.EMAILS_FROM_EMAIL,
    MAIL_FROM_NAME=settings.EMAILS_FROM_NAME,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_SSL_TLS=settings.SMTP_TLS,
    MAIL_STARTTLS=settings.SMTP_SSL,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


def render_email_templates(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (
        Path(__file__).parent.parent.parent / "email_template" / "build" / template_name
    ).read_text()
    
    html_content = Template(template_str).render(context)
    return html_content

async def send_email(
    *, email_to: str, subject: str = "", html_content: str = ""
) -> bool:
    
    message = MessageSchema(
        subject=subject, recipients=[email_to], body=html_content, subtype="html"
    )
    
    fm = FastMail(conf)
    try:
        logger.info("📧sending email", email=email_to, subject=subject)
        await fm.send_message(message)
        logger.info("✅email sent", email=email_to, subject=subject)
        return True
    except smtplib.SMTPException as e:
        logger.error("❌email not sent", email=email_to, subject=subject)
        return False

async def send_otp_verification_email(email_to: str, first_name: str, otp_code: str) -> None:
    
    template = "otp_verification.html"
    context = {
        "user_name": first_name,
        "otp_code": otp_code,
        "expiry_minutes": settings.OTP_EXPIRY_TIME,
        "year": datetime.now(timezone.utc).year
    }

    html_content = render_email_templates(template_name=template, context=context)
    await send_email(
        email_to=email_to,
        subject="Email Verification",
        html_content=html_content
    )