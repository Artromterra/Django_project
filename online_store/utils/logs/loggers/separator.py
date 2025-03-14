
from uuid import uuid4
from typing import TypeVar, Type
from logging import getLogger

from ..adapters.separator import SeparatorAdapter
from ..handlers.base_separator import BaseSeparateHandler

H = TypeVar("H", bound=BaseSeparateHandler)


class SeparatorLogger(object):

    def __init__(
            self,
            logger_name: str,
            separator_handler: H,
    ):
        self.__unique_id: str = self.__generate_unique_id()
        self.__logger = getLogger(logger_name)
        self.__separator_handler = separator_handler

    @classmethod
    def __generate_unique_id(cls) -> str:
        return str(uuid4())

    @property
    def unique_id(self) -> str:
        """Get logging unique id."""
        return self.__unique_id

    @property
    def handler(self) -> H:
        return self.__separator_handler

    @property
    def adapter(self) -> SeparatorAdapter:
        handler_type = type(self.__separator_handler)
        for handler in self.__logger.handlers:
            if isinstance(handler, handler_type):
                break
        else:
            self.__logger.addHandler(self.__separator_handler)

        return SeparatorAdapter(self.__logger, dict(unique_id=self.__unique_id))
