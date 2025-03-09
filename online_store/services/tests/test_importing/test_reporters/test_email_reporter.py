from unittest.mock import patch, MagicMock
from django.test import TestCase

from services.importing.reporters.email_reporter import EmailReporter


class TestEmailReporter(TestCase):
    """Test case for EmailReporter."""

    @patch("services.importing.reporters.email_reporter.send_email")
    def test_report_about_success(self, mock_send_email: MagicMock):
        """Test EmailReporter.report_about_success."""
        emails = ["admin1@test.com", "admin2@test.com"]
        reporter = EmailReporter(emails)
        import_file = "test_import_file.xlsx"

        subject = reporter.REPORT_SUBJECT.format(status="successful")
        text = reporter.SUCCESS_REPORT_TEXT.format(file_path=import_file)

        reporter.report_about_success(import_file)

        mock_send_email.assert_called_once_with(emails, subject, text)
