import os

from django.test import TestCase
from django.conf import settings

from services.importing.importers.xlsx import XLSXImporter
from services.importing.excs import NotFoundData


class TestXLSXImporter(TestCase):
    """Test case for testing XLSXImporter."""

    def setUp(self):
        self.abs_path = "/home/vladimir/learning/django_diploma/online_store/services/tests/test_importing/test_files"
        self.dir_with_test_files = (settings.BASE_DIR / "services" / "tests" /
                                       "test_importing" / "test_files")

        correct_import_file: str = str(self.dir_with_test_files / "correct_import_file.xlsx")
        self.importer = XLSXImporter(correct_import_file)

        empty_file: str = str(self.dir_with_test_files / "empty_file.xlsx")
        self.importer_without_sheets = XLSXImporter(empty_file)

        invalid_headers_file: str = str(self.dir_with_test_files / "invalid_headers.xlsx")
        self.importer_with_invalid_headers = XLSXImporter(invalid_headers_file)

    def test_import_categories(self):
        """Test importing categories."""
        try:
            for _ in self.importer.import_categories():
                pass
        except Exception as exc:
            self.fail(exc)

    def test_import_products(self):
        """Test importing products."""
        try:
            for _ in self.importer.import_products():
                pass
        except Exception as exc:
            self.fail(exc)

    def test_import_sellers(self):
        """Test importing sellers."""
        try:
            for _ in self.importer.import_sellers():
                pass
        except Exception as exc:
            self.fail(exc)

    def test_import_product_seller(self):
        """Test importing ProductSeller."""
        try:
            for _ in self.importer.import_products_sellers():
                pass
        except Exception as exc:
            self.fail(exc)

    def test_import_from_file_without_sheet_products(self):
        """Test importing products without sheet 'products'."""
        try:
            products = list(self.importer_without_sheets.import_products())
        except Exception as exc:
            self.fail(exc)
        else:
            self.assertEqual(len(products), 0)

    def test_import_from_file_with_invalid_headers(self):
        """Test importing products from sheet with invalid headers."""
        try:
            products = list(self.importer_with_invalid_headers.import_products())
        except Exception as exc:
            self.fail(exc)
        else:
            self.assertEqual(len(products), 0)
