"""The module responsible for Celery tasks related to the django app."""

from typing import Dict, Any, List, Set
from logging import getLogger

from celery import shared_task, chain, group

from utils.xlsx import xlsx_reader
from utils.email import send_email, compile_report
from utils.files import move_file_depends_on_import_result

from .models.product import Product

logger = getLogger("celery")


def product_from_dict(product_data: Dict[str, Any]) -> bool:
    """
    Create the product from dict.

    If import was successful return True, else False.
    """
    try:
        Product.objects.update_or_create(**product_data)
    except Exception as exc:
        logger.exception(exc)
        return False
    else:
        return True


def import_was_successful(import_results: List[bool]) -> bool:
    """Return True if import was successful, else False."""
    import_results_set: Set[bool] = set(import_results)
    if import_results_set is {True}:
        logger.info("Import was successful.")
        return True

    logger.warning("Import was with failures.")
    return False


def move_file(was_successful: bool, file_path: str, success_dir: str, failure_dir: str) -> bool:
    """
    Transfer the file depending on the success of the import.

    :param was_successful: True, if all rows from xlsx file were converted to Product models.
    :param file_path: Import file path.
    :param success_dir: The directory to move the import file to in case of success.
    :param failure_dir: The directory to move the import file to in case of failure.
    :return: True, if moving was successful, else False
    """
    try:
        target_path: str = move_file_depends_on_import_result(
            was_successful, file_path, success_dir, failure_dir
        )
    except Exception as exc:
        logger.exception(exc)
        return False
    else:
        logger.info("Import file %s was moved.", target_path)
        return True


def report_about_import(
        was_successful: bool, admin_email: str, file_path: str, log_file_path: str
) -> bool:
    """
    Report about import process result.

    :param was_successful: True, if import was successful, else False.
    :param admin_email: Email address where to send the message with the report.
    :param file_path: Import file path.
    :param log_file_path: File path with logs about import.
    """
    email_subject, email_text = compile_report(
        was_successful, file_path, log_file_path
    )

    try:
        send_email(admin_email, email_subject, email_text)
    except Exception as exc:
        logger.error(exc)
        return False
    else:
        logger.info("Report about import has been sent.")
        return True


@shared_task
def import_products(file_path: str, success_dir: str, failure_dir: str) -> Dict[str, bool]:
    """
    Import products from Excel file.

    A task consists of a chain of tasks.
    The first task in the chain is a group of tasks for creating models from Excel rows.
    The next task is to verify the success of the import.
    If all lines were imported without errors, the task returns True.
    Further along the chain, a group of tasks is performed,
    consisting of 2 tasks - sending the report and moving the import file.

    :param file_path: Import file path.
    :param success_dir: The directory where you want to move the files of the successful import.
    :param failure_dir: The directory where you want to move the import files with errors.
    :return: Dictionary in the form of
    {"importing": True, "moving_file": True, "reporting": True}
    """
    # 1 link - first group
    group_from_dict_to_model = group(
        shared_task(product_from_dict).s(product_dict)
        for product_dict in xlsx_reader(file_path)
    )

    # 2 link - task
    group_move_and_send_email = group(
        shared_task(move_file).s(file_path, success_dir, failure_dir),
        shared_task(report_about_import).s(),
    )

    # 3 link - second group
    import_process = chain(
        group_from_dict_to_model,
        shared_task(import_was_successful).s(),
        group_move_and_send_email
    ).apply_async()
    moving_file, reporting = import_process.get()

    return {
        "importing": import_process.parent.get(),
        "moving_file": moving_file,
        "reporting": reporting
    }
