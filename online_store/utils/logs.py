"""The module responsible for working with log files."""

from typing import List, Tuple


def get_logs_with_levels_from_file(levels: Tuple[str, ...], log_file: str) -> List[str]:
    """
    Return the list of logs with the specified levels.

    :param levels: Tuple of levels logs.
    :param log_file: Log file path.
    :return: List of logs with these levels.
    """
    logs: List[str] = list()
    with open(log_file, "r", encoding="utf-8") as file:
        for line in file:
            for level in levels:
                if level in line:
                    logs.append(line)
                    break

    return logs
