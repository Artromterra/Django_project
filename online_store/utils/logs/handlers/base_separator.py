from abc import ABC, abstractmethod
from logging import Handler
from typing import Optional, Set, Literal, List


class BaseSeparateHandler(Handler, ABC):
    """A basic handler for separate logging in different threads or processes."""

    @abstractmethod
    def get_logs(
            self,
            unique_id: str,
            levels: Optional[Set[Literal[
                "DEBUG",
                "INFO",
                "WARNING",
                "ERROR",
                "CRITICAL"
            ]]] = None
    ) -> List[str]:
        """
        Get logs with levels.

        If levels is None, return all logs.
        """
        pass

    @abstractmethod
    def extract(self, unique_id: str) -> List[str]:
        """Extract all logs from redis."""
        pass

    @abstractmethod
    def save(
            self,
            unique_id: str,
            filename: str,
            mode: Literal["w", "a"] = "w",
            extract: bool = True
    ) -> None:
        """
        Save logs into file.

        If extract == True, logs will be deleted from redis.
        """
        pass
