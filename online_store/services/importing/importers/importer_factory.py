"""The module responsible for the importer object factory."""

from typing import Dict, Type, Tuple
import re

from services.importing.importers.base import BaseImporter
from services.importing.importers.xlsx import XLSXImporter
from services.importing.excs import InvalidImportFileExtension
from utils.logs.loggers.separator import SeparatorLogger


class ImporterFactory(object):
    """Importer factory class."""

    __importer_types: Dict[Tuple[str, ...], Type[BaseImporter]] = {
        ("xlsx", "xlsm", "xltx", "xltm"): XLSXImporter,
    }

    @classmethod
    def __file_extension(cls, filepath: str) -> str:
        """Return file extension."""
        file_match = re.search(r".*\.(.*)?", filepath)
        return file_match.group(1)

    def __call__(self, filepath: str, separator_logger: SeparatorLogger) -> BaseImporter:
        """Return importer object depends on file extension."""
        file_extension: str = self.__file_extension(filepath)
        for extensions, class_importer in self.__importer_types.items():
            if file_extension in extensions:
                return class_importer(filepath, separator_logger)
        else:
            raise InvalidImportFileExtension(extension=file_extension)
