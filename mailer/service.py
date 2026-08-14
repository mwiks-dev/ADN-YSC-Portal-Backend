import os
import logging
from datetime import date
from fastapi_mail import FastMail, MessageSchema, MessageType
from .config import mail_config

logger = logging.getLogger(__name__)

fm = FastMail(mail_config)

FRONT_END_URL = os.getenv("FRONT_END_URL", "http://localhost:3560")
SUPPORT_URL = os.getenv("SUPPORT_URL", "mailto:support@adn-youth.org")

async def send_welcome_email(email: str, name: str) -> None:
    try:
        message = MessageSchema(
            subject="Welcome to the Family!",
            recipients=[email],
            template_body={
                "name": name,
                "email": email,
                "FRONT_END_URL": f"{FRONT_END_URL}/login",
                "SUPPORT_URL": SUPPORT_URL,
                "year": date.today().year,
            },
            subtype=MessageType.html,
        )
        await fm.send_message(message, template_name="welcome.html")
    except Exception:
        logger.exception("Failed to send welcome email to %s", email)