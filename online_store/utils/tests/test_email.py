"""The module responsible for testing the module email.py."""
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.conf import settings

from ..emails_utils import send_email


class SendEmailTestCase(TestCase):
    def setUp(self):
        self.attachments = [str(settings.BASE_DIR / "utils" / "tests" / "attachment.txt")]

    @patch("utils.emails_utils.EmailMessage")
    def test_send_email(self, mock_email_message: MagicMock):
        mock_email_instance = mock_email_message.return_value
        mock_email_instance.send.return_value = None

        to = ["email1@test.com", "email2@test.com"]
        subject = "Test Subject"
        text = "Test Body"
        attach_files = self.attachments

        send_email(to=to, subject=subject, text=text, attach_files=attach_files)
        print(mock_email_message.call_args)

        mock_email_message.assert_called_once_with(
            subject=subject,
            body=text,
            from_email=settings.EMAIL_HOST_USER,
            to=to,
        )
        for attach in self.attachments:
            mock_email_instance.attach_file.assert_any_call(attach)

        mock_email_instance.send.assert_called_once()
