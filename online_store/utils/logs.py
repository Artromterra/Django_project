"""The module responsible for working with logs."""
from typing import Optional, List, Set, Literal
from uuid import UUID
from logging import getLogger
from logging.handlers import MemoryHandler


def generate_unique_logger_name(parent_logger_name: Optional[str] = None) -> str:
    """Generate unique logger name for celery"""
    return f"{parent_logger_name}.{str(UUID())}"


def get_memory_handler_from_logger(logger_name: str) -> MemoryHandler:
    """Return MemoryHandler from logger with logger_name."""
    logger = getLogger(logger_name)
    for handler in logger.handlers:
        if isinstance(handler, MemoryHandler):
            return handler
    else:
        raise ValueError("Logger doesn't have MemoryHandler.")


def get_logs_with_levels_from_memory_handler(
    logger_name: str,
    levels: Set[Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]]
) -> List[str]:
    """Get logs with levels from MemoryHandler."""
    memory_handler: MemoryHandler = get_memory_handler_from_logger(logger_name)
    formatter = memory_handler.formatter
    logs = memory_handler.buffer
    return [
        formatter.format(log)
        for log in logs if log.levelname in levels
    ]


def save_logs_from_buffer_to_file(filepath: str, logger_name: str) -> None:
    """Save logs from MemoryHandler buffer to file."""
    logs: List[str] = get_logs_with_levels_from_memory_handler(
        logger_name=logger_name,
        levels={"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"},
    )

    with open(filepath, "w", encoding="utf-8") as logfile:
        logfile.write("\n".join(logs))
