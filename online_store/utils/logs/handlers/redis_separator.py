from typing import Optional, Dict, Any, Literal, Set, List
import json

from redis import Redis

from .base_separator import BaseSeparateHandler


class RedisHandler(BaseSeparateHandler):
    """
    The handler that stores logs in Redis.

    Logs are stored in lists,
    lists are stored under keys, which are logger names (to separate logs from individual loggers).
    Logs are stored as dictionaries {"level": ..., "log": ...}, serialized in json strings.
    """

    def __init__(
            self,
            *args,
            redis_client: Optional[Redis] = None,
            redis_kwargs: Optional[Dict[str, Any]] = None,
            **kwargs
    ):
        """
        Init handler.

        :param redis_client: Initialized Redis client.
        :param redis_kwargs: Parameters for initializing the Redis client.
        :raise ValueError: If redis_client is None and redis_kwargs is None.
        """
        super().__init__(*args, **kwargs)

        if not redis_client and not redis_kwargs:
            raise ValueError(
                "Pass either the initialized Redis client"
                " or the parameters for initialization "
                "(redis_client and redis_kwargs cannot both be None)"
            )

        if not redis_client:
            self.__redis = Redis(**redis_kwargs)
        else:
            self.__redis = redis_client

    def emit(self, record):
        unique_id: str = record.unique_id
        level: str = record.levelname
        log: str = self.format(record)
        self.__redis.rpush(unique_id, json.dumps({"level": level, "log": log}))

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
        if not levels:
            return [
                json.loads(log_json)["log"]
                for log_json in self.__redis.lrange(unique_id, 0, -1)
            ]
        else:
            return [
                json.loads(log_json)["log"]
                for log_json in self.__redis.lrange(unique_id, 0, -1)
                if json.loads(log_json)["level"] in levels
            ]

    def extract(self, unique_id: str) -> List[str]:
        """Extract all logs from redis."""
        logs: List[str] = self.get_logs(unique_id)
        self.__redis.delete(unique_id)
        return logs

    def save(self, unique_id: str, filename: str, mode: Literal["w", "a"] = "w", extract: bool = True):
        """
        Save logs into file.

        If extract == True, logs will be deleted from redis.
        """
        with open(filename, mode, encoding="utf-8") as logfile:
            if extract:
                logs = self.extract(unique_id)
            else:
                logs = self.get_logs(unique_id)

            logfile.write("\n".join(logs))
