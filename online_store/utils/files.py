"""The module responsible for working with files."""

import os
import shutil


def move_file_depends_on_import_result(
        was_successful: bool,
        file_path: str,
        success_dir: str,
        failure_dir: str
) -> str:
    """
    Move the file depending on the result of the import.

    :param was_successful: True, if all rows from xlsx file were converted to Product models.
    :param file_path: Import file path.
    :param success_dir: The directory to move the import file to in case of success.
    :param failure_dir: The directory to move the import file to in case of failure.
    :return: Target path.
    """
    _, filename = os.path.split(file_path)

    if was_successful:
        target_path: str = os.path.join(success_dir, filename)
    else:
        target_path = os.path.join(failure_dir, filename)

    shutil.move(file_path, target_path)
    return target_path
