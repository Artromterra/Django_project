"""The module responsible for the django command import_data."""
from typing import List

from django.core.management.base import BaseCommand

from shop.tasks import import_data_from_files
from online_store.celery import app


class Command(BaseCommand):
    help = "Import data from files."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dir_with_import_files",
            type=str,
            required=True,
            help="The directory where the import files are stored."
        )
        parser.add_argument(
            "--success_dir",
            type=str,
            required=True,
            help="The directory where the files of successful imports will be stored."
        )
        parser.add_argument(
            "--failure_dir",
            type=str,
            required=True,
            help="The directory where the import files with errors will be stored."
        )
        parser.add_argument(
            "--import_filenames",
            type=List[str],
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
            "--emails",
            type=List[str],
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
        dir_with_import_files = options["dir_with_import_files"]
        success_dir = options["success_dir"]
        failure_dir = options["failure_dir"]
        import_filenames = options.get("import_filenames")
        emails = options.get("emails")

        import_data_from_files.apply_async(
            dir_with_import_files=dir_with_import_files,
            success_dir=success_dir,
            failure_dir=failure_dir,
            import_filenames=import_filenames,
            emails=emails,
        )
