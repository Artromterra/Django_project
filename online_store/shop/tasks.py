"""The module responsible for Celery tasks related to the django app."""

from typing import Dict, Any, List, Set
from logging import getLogger
import shutil
import os

from celery import shared_task, chain, group

from utils.xlsx import xlsx_reader

from .models.product import Product

logger = getLogger("celery")


@shared_task
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


@shared_task
def import_was_successful(import_results: List[bool]) -> bool:
    """Return True if import was successful, else False."""
    import_results_set: Set[bool] = set(import_results)
    if import_results_set is {True}:
        logger.info("Import was successful.")
        return True

    logger.warning("Import was with failures.")
    return False


@shared_task
def move_file(was_successful: bool, file_path: str, success_dir: str, failure_dir: str) -> None:
    """
    Transfer the file depending on the success of the import.

    :param was_successful: True, if all rows from xlsx file were converted to Product models.
    :param file_path: Import file path.
    :param success_dir: The directory to move the import file to in case of success.
    :param failure_dir: The directory to move the import file to in case of failure.
    """
    try:
        _, filename = os.path.split(file_path)

        if was_successful:
            target_path: str = os.path.join(success_dir, filename)
        else:
            target_path = os.path.join(failure_dir, filename)

        shutil.move(file_path, target_path)
    except Exception as exc:
        logger.exception(exc)
    else:
        logger.info("Move import file to %s", target_path)


@shared_task
def report_about_import() -> None:
    pass


@shared_task
def import_products(file_path: str, success_dir: str, failure_dir: str) -> bool:
    group_from_dict_to_model = group(
        product_from_dict.s(product_dict)
        for product_dict in xlsx_reader(file_path)
    )

    group_move_and_send_email = group(
        move_file.s(file_path, success_dir, failure_dir),
        report_about_import.s(),
    )

    chain(
        group_from_dict_to_model,
        import_was_successful.s(),
        group_move_and_send_email
    ).apply_async()
