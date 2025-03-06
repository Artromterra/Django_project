"""The module responsible for celery tasks."""
from typing import Optional, List
import os

from celery import shared_task

from services.importing.manager import ImportManager
from services.importing.importers.importer_factory import ImporterFactory
from services.importing.reporters.email_reporter import EmailReporter


@shared_task
def import_from_file(
        filepath: str,
        success_dir: str,
        failure_dir: str,
        emails: Optional[List[str]] = None
):
    """
    Import data from a file.

    :param filepath: Import file.
    :param success_dir: The directory where the files of successful imports will be stored.
    :param failure_dir: The directory where the import files with errors will be stored.
    :param emails: The email list where the import reports will be sent.
    If None or an empty list is passed,
    reports will be sent to the emails specified in the ADMIN_EMAILS in the .env file.
    """
    importer_factory = ImporterFactory()
    email_reporter = EmailReporter(emails)
    import_manager = ImportManager(
        import_file=filepath,
        importer_factory=importer_factory,
        reporter=email_reporter,
        success_dir=success_dir,
        failure_dir=failure_dir
    )

    import_manager.run_import()


@shared_task
def import_data_from_files(
        dir_with_import_files: str,
        success_dir: str,
        failure_dir: str,
        import_filenames: Optional[List[str]] = None,
        emails: Optional[List[str]] = None
):
    """
    Create tasks for importing data from files.

    If multiple import files are transferred, importing from each file will occur asynchronously.

    :param dir_with_import_files: The directory where the import files are stored.
    :param success_dir: The directory where the files of successful imports will be stored.
    :param failure_dir: The directory where the import files with errors will be stored.
    :param import_filenames: The names of the import files.
    If None or an empty list is passed,
    data will be imported from all files in the directory dir_with_import_files.
    If a non-empty list is passed, data will be imported only from these files.
    The names of the import files will be combined with the directory path.

    :param emails: The email list where the import reports will be sent.
    If None or an empty list is passed,
    reports will be sent to the emails specified in the ADMIN_EMAILS in the .env file.
    """
    if not import_filenames:
        filenames: List[str] = os.listdir(dir_with_import_files)
        filepaths: List[str] = [
            os.path.join(dir_with_import_files, filename)
            for filename in filenames
        ]
    else:
        filepaths: List[str] = [
            os.path.join(dir_with_import_files, filename)
            for filename in import_filenames
        ]
    for filepath in filepaths:
        import_from_file.apply_async(
            filepath=filepath,
            success_dir=success_dir,
            failure_dir=failure_dir,
            emails=emails
        )
