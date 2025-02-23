"""The module responsible for sending emails."""

from email.message import EmailMessage
from email.mime.base import MIMEBase
from email import encoders
import smtplib
from logging import getLogger
from typing import Optional, List

from django.conf import settings

logger = getLogger("main.utils.email")


def send_email(to: str, subject: str, text: str, attach_files: Optional[List[str]] = None) -> None:
    """
    Send an email.

    :param to: The email address to send the message to.
    :param subject: Email subject.
    :param text: Email content.
    :param attach_files: Files to attach to the email.
    """
    sender = settings.EMAIL
    sender_password = settings.EMAIL_PASSWORD

    try:
        logger.debug("Connecting...")
        mail_lib = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
        logger.debug("Login...")
        mail_lib.login(sender, sender_password)

        msg: EmailMessage = EmailMessage()
        msg.set_content(text)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to

        # attach
        if attach_files:
            for attach_file in attach_files:
                with open(attach_file, "rb") as file:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(file.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f"attachment; filename={file}")

                msg.attach(part)

        logger.debug("Sending email...")
        mail_lib.send_message(msg)
        mail_lib.quit()
    except Exception as exc:
        logger.exception("Error when sending an email. exc=%s", str(exc))
    else:
        logger.info("The email was sent successfully.")
