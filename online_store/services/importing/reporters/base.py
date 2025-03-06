"""The module responsible for the reporter base class."""

from abc import ABC, abstractmethod


class BaseReporter(ABC):
    """Base reporter class."""

    SUCCESS_REPORT_TEXT: str = "Import file {file_path} was successful."
    FAILURE_REPORT_TEXT: str = ("Uncritical errors occurred during import file {file_path}.\n"
                                "Logs with level WARNING and ERROR:\n{error_logs}")

    @abstractmethod
    def report_about_success(self, import_file: str):
        """Report about successful import."""
        pass

    @abstractmethod
    def report_about_failure(self, import_file: str, **kwargs):
        """Report about unsuccessful import"""
        pass
