"""The module responsible for testing the module email.py."""
from django.test import TestCase
from django.conf import settings

from ..email import compile_report, SUCCESS_REPORT_TEXT, REPORT_SUBJECT


class TestReportText(TestCase):

    def setUp(self):
        self.file_path = "example.xlsx"
        self.log_file_path = settings.BASE_DIR / "utils" / "tests" / "test_logfile.log"

    def test_compiling_report_with_successful_import(self):
        """Test compiling report in case successful import."""
        subject, text = compile_report(True, self.file_path, self.log_file_path)
        self.assertEqual(subject, REPORT_SUBJECT.format(status="successful"))
        self.assertEqual(text, SUCCESS_REPORT_TEXT.format(file_path=self.file_path))

    def test_compiling_report_with_unsuccessful_import(self):
        """Test compiling report in case unsuccessful import."""
        subject, text = compile_report(False, self.file_path, self.log_file_path)
        self.assertEqual(subject, REPORT_SUBJECT.format(status="unsuccessful"))
        self.assertIn("ERROR", text)
        self.assertIn("WARNING", text)
        self.assertNotIn("DEBUG", text)
        self.assertNotIn("INFO", text)
