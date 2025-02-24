"""The module responsible for working with xlsx files."""

from openpyxl import load_workbook, Workbook
from openpyxl.worksheet.worksheet import Worksheet
from typing import Dict, Any, Generator


def xlsx_reader(filename: str) -> Generator[Dict[str, Any], None, None]:
    """
    Generate dictionaries from xlsx file strings.

    Using the opengl library, the function does not load the entire file into memory,
    but reads it line by line. In the first line, the file should have column headings.
    Dictionaries will be compiled based on these headings (headers as keys).

    :param filename: File name
    """
    wb: Workbook = load_workbook(filename, read_only=True)
    ws: Worksheet = wb.active

    ws_iter = ws.iter_rows()
    print(f"{str(ws_iter)=}")
    headers = next(ws_iter)
    print(f"{str(headers)=}")

    for row in ws_iter:
        print(f"{str(row)=}")
        yield {
            header.value: cell.value
            for cell in row
            for header in headers
        }

