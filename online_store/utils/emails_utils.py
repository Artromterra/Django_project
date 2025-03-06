"""The module responsible for sending emails."""
from logging import getLogger
from typing import Optional, List

from django.core.mail import EmailMessage
from django.conf import settings


logger = getLogger("main.utils.email")


def send_email(to: List[str], subject: str, text: str, attach_files: Optional[List[str]] = None) -> None:
    """
    Send an email.

    :param to: The list of email addresses to send the message to.
    :param subject: Email subject.
    :param text: Email content.
    :param attach_files: Files to attach to the email.
    """
    try:
        email = EmailMessage(
            subject=subject,
            body=text,
            from_email=settings.EMAIL_HOST_USER,
            to=to,
        )
        for file in attach_files:
            email.attach_file(file)
        email.send()
    except Exception as exc:
        logger.exception("Error when sending an email. exc=%s", str(exc))
    else:
        logger.info("The email was sent successfully.")
