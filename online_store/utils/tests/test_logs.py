"""The module responsible for testing the module logs.py."""

from typing import Tuple, List
from logging import getLogger
import random

from django.test import TestCase
from django.conf import settings

from ..logs import get_logs_with_levels_from_file


logger = getLogger("main.tests")


class TestReportText(TestCase):
    """Test case for func get_logs_with_levels_from_file."""

    def setUp(self):
        self.log_file: str = settings.BASE_DIR / "utils" / "tests" / "test_logfile.log"
        self.levels: Tuple[str, ...] = (
            "WARNING",
            "ERROR",
            "INFO",
            "DEBUG",
        )

    def test_getting_logs_with_levels_from_file(self):
        """Test compiling report in case successful import."""
        random_levels: Tuple[str, ...] = tuple(random.choices(self.levels, k=random.randint(0, len(self.levels))))
        random_levels = tuple(set(random_levels))

        logs: List[str] = get_logs_with_levels_from_file(random_levels, str(self.log_file))
        with open(self.log_file, "r") as file:
            logs_text: str = file.read()

        self.assertEqual(len(logs), sum(logs_text.count(level) for level in random_levels))
