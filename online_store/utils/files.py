
import os
from typing import List, Optional

from django.conf import settings


def get_import_files(import_dir: Optional[str] = None) -> List[str]:
    if not import_dir:
        import_dir = settings.DIR_WITH_IMPORT_FILES
    import_files = [
        filepath for filepath in os.listdir(import_dir)
        if os.path.isfile(filepath)
    ]
    return import_files
