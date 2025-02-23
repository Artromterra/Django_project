"""The module responsible for sending emails."""

from logging.handlers import TimedRotatingFileHandler
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email import encoders
import smtplib
from logging import getLogger
from typing import Optional, List, Tuple

from django.conf import settings


from .logs import get_logs_with_levels_from_file

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


REPORT_SUBJECT: str = "Import was {status}."
SUCCESS_REPORT_TEXT: str = "Import file {file_path} was successful."
FAILURE_REPORT_TEXT: str = ("Uncritical errors occurred during import file {file_path}.\n"
                            "Logs with errors:\n{error_logs}")


def compile_report(
        was_successful: bool,
        file_path: str,
        log_file_path: str
) -> Tuple[str, str]:
    """
    Collect the subject and email text depending on the success of the import.

    :param was_successful: True, if import was successful, else False.
    :param file_path: Import file path.
    :param log_file_path: Log file path.
    :return: Email subject and email text.
    """
    if was_successful:
        email_subject: str = REPORT_SUBJECT.format(status="successful")
        email_text: str = SUCCESS_REPORT_TEXT.format(file_path=file_path)
    else:
        email_subject = REPORT_SUBJECT.format(status="unsuccessful")

        # print all logs from buffer to file
        for handler in logger.handlers:
            if isinstance(handler, TimedRotatingFileHandler):
                handler.flush()
                break

        email_text = FAILURE_REPORT_TEXT.format(
            file_path=file_path,
            error_logs=get_logs_with_levels_from_file(
                ("WARNING", "ERROR"),
                log_file_path
            )
        )

    return email_subject, email_text
