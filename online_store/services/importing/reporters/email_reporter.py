"""The module responsible for implementing email-based BaseReporter."""

from logging import getLogger
import os
from typing import List, Optional

from django.conf import settings

from utils.emails_utils import send_email
from utils.logs.loggers.separator import SeparatorLogger

from .base import BaseReporter

logger = getLogger("main.services.importing.reporters")


class EmailReporter(BaseReporter):
    """Email Reporter."""

    REPORT_SUBJECT: str = "Import was {status}."

    def __init__(self, separator_logger: SeparatorLogger, emails: Optional[List[str]] = None):
        self.__separator_logger = separator_logger

        if not emails:
            self.__emails = settings.ADMIN_EMAILS
        else:
            self.__emails = emails

    def report_about_success(self, import_file: str):
        """Report about successful importing by email."""
        email_subject: str = self.REPORT_SUBJECT.format(status="successful")
        email_text: str = self.SUCCESS_REPORT_TEXT.format(file_path=import_file)
        self.__create_logfile()
        send_email(self.__emails, email_subject, email_text)


    def __create_logfile(self) -> str:
        unique_id = self.__separator_logger.unique_id
        unique_logfile_name: str = ".".join((unique_id, "log"))
        separate_handler = self.__separator_logger.handler
        separate_handler.save(
            unique_id=unique_id,
            filename=unique_logfile_name,
            extract=True,
        )
        return unique_logfile_name

    @classmethod
    def __delete_logfile(cls, logfile: str):
        os.remove(logfile)

    def report_about_failure(self, import_file: str):
        """Report about unsuccessful importing by email."""
        email_subject: str = self.REPORT_SUBJECT.format(status="unsuccessful")

        separate_handler = self.__separator_logger.handler
        email_text = self.FAILURE_REPORT_TEXT.format(
            file_path=import_file,
            error_logs="<br>".join(separate_handler.get_logs(
                unique_id=self.__separator_logger.unique_id,
                levels={"WARNING", "ERROR", "CRITICAL"}),
            )
        )

        # create logfile
        unique_logfile = self.__create_logfile()
        # send email with attachment
        send_email(self.__emails, email_subject, email_text, attach_files=[unique_logfile])
        # # delete logfile
        # self.__delete_logfile(unique_logfile)
