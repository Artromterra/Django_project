
from logging import getLogger

from online_store.celery import app

logger = getLogger("main.utils.celery")


def are_there_any_active_importing_tasks():
    """Return True, if there are active importing tasks."""
    inspector = app.control.inspect()
    active_tasks = inspector.active()
    if not active_tasks:
        logger.debug("There are no active tasks.")
        return False
    for _, tasks in active_tasks.items():
        for task in tasks:
            if task["name"] == "shop.tasks.import_data_from_files":
                logger.warning("There are at least one active importing task.")
                return True
    logger.debug("There ara no active importing tasks.")
    return False


def are_there_any_reserved_importing_tasks():
    """Return True, if there are reserved importing tasks."""
    inspector = app.control.inspect()
    reserved_tasks = inspector.reserved()
    if not reserved_tasks:
        logger.debug("There are no reserved tasks.")
        return False
    for _, tasks in reserved_tasks.items():
        for task in tasks:
            if task["name"] == "shop.tasks.import_data_from_files":
                logger.warning("There are at least one reserved importing tasks.")
                return True
    logger.debug("There are no reserved importing tasks.")
    return False