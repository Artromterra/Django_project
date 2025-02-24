
from typing import List, Dict, Any
import random

from django.test import TestCase
from django.conf import settings
import openpyxl

from ..xlsx import xlsx_reader


def generate_test_import_file(filename: str = "test_import_file.xlsx") -> List[List[str]]:
    wb = openpyxl.Workbook()
    ws = wb.active

    data: List[List[str]] = [["test_A", "test_B", "test_C"]]
    data.extend([
        [random.randint(1, 10), random.uniform(1, 10), "random_str"]
        for _ in range(100)
    ])
    for row in range(len(data)):
        for col in range(len(data[row])):
            ws.cell(row=row + 1, column=col + 1, value=data[row][col])

    wb.save(filename)
    return data


class TestXLSXReader(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text_excel_path: str = settings.BASE_DIR / "utils" / "tests" / "test_import_file.xlsx"
        cls.data: List[List[str]] = generate_test_import_file(str(cls.text_excel_path))

    def test_xlsx_reader(self):
        headers: List[str] = self.data[0]
        for row, read_dict in zip(self.data[1:], xlsx_reader(self.text_excel_path)):
            print(f"{row=}")
            print(f"{read_dict=}")
            for num_header, header in enumerate(headers):
                self.assertEqual(read_dict[header], row[num_header])


if __name__ == "__main__":
    generate_test_import_file()
