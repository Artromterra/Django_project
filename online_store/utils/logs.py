"""The module responsible for working with log files."""

from typing import List, Tuple
import re


def get_logs_with_levels_from_file(levels: Tuple[str, ...], log_file: str) -> List[str]:
    """
    Return the list of logs with the specified levels.

    :param levels: Tuple of levels logs.
    :param log_file: Log file path.
    :return: List of logs with these levels.
    """
    logs: List[str] = list()
    with open(log_file, "r", encoding="utf-8") as file:
        suitable_log: bool = False

        for line in file:
            match = re.match(r"\[(.*?)].*", line)

            if match:
                # if line starts with [<LOGLEVEL>]
                if match.group(1) in levels:
                    suitable_log = True
                    logs.append(line)
                else:
                    suitable_log = False
            elif suitable_log:
                # if line doesn't start with [<LOGLEVEL>]
                logs[-1] += "\n" + line

    return logs
