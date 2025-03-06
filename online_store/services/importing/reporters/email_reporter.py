"""The module responsible for implementing email-based BaseReporter."""

from logging import getLogger
import re
import os
from typing import List, Optional

from django.conf import settings

from utils.emails_utils import send_email
from utils.logs import get_logs_with_levels_from_memory_handler, save_logs_from_buffer_to_file

from .base import BaseReporter

logger = getLogger("main.services.importing.reporters")


class EmailReporter(BaseReporter):
    """Email Reporter."""

    REPORT_SUBJECT: str = "Import was {status}."

    def __init__(self, emails: Optional[List[str]] = None):
        if not emails:
            self.__emails = settings.ADMIN_EMAILS
        else:
            self.__emails = emails

    def report_about_success(self, import_file: str):
        """Report about successful importing by email."""
        email_subject: str = self.REPORT_SUBJECT.format(status="successful")
        email_text: str = self.SUCCESS_REPORT_TEXT.format(file_path=import_file)

        send_email(self.__emails, email_subject, email_text)

    @classmethod
    def __create_logfile(cls, logger_name: str) -> str:
        match = re.match(r".*\.(.*?)", logger_name)
        unique_logfile_name: str = match.group(1) + ".log"
        save_logs_from_buffer_to_file(filepath=unique_logfile_name, logger_name=logger_name)
        return unique_logfile_name

    @classmethod
    def __delete_logfile(cls, logfile: str):
        os.remove(logfile)

    def report_about_failure(self, import_file: str, logger_name: str = "celery"):
        """Report about unsuccessful importing by email."""
        email_subject: str = self.REPORT_SUBJECT.format(status="unsuccessful")
        email_text = self.FAILURE_REPORT_TEXT.format(
            file_path=import_file,
            error_logs=get_logs_with_levels_from_memory_handler(
                logger_name=logger_name,
                levels={"WARNING", "ERROR"},
            )
        )

        # create logfile
        unique_logfile = self.__create_logfile(logger_name)
        # send email with attachment
        send_email(self.__emails, email_subject, email_text, attach_files=[unique_logfile])
        # delete logfile
        self.__delete_logfile(unique_logfile)
