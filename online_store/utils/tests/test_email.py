"""The module responsible for testing the module email.py."""
from django.test import TestCase

from ..email import compile_report, SUCCESS_REPORT_TEXT, REPORT_SUBJECT, FAILURE_REPORT_TEXT


class TestReportText(TestCase):

    def setUp(self):
        self.file_path = "example.xlsx"
        self.log_file_path = "log_example.log"

    def test_compiling_report_with_successful_import(self):
        """Test compiling report in case successful import."""
        subject, text = compile_report(True, self.file_path, self.log_file_path)
        self.assertEqual(subject, REPORT_SUBJECT.format(status="successful"))
        self.assertEqual(text, SUCCESS_REPORT_TEXT.format(file_path=self.file_path))
