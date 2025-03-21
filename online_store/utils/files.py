
import os
from typing import List
from uuid import uuid4
import re
from logging import getLogger

logger = getLogger("main.utils.files")


def get_files_in_dir(target_dir: str) -> List[str]:
    """Return list of file names in dir. Only files."""
    files = [
        file for file in os.listdir(target_dir)
        if os.path.isfile(os.path.join(target_dir, file))
    ]
    return files


def generate_unique_filename(filename: str) -> str:
    """Add a random salt to the file name."""
    logger.debug("filename: %s", filename)
    match = re.search(r"(.*)\.(.*)?", filename)
    if not match:
        raise ValueError(f"Invalid filename (must be name.extension). {filename=}")
    name = match.group(1)
    logger.debug("name: %s", name)
    extension = match.group(2)
    logger.debug("extension: %s", extension)
    salt = str(uuid4())
    logger.debug("unique salt: %s", salt)
    unique_filename: str = name + salt + "." + extension
    logger.debug("unique filename: %s", unique_filename)
    return unique_filename


def create_dir_if_not_exists(dir_: str) -> None:
    """Create dir if not exists."""
    if not os.path.exists(dir_):
        os.makedirs(dir_)

def delete_files(filepaths: List[str]) -> None:
    """Delete files."""
    for filepath in filepaths:
        if os.path.exists(filepath):
            os.remove(filepath)
