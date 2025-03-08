"""The module responsible for the django command import_data."""

import os

from django.core.management.base import BaseCommand
from django.conf import settings

from shop.tasks import import_data_from_files
from online_store.celery import app


class Command(BaseCommand):
    help = "Import data from files."

    def add_arguments(self, parser):
        parser.add_argument(
            "-i", "--imports-dir",
            type=str,
            required=False,
            help="The directory where the import files are stored."
        )
        parser.add_argument(
            "-s", "--success-dir",
            type=str,
            required=False,
            help="The directory where the files of successful imports will be stored."
        )
        parser.add_argument(
            "-f", "--failure-dir",
            type=str,
            required=False,
            help="The directory where the import files with errors will be stored."
        )
        parser.add_argument(
            "--filenames",
            nargs="+",
            type=str,
            required=False,
            help="""
            The names of the import files.
            If None or an empty list is passed,
            data will be imported from all files in the directory dir_with_import_files.
            If a non-empty list is passed, data will be imported only from these files.
            The names of the import files will be combined with the directory path.
            """
        )
        parser.add_argument(
            "-e", "--emails",
            nargs="+",
            type=str,
            required=False,
            help="""
            The email list where the import reports will be sent.
            If None or an empty list is passed,
            reports will be sent to the emails specified in the ADMIN_EMAILS in the .env file.
            """
        )

    @classmethod
    def __are_there_any_active_importing_tasks(cls):
        """Return True, if there are active importing tasks."""
        inspector = app.control.inspect()
        active_tasks = inspector.active()
        if not active_tasks:
            return False
        for _, tasks in active_tasks.items():
            for task in tasks:
                if task["name"] == "shop.tasks.import_data_from_files":
                    return True
        return False

    @classmethod
    def __are_there_any_reserved_importing_tasks(cls):
        """Return True, if there are reserved importing tasks."""
        inspector = app.control.inspect()
        reserved_tasks = inspector.reserved()
        if not reserved_tasks:
            return False
        for _, tasks in reserved_tasks.items():
            for task in tasks:
                if task["name"] == "shop.tasks.import_data_from_files":
                    return True
        return False

    @classmethod
    def __create_dir_if_not_exists(cls, dir_: str) -> None:
        if not os.path.exists(dir_):
            os.makedirs(dir_)


    def handle(self, *args, **options):
        # Check that celery is not performing any tasks.
        if (self.__are_there_any_reserved_importing_tasks() or
                self.__are_there_any_reserved_importing_tasks()
        ):
            self.stderr.write(
                "There are currently reserved or active data import tasks. "
                "Please wait and try again."
            )
            return

        # Run import data from files task.
        dir_with_import_files = options.get("imports-dir", settings.DIR_WITH_IMPORT_FILES)
        self.stdout.write(f"Dir with import files: {dir_with_import_files}\n")

        success_dir = options.get("success-dir", settings.DIR_WITH_SUCCESSFUL_IMPORTS)
        self.__create_dir_if_not_exists(success_dir)
        self.stdout.write(f"Dir with successful import files: {success_dir}\n")

        failure_dir = options.get("failure-dir", settings.DIR_WITH_IMPORTS_WITH_ERRORS)
        self.__create_dir_if_not_exists(failure_dir)
        self.stdout.write(f"Dir with import files with errors: {failure_dir}\n")

        import_filenames = options.get("filenames")
        self.stdout.write(f"Import files: {import_filenames}\n")

        emails = options.get("emails")
        self.stdout.write(f"Emails: {emails}\n")

        import_data_from_files.apply_async(
            args=[dir_with_import_files, success_dir, failure_dir],
            import_filenames=import_filenames,
            emails=emails,
        )
